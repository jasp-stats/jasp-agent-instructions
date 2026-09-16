#!/usr/bin/env python3
"""Consult a senior-engineer advisor about a hard problem.

Spawns a separate, hooks-disabled `claude -p` session running a stronger model
(Fable 5.1 at extra effort) with read-only access to this repository, so the
advisor can read the actual code rather than advise blind.

Usage:
    python .claude/skills/advisor/ask-advisor.py <question-file>
    ... or pipe the question on stdin.

The question file should state the problem, what has already been tried and
ruled out, and the specific decision or blocker at hand. Write it anywhere outside the tracked tree, e.g. a scratch path.

Exits non-zero and prints a diagnostic if the advisor cannot be reached, so a
failed consult is never mistaken for advice.
"""
import datetime
import os
import subprocess
import sys
import time

MODEL = "claude-fable-5-1"
EFFORT = "xhigh"
TIMEOUT_S = 900              # 15 minutes: a hard question deserves the wait

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
LOG_PATH = os.path.join(REPO_ROOT, ".claude", "logs", "advisor.log")
ADVICE_DIR = os.path.join(REPO_ROOT, ".claude", "logs", "advisor")

# Advice routinely contains arrows and other non-cp1252 characters; a Windows
# console would otherwise kill the process after the consult has been paid for.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

FRAMING = """You are a senior engineer, consulted by a capable colleague who is
already deep in this problem and is stuck. Treat this as a focused design and
debugging review, not a tutorial.

You have read-only access to the repository in the working directory. Read
whatever files you need before answering. This is a JASP module: a QML front
end, an R backend, and jaspResults-driven output. The conventions in
.claude/CLAUDE.md and the rule files under .claude/rules/ apply - in particular
the module architecture, dependency and state-management rules, which explain
why code that looks correct in isolation still misbehaves in the reactive loop.
Statistical and reactive behaviour matter more than surface tidiness.

Answer with:
1. Your read of what is actually going on, naming the specific code or maths you
   based it on.
2. The concrete next step you would take, specific enough to act on.
3. Anything the colleague seems to have assumed that you think is wrong.

You have up to fifteen minutes of wall clock time, and nobody is waiting on a
fast answer - a consult is only requested for problems that are already stuck.
Spend that budget: read the code that actually matters, check your reading
against more than one file, and measure or count something concrete rather than
reasoning from the shape of the question. A specific answer grounded in what you
read is worth far more than a quick one.

Be direct. If the whole approach is misconceived, say so plainly and say what
you would do instead. If the question is underspecified, say exactly what
further information you need rather than guessing. If you are uncertain, say so
and give your best judgement with the reasoning - do not hedge into vagueness.

The colleague's question follows.
------------------------------------------------------------------------------
"""


def log(outcome, started, detail=""):
    """Append one line recording the consult. Never raises."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write("%s  %-12s %4.0fs  %s\n"
                         % (stamp, outcome, time.time() - started, detail))
    except Exception:
        pass


def main(argv):
    started = time.time()

    if len(argv) > 1:
        path = argv[1]
        if not os.path.isfile(path):
            print("advisor: no such question file: %s" % path, file=sys.stderr)
            return 2
        with open(path, encoding="utf-8") as handle:
            question = handle.read()
    else:
        question = sys.stdin.read()

    question = question.strip()
    if not question:
        print("advisor: empty question", file=sys.stderr)
        return 2

    claude = __import__("shutil").which("claude")
    if not claude:
        print("advisor: the claude CLI is not on PATH", file=sys.stderr)
        log("no-cli", started)
        return 2

    try:
        result = subprocess.run(
            [claude, "-p",
             "--settings", '{"disableAllHooks":true}',
             "--model", MODEL,
             "--effort", EFFORT,
             "--allowedTools", "Read", "Grep", "Glob"],
            input=FRAMING + question,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=TIMEOUT_S,
            cwd=REPO_ROOT,
        )
    except subprocess.TimeoutExpired:
        print("advisor: timed out after %ss" % TIMEOUT_S, file=sys.stderr)
        log("timeout", started, "%ss cap" % TIMEOUT_S)
        return 2
    except Exception as exc:
        print("advisor: could not start: %r" % exc, file=sys.stderr)
        log("spawn-failed", started, repr(exc)[:120])
        return 2

    advice = (result.stdout or "").strip()
    if not advice:
        print("advisor: no advice returned (rc=%s) %s"
              % (result.returncode, (result.stderr or "")[:300]), file=sys.stderr)
        log("no-advice", started, "rc=%s" % result.returncode)
        return 2

    # Persist before printing: a consult costs minutes, and stdout can fail.
    saved = ""
    try:
        os.makedirs(ADVICE_DIR, exist_ok=True)
        saved = os.path.join(ADVICE_DIR, datetime.datetime.now().strftime(
            "%Y%m%d-%H%M%S.md"))
        with open(saved, "w", encoding="utf-8") as handle:
            handle.write("# Question\n\n%s\n\n# Advice\n\n%s\n"
                         % (question, advice))
    except Exception:
        saved = ""

    first_line = question.splitlines()[0][:120] if question.splitlines() else ""
    log("ok", started, first_line)
    print(advice)
    if saved:
        print("\n[advisor: question and advice saved to %s]"
              % os.path.relpath(saved, REPO_ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
