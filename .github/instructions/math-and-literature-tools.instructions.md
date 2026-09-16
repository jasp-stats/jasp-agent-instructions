---
applyTo: "**/R/*.R"
description: "StatsVault literature search, Wolfram/Mathematica, and the Python symbolic/arbitrary-precision stack"
---

# Math & Literature Tools

Machine-level tools for symbolic derivation, independent numerical validation, and
statistical literature. **Not provided by this repo** - they come from the
developer's machine and global MCP config. Check availability before relying on
one; if missing, say so rather than silently substituting.

## Literature: StatsVault (MCP)

Global MCP server. First stop for statistical literature.

| Tool | Use for |
|------|---------|
| `search_papers` | Known-item or targeted lookup |
| `discover_relevant_papers` | Broad recall, finding what you are missing |
| `find_canonical_citations` | Established references for a concept |
| `materialize_papers` | Copy sources locally before detailed reading |
| `get_project_workspace_status` | What is already selected and pending |

Pass the repo root as `project_root`. Sources land under `.StatsVault/`. Verify
equations and assumptions in the full source before implementing them.

## Symbolic algebra: Wolfram / Mathematica

Two routes, both verified on Wolfram 15.0.1:

- **MCP**: `WolframLanguageEvaluator` (also `WolframLanguageContext`,
  `SymbolDefinition`). Sessions persist - reuse the returned session id.
- **Console kernel**:
  ```bash
  '/c/Program Files/Wolfram Research/Wolfram/15.0/math.exe' -noinit -noprompt -run 'Print[2+2]; Exit[]'
  ```

## Numerics: Python math environment

Separate venv, independent of the JASP/R package set:

```bash
'/c/Users/fbart/.codex/math-tools/.venv/Scripts/python.exe' script.py
```

SymPy (exact algebra), mpmath (arbitrary precision references), python-flint
(FLINT/Arb rigorous ball arithmetic). Installation self-check:

```bash
'/c/Users/fbart/.codex/math-tools/.venv/Scripts/python.exe' -B '/c/Users/fbart/.codex/math-tools/verify.py'
```

Guide: `C:/Users/fbart/.codex/math-tools/README.md`.

## Use

Validate numerical work against analytic identities, an independent
implementation, or a checked source - not against another run of the same code.
Keep these as development aids; never make them module dependencies. Numerical
agreement is evidence, not proof: state the tolerance or Monte Carlo error you
judged against.
