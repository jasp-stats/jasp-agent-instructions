---
name: advisor
description: Consult a senior-engineer advisor (a stronger model with read-only access to this repo) on a genuinely hard problem. Use when stuck after real attempts - a bug whose cause you cannot locate, a JASP reactive/state issue you cannot explain, a statistical result that will not reconcile, or a design choice with no clear winner. Not for routine lookups, QML/R syntax, API details, or anything not yet attempted.
---

# Advisor

Spawns a separate `claude -p` session running a stronger model (Fable 5.1, extra
effort) with read-only access to this repo. It reads the actual code before
answering, so it can disagree with your diagnosis on the evidence.

## When to call it

Like asking a senior colleague to look over your shoulder: after you understand
the problem, tried the obvious things, and are still stuck. Good reasons:

- a bug chased over several attempts without locating the cause;
- output that appears, vanishes or goes stale in the reactive loop and the
  `$dependOn` / `createJaspState` reasoning does not explain it;
- a statistical result you cannot reconcile against a reference implementation;
- a design choice (option contract, container structure, state granularity)
  where the trade-offs are real and you keep flipping;
- a failure where each fix reveals a different diagnosis - you likely have the
  wrong model of what is happening.

Do **not** call it for: QML or R syntax, jaspResults API details, anything in
the rule files you could read directly, routine choices you should just make, or
a problem you have not yet attempted. A consult costs minutes.

## How to ask

Answer quality tracks question quality. Write the question to a scratch file
outside the tracked tree, covering:

1. **Goal** - what the analysis is supposed to produce.
2. **Symptom** - exact error, wrong output, or the blocked decision. Paste real
   output, not a paraphrase.
3. **What you tried** and what each attempt ruled out. This stops the advisor
   repeating your work.
4. **Where to look** - files and functions, so it reads the right code first.
5. **The question** - state plainly what you want decided.

```bash
python .claude/skills/advisor/ask-advisor.py <question-file>
```

Advice prints to stdout; each consult appends to `.claude/logs/advisor.log` and
saves question plus advice under `.claude/logs/advisor/`. The script exits
non-zero and explains itself if the advisor cannot be reached, so a failed
consult is never mistaken for advice.

Requires the Claude CLI to be logged in (`claude -p` runs as a subprocess).

## What to do with the answer

Advice from a colleague who read the code, not a verdict. It cannot run
anything, so verify any claim about numerical or reactive behaviour before
acting on it. If you disagree after checking, say so and explain why.
