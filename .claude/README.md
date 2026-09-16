# Claude Code Instructions

This directory contains project-specific instructions for Claude Code, Anthropic's CLI tool.

## Purpose

These files are automatically loaded when Claude Code starts, providing context about:

- JASP module structure and conventions
- Development workflows and best practices
- Testing requirements
- Translation guidelines

## Structure

```
.claude/
├── CLAUDE.md                          # Main project instructions (always loaded)
├── README.md                          # This file
├── r-preamble.R                       # Per-call R bootstrap
├── session_startup.R                  # One-time module + jaspTools install
├── hooks/                             # PreToolUse and Stop hooks
├── skills/                            # advisor, fix-debug-analysis
├── settings.local.json                # Claude Code settings, incl. Stop hooks
└── rules/                             # Path-specific rules
    ├── r-instructions.md              # R backend guidelines (**/R/*.R)
    ├── qml-instructions.md            # QML interface guidelines (**/inst/qml/*.qml)
    ├── testing-instructions.md        # Test framework guidelines (**/tests/testthat/*.R)
    ├── git-workflow.md                # Git and commit conventions
    └── translation-instructions.md    # i18n/l10n guidelines
```

## Running R

Agents call R directly -- every `Rscript` call is a fresh process:

```bash
Rscript --no-init-file -e 'source(".claude/r-preamble.R"); agentTestAll()'
```

`r-preamble.R` loads the project library and configures jaspTools.
`session_startup.R` does the one-time install and is run once per checkout.

## Turn Discipline and Advisor

`settings.local.json` registers two `Stop` hooks: a self-check checklist and
`hooks/stop-audit.py`, an independent audit of the turn by a separate
`claude -p` session. Logs land in `logs/` (gitignored). `skills/advisor/`
consults a stronger model when genuinely stuck.

## How It Works

**Automatic Loading:**

- `CLAUDE.md` is automatically loaded in every Claude Code session
- Files in `rules/` are loaded based on their `paths:` frontmatter
- Path-specific rules apply only when working on matching files

**Path Scoping:**
Rules use YAML frontmatter to scope to specific files:

```yaml
---
paths:
  - "**/R/*.R"
---
```

## Copying to Other JASP Modules

To use these instructions in another JASP module:

1. Copy the `.claude/` directory to the target module
2. Run the one-time setup: `Rscript --no-init-file -e 'source(".claude/session_startup.R")'`
3. Adjust the `Rscript` command path if needed for your system
4. Add `.claude/logs/` to the module `.gitignore`

## Personal Preferences

To add personal project-specific preferences that aren't shared with the team:

1. Create `CLAUDE.local.md` in this directory
2. Add your personal preferences
3. File is already in `.gitignore` and won't be committed

## Maintenance

**When to update:**

- Adding new development conventions
- Changing testing requirements
- Updating build/deployment processes
- Adding new repository-specific workflows

**What to include:**

- Information Claude can't infer from code
- Project-specific conventions that differ from defaults
- Critical commands and workflows
- Non-obvious patterns and gotchas

**What to exclude:**

- Standard language conventions
- Detailed API documentation (link to it instead)
- Frequently changing information
- Information easily discovered by reading code
