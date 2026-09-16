#!/usr/bin/env python3
"""Independent completion auditor for Claude Code Stop hooks.

Projects the session transcript into a structured brief - the turn's
commitments, a complete tool ledger, and a detailed tail - and sends it to a
separate, hooks-disabled `claude -p` session, which blocks the stop if the turn
did not finish what was asked.

The brief matters more than its size. A raw byte window is mostly thinking
blocks, envelope duplication and tool-result JSON, and it truncates exactly the
commitments the audit exists to check - which are typically stated in the
*previous* turn's final message, or in a plan file the turn only reads. The
projection keeps every statement the assistant made (they are tiny), every tool
call it issued (so "no test was run" is a checkable finding), and drops the
thinking and envelope noise entirely.

Fails open on every error path: a broken or unreachable auditor must never wedge
the session. Runs on the re-stop, not the first stop, so it judges the turn as
it finally stands; a marker keyed on the turn anchor bounds it to one audit per
turn. Every invocation appends a line to .claude/logs/stop-audit.log, so silence
is never mistaken for a pass.

Requires the Claude CLI to be logged in.
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
import time

MODEL = "claude-sonnet-5"
TIMEOUT_S = 900              # 15 minutes: a thorough audit is worth the wait

# Soft target: elision removes routine calls, never evidence lines or errors,
# so a turn that is mostly checks stays above it. Measured worst case over a
# 36 MB session (568 calls in one turn) is ~34 KB of ledger, ~65 KB of brief.
LEDGER_CAP = 30_000
DETAIL_CALLS = 15            # trailing calls shown with input and result
DETAIL_INPUT = 400
DETAIL_RESULT = 500
PREV_TURNS = 2               # preceding turns kept for their commitments

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
LOG_PATH = os.path.join(REPO_ROOT, ".claude", "logs", "stop-audit.log")
STATE_DIR = os.path.join(REPO_ROOT, ".claude", "logs", "audit-state")

# Envelope and bookkeeping lines carry no conversation content.
SKIP_TYPES = frozenset((
    "attachment", "bridge-session", "queue-operation", "last-prompt",
    "custom-title", "atis-latch", "file-history-snapshot", "file-history-delta",
))
PLAN_FILE_RE = re.compile(r"\.work/tasks/[\w\-.]+\.md")
# Evidence for "tests actually ran" must survive ledger elision wherever it sits.
KEEP_RE = re.compile(r"test|check|verif|commit|agent-r|R CMD|pytest|snapshot",
                     re.IGNORECASE)
HOOK_FEEDBACK_PREFIX = "Stop hook feedback:"
SLASH_COMMAND_PREFIXES = ("<command-name>", "<local-command-stdout>")

PROMPT = """You are an independent completion auditor for a Claude Code turn.

What follows is a structured brief projected from the session transcript, in
labelled sections:

- TASK: the user message that started the turn being audited.
- PRECEDING TURNS: the previous turns' user messages and final assistant
  messages. Commitments are often made here rather than in this turn - a plan or
  numbered list promised last turn is still owed.
- HOOK FEEDBACK DURING THIS TURN: checklists the harness fed back mid-turn. Each
  is a commitment the assistant accepted.
- PLAN FILES REFERENCED: paths the turn opened. If the task refers to a plan,
  Read these yourself to recover the item list - you have Read, Grep and Glob.
- ASSISTANT STATEMENTS: every message the assistant wrote during the turn, in
  order, complete and untruncated.
- TOOL LEDGER: the COMPLETE list of tool calls the turn made, one per line, with
  result size and first result line. Because it is complete, the absence of a
  call is evidence: if no test or verification command appears, none was run,
  whatever the assistant claims.
- RECENT CALLS IN DETAIL: the last calls with their inputs and results.
- FINAL MESSAGE: the assistant's closing message, complete.

Work out what was asked and every item the assistant committed to, across the
task, the preceding turns, the hook feedback and its own statements. Then judge
from the ledger and results whether each was carried out.

Reply with exactly PASS on a single line if all of the following hold.
Otherwise reply BLOCK followed by a short numbered list naming what is missing:

(a) every item the assistant committed to was done, or is named in the final
    message together with a concrete blocker;
(b) the assistant did not give session length, elapsed effort, cost, token
    budget, remaining scope size or multi-day effort estimates as a reason to
    stop - those are never valid reasons;
(c) every claim that tests, checks or verification passed is backed by a call in
    the ledger showing the actual run and its real output;
(d) the final message is specific enough for the maintainer to verify what was
    done without rereading the conversation.

Judge only the assistant's work, never the user's. Legitimate reasons to finish
with work outstanding are only: an unresolved maintainer decision, a hard
failure, or a missing permission. Be strict, but do not invent problems and do
not block on style or tone. Output only PASS, or BLOCK and the list.

==============================================================================
"""

REASON_PREFIX = (
    "An independent audit of this turn (a separate model reading the raw "
    "transcript, not your own summary) did not pass: "
)


def log(outcome, started=None, detail=""):
    """Append one line recording what this invocation did. Never raises."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        elapsed = "" if started is None else " %.0fs" % (time.time() - started)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write("%s  %-14s%s  %s\n" % (stamp, outcome, elapsed, detail))
    except Exception:
        pass


# --------------------------------------------------------------------------
# transcript projection
# --------------------------------------------------------------------------

def load_entries(path):
    """Parse the transcript into conversation entries, newest last."""
    entries = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.startswith("{"):
                continue
            # Cheap prefilter: most lines are envelope noise.
            if '"type":"user"' not in line and '"type":"assistant"' not in line:
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") in SKIP_TYPES or entry.get("isSidechain"):
                continue
            if entry.get("type") in ("user", "assistant"):
                entries.append(entry)
    return entries


def parts(entry):
    """Content parts of an entry, always as a list of dicts."""
    content = entry.get("message", {}).get("content")
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [p for p in content if isinstance(p, dict)]
    return []


def text_of(entry):
    """Concatenated text parts of an entry."""
    return "\n".join(p.get("text", "") for p in parts(entry)
                     if p.get("type") == "text").strip()


def result_text(part):
    """Text of a tool_result part, whose content may be a string or a list."""
    content = part.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(p.get("text", "") for p in content
                         if isinstance(p, dict) and p.get("type") == "text")
    return ""


def is_tool_result(entry):
    return any(p.get("type") == "tool_result" for p in parts(entry))


def is_real_user(entry):
    """A message actually typed by the user: a turn boundary."""
    return (entry.get("type") == "user"
            and not entry.get("isMeta")
            and not is_tool_result(entry))


def is_hook_feedback(entry):
    return (entry.get("type") == "user" and entry.get("isMeta")
            and text_of(entry).startswith(HOOK_FEEDBACK_PREFIX))


def clip(text, head, tail=0):
    """Truncate text, keeping the head and optionally the tail."""
    text = text or ""
    if len(text) <= head + tail + 60:
        return text
    if tail:
        return "%s\n    ...[%d chars elided]...\n%s" % (
            text[:head], len(text) - head - tail, text[-tail:])
    return "%s ...[%d more chars]" % (text[:head], len(text) - head)


def first_line(text):
    for line in (text or "").splitlines():
        if line.strip():
            return line.strip()
    return ""


def key_argument(name, tool_input):
    """The part of a tool call that says what it actually did."""
    if not isinstance(tool_input, dict):
        return ""
    if name in ("Bash", "PowerShell"):
        return "[%s] %s" % (tool_input.get("description", ""),
                            " ".join((tool_input.get("command") or "").split())[:80])
    for field in ("file_path", "path", "pattern", "url", "prompt",
                  "description", "skill"):
        if tool_input.get(field):
            return " ".join(str(tool_input[field]).split())[:90]
    return ""


def turn_boundaries(entries):
    """Indices of real user messages, skipping slash-command echo pairs."""
    bounds = []
    for i, entry in enumerate(entries):
        if not is_real_user(entry):
            continue
        if text_of(entry).startswith(SLASH_COMMAND_PREFIXES):
            continue
        bounds.append(i)
    return bounds


def turn_anchor_uuid(entries):
    """uuid of the current turn's opening user message, or None."""
    bounds = turn_boundaries(entries)
    return entries[bounds[-1]].get("uuid") if bounds else None


def collect_calls(turn):
    """Tool calls in order, each paired with its result."""
    results = {}
    for entry in turn:
        for part in parts(entry):
            if part.get("type") == "tool_result":
                results[part.get("tool_use_id")] = part
    calls = []
    for entry in turn:
        if entry.get("type") != "assistant":
            continue
        for part in parts(entry):
            if part.get("type") != "tool_use":
                continue
            result = results.get(part.get("id"), {})
            body = result_text(result)
            calls.append({
                "name": part.get("name", "?"),
                "input": part.get("input", {}),
                "result": body,
                "error": bool(result.get("is_error")),
                "missing": part.get("id") not in results,
            })
    return calls


def build_ledger(calls):
    """One line per call; elide the middle but never drop evidence lines."""
    lines = []
    for index, call in enumerate(calls, 1):
        status = "ERROR" if call["error"] else (
            "no-result-yet" if call["missing"] else "%dB" % len(call["result"]))
        argument = key_argument(call["name"], call["input"])
        # Evidence lines keep a fuller result excerpt; routine ones are terse.
        evidence = call["error"] or KEEP_RE.search("%s %s" % (call["name"], argument))
        lines.append("#%03d %-11s %-72s -> %-12s %s" % (
            index, call["name"], argument[:72], status,
            first_line(call["result"])[:100 if evidence else 60]))

    total = sum(len(line) + 1 for line in lines)
    if total <= LEDGER_CAP:
        return "\n".join(lines)

    # Keep the head, the tail, and every line that is evidence of a check.
    keep = set(range(0, 20)) | set(range(len(lines) - 40, len(lines)))
    for i, line in enumerate(lines):
        if "ERROR" in line or KEEP_RE.search(line):
            keep.add(i)
    kept, elided = [], 0
    for i, line in enumerate(lines):
        if i in keep:
            if elided:
                kept.append("     ... %d routine calls elided ..." % elided)
                elided = 0
            kept.append(line)
        else:
            elided += 1
    if elided:
        kept.append("     ... %d routine calls elided ..." % elided)
    return "\n".join(kept)


def build_brief(entries, payload):
    """Project the transcript into the labelled brief the auditor reads."""
    bounds = turn_boundaries(entries)
    if not bounds:
        return ""
    turn = entries[bounds[-1]:]
    out = []

    out.append("## TASK\n\n%s" % text_of(entries[bounds[-1]]))

    previous = bounds[-(PREV_TURNS + 1):-1]
    if previous:
        out.append("## PRECEDING TURNS (commitments made before this turn)")
        for pos, start in enumerate(previous):
            end = bounds[bounds.index(start) + 1]
            finals = [text_of(e) for e in entries[start:end]
                      if e.get("type") == "assistant" and text_of(e)]
            out.append("### user asked\n\n%s\n\n### assistant concluded\n\n%s"
                       % (clip(text_of(entries[start]), 2000),
                          finals[-1] if finals else "(no closing message)"))

    feedback = [text_of(e) for e in turn if is_hook_feedback(e)]
    if feedback:
        out.append("## HOOK FEEDBACK DURING THIS TURN (accepted commitments)"
                   "\n\n%s" % "\n\n---\n\n".join(feedback))

    plans = []
    for entry in turn:
        for part in parts(entry):
            if part.get("type") == "tool_use":
                for hit in PLAN_FILE_RE.findall(json.dumps(part.get("input", {}))):
                    if hit not in plans:
                        plans.append(hit)
    if plans:
        out.append("## PLAN FILES REFERENCED\n\n%s\n\nRead these if the task "
                   "refers to a plan; their item lists are commitments."
                   % "\n".join(plans))

    calls = collect_calls(turn)
    statements = []
    seen = 0
    for entry in turn:
        if entry.get("type") != "assistant":
            continue
        for part in parts(entry):
            if part.get("type") == "tool_use":
                seen += 1
            elif part.get("type") == "text" and part.get("text", "").strip():
                statements.append("--- after tool call #%d ---\n%s"
                                  % (seen, part["text"].strip()))
    if statements:
        out.append("## ASSISTANT STATEMENTS DURING THIS TURN\n\n%s"
                   % "\n\n".join(statements))

    out.append("## TOOL LEDGER - COMPLETE LIST OF %d CALLS THIS TURN\n\n%s"
               % (len(calls), build_ledger(calls) or "(no tool calls)"))

    if calls:
        detail = []
        for index, call in enumerate(calls[-DETAIL_CALLS:],
                                     max(1, len(calls) - DETAIL_CALLS + 1)):
            detail.append("#%03d %s\ninput: %s\nresult%s: %s" % (
                index, call["name"],
                clip(" ".join(json.dumps(call["input"]).split()), DETAIL_INPUT),
                " (ERROR)" if call["error"] else "",
                clip(call["result"], DETAIL_RESULT // 2, DETAIL_RESULT // 2)))
        out.append("## RECENT CALLS IN DETAIL\n\n%s" % "\n\n".join(detail))

    final = payload.get("last_assistant_message") or ""
    if final:
        out.append("## FINAL MESSAGE\n\n%s" % final)

    return "\n\n".join(out)


# --------------------------------------------------------------------------
# one audit per turn
# --------------------------------------------------------------------------

def already_audited(session_id, anchor):
    if not session_id or not anchor:
        return False
    try:
        with open(os.path.join(STATE_DIR, "%s.anchor" % session_id),
                  encoding="utf-8") as handle:
            return handle.read().strip() == anchor
    except OSError:
        return False


def record_audited(session_id, anchor):
    if not session_id or not anchor:
        return
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(os.path.join(STATE_DIR, "%s.anchor" % session_id), "w",
                  encoding="utf-8") as handle:
            handle.write(anchor)
    except Exception:
        pass


def main():
    started = time.time()
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        log("bad-payload", started, repr(exc)[:120])
        return 0

    transcript = payload.get("transcript_path")
    if not transcript or not os.path.isfile(transcript):
        log("no-transcript", started, str(transcript)[:120])
        return 0

    # Audit the turn as it finally stands. The self-check blocks the first stop,
    # so anything done in response to it exists only by the re-stop.
    if not payload.get("stop_hook_active"):
        log("skip-first-stop")
        return 0

    try:
        entries = load_entries(transcript)
    except OSError as exc:
        log("unreadable", started, repr(exc)[:120])
        return 0

    anchor = turn_anchor_uuid(entries)
    session_id = payload.get("session_id")
    if already_audited(session_id, anchor):
        log("skip-audited")
        return 0

    claude = shutil.which("claude")
    if not claude:
        log("no-claude-cli", started)
        return 0

    try:
        brief = build_brief(entries, payload)
    except Exception as exc:
        log("brief-failed", started, repr(exc)[:120])
        return 0
    if not brief.strip():
        log("empty-brief", started)
        return 0

    try:
        result = subprocess.run(
            [claude, "-p",
             "--settings", '{"disableAllHooks":true}',
             "--model", MODEL,
             "--allowedTools", "Read", "Grep", "Glob"],
            input=PROMPT + brief,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_S,
            cwd=REPO_ROOT,
        )
    except subprocess.TimeoutExpired:
        log("timeout", started, "%ss cap" % TIMEOUT_S)
        return 0
    except Exception as exc:
        log("spawn-failed", started, repr(exc)[:120])
        return 0

    verdict = (result.stdout or "").strip()
    if not verdict:
        log("no-verdict", started,
            "rc=%s %s" % (result.returncode, (result.stderr or "")[:100]))
        return 0

    record_audited(session_id, anchor)

    head = verdict.upper()
    if head.startswith("PASS"):
        log("PASS", started, "brief %dKB" % (len(brief) // 1024))
        return 0
    if "BLOCK" not in head:
        log("unparsed", started, verdict[:120])
        return 0

    log("BLOCK", started, verdict.replace("\n", " ")[:200])
    print(json.dumps({"decision": "block", "reason": REASON_PREFIX + verdict}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
