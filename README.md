# JASP Agent Instructions

Common resource for AI workflows across JASP R modules.

## Purpose

This repository contains instruction files that guide AI coding assistants (GitHub Copilot, Claude Code, OpenAI Codex CLI) when working with JASP modules. These instructions ensure consistent development practices, coding standards, and best practices across all JASP R packages when using AI coding assistants.

Three platforms are supported, each with its own configuration directory:

| Platform | Main instructions | Rules directory | Config |
| -------- | ----------------- | --------------- | ------ |
| **Claude Code** | `.claude/CLAUDE.md` | `.claude/rules/` | `.claude/settings.local.json` |
| **OpenAI Codex CLI** | `AGENTS.md` | `.codex/rules/` | `.codex/config.toml` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/instructions/` | `.vscode/settings.json` |

## Repository Structure

```text
repo/
├── AGENTS.md                           # Codex CLI main instructions
├── MIGRATION.md                        # Cross-platform sync guide
│
├── .claude/
│   ├── CLAUDE.md                       # Claude Code main instructions
│   ├── r-preamble.R                    # Per-call R bootstrap (all platforms)
│   ├── session_startup.R               # Shared R bootstrap
│   ├── settings.local.json             # Claude config incl. Stop hooks (committed)
│   ├── hooks/
│   │   ├── block-test-edits.js         # Claude PreToolUse safety hook
│   │   └── stop-audit.py               # Stop hook: independent turn audit
│   ├── rules/                          # 12 rule files (canonical source of truth)
│   │   ├── r-instructions.md
│   │   ├── qml-instructions.md
│   │   ├── testing-instructions.md
│   │   ├── git-workflow.md
│   │   ├── translation-instructions.md
│   │   ├── jasp-module-architecture.md
│   │   ├── jasp-dependency-management.md
│   │   ├── jasp-state-management.md
│   │   ├── jasp-tables.md
│   │   ├── jasp-plots.md
│   │   ├── jasp-containers-and-errors.md
│   │   └── jasp-output-structure.md
│   └── skills/
│       ├── fix-debug-analysis/
│       │   └── SKILL.md                # Claude debugging skill
│       └── advisor/
│           └── SKILL.md                # Consult a stronger model when stuck
│
├── .codex/
│   ├── config.toml                     # Codex sandbox, approval, reasoning
│   └── rules/                          # 12 rule files (no frontmatter) + Starlark policy
│       ├── default.rules               # Execution policy (forbid force-push, etc.)
│       └── *.md                        # Same rule body as .claude/rules/
│
├── .agents/
│   └── skills/
│       ├── fix-debug-analysis/
│       │   └── SKILL.md                # Codex debugging skill (YAML frontmatter)
│       └── advisor/
│           └── SKILL.md                # Advisor skill (YAML frontmatter)
│
├── .github/
│   ├── copilot-instructions.md         # GitHub Copilot main instructions
│   └── instructions/                   # 12 instruction files (applyTo: frontmatter)
│       └── *.instructions.md           # Same rule body as .claude/rules/
│
└── .vscode/
```

## Usage

To use these instructions in a JASP module, copy **all** of the following into your module root:

- `.claude/` — shared R scripts (`r-preamble.R`, `session_startup.R`), Claude Code rules, hooks and skills. **Always required**, even if you only use Copilot or Codex, because all platforms use these scripts.
- `.codex/` — OpenAI Codex CLI config and rules
- `.agents/` — cross-platform skills (e.g., `fix-debug-analysis`)
- `.github/` — GitHub Copilot instructions
- `AGENTS.md` — Codex CLI main instructions

The AI assistants will automatically detect and use these instructions when working in your module.

## Prerequisites

For AI agents to function properly with JASP modules, ensure the following:

### System PATH Requirements

- **Rscript**: Must be accessible from PATH; agents call R directly
- **python**: Required by the Claude Code Stop hooks and the advisor skill
- **qml**: Qt's qml tools (specifically `qmllint`) must be on PATH for QML validation and linting

### R Setup

Run once per checkout:

```bash
Rscript --no-init-file -e 'source(".claude/session_startup.R")'
```

This restores dependencies via `renv::restore()`, installs the module and
jaspTools, and configures `module.dirs`.

Thereafter agents call R directly. Every `Rscript` call is a fresh process, so
each one sources the shared bootstrap:

```bash
Rscript --no-init-file -e 'source(".claude/r-preamble.R"); agentTestAll()'
```

## Skills

A shared **fix-debug-analysis** skill is available for debugging JASP analysis functions via code inspection and `saveRDS` state capture. It is deployed in platform-specific formats:

- **Claude Code**: `.claude/skills/fix-debug-analysis.md`
- **Codex CLI**: `.agents/skills/fix-debug-analysis/SKILL.md` — invoke with `$fix-debug-analysis` or let Codex auto-trigger it
- **GitHub Copilot**: embedded in `.github/instructions/fix-debug-analysis.instructions.md`

## Safety Features

### Claude Code hook

`.claude/hooks/block-test-edits.js` is a `PreToolUse` hook that prevents the agent from directly editing test files under `tests/`. Test snapshots require human review before acceptance.

### Codex CLI execution policy

`.codex/rules/default.rules` is a Starlark policy file that gates shell commands — for example, forbidding `git push --force` and prompting before any `git push`.

## Maintaining Instruction Files

Rule content is kept byte-identical across all three platforms. The canonical source of truth is `.claude/rules/`. See [MIGRATION.md](MIGRATION.md) for the full sync workflow.

Quick sync checklist when updating instructions:

- [ ] Rule body text is identical across `.claude/rules/`, `.codex/rules/`, `.github/instructions/`
- [ ] Main instruction files reference the correct rule directory for their platform
- [ ] New rules are linked in all three main instruction files
- [ ] Skills exist in both `.claude/skills/` and `.agents/skills/`
- [ ] Execution policy in `.codex/rules/default.rules` reflects any new safety constraints
- [ ] Claude hooks in `.claude/hooks/` reflect any new safety constraints

## Contributing

This repository is continuously updated as instruction files are refined and best practices evolve.

To contribute:

1. Create a pull request with your proposed changes
2. Assign either **@fbartos** or **@vandenman** as reviewers
