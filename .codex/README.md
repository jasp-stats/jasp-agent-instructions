# Codex CLI Instructions

This directory contains project-specific configuration for OpenAI Codex CLI.

## Structure

```
.codex/
├── README.md                          # This file
├── config.toml                        # Sandbox, approval, reasoning settings
└── rules/
    ├── default.rules                  # Starlark execution policy (git safety)
    ├── r-instructions.md              # R backend guidelines
    ├── qml-instructions.md            # QML interface guidelines
    ├── testing-instructions.md        # Test framework guidelines
    ├── git-workflow.md                # Git and commit conventions
    ├── translation-instructions.md    # i18n/l10n guidelines
    ├── jasp-module-architecture.md    # QML-Desktop-R reactive loop
    ├── jasp-dependency-management.md  # $dependOn mechanics
    ├── jasp-state-management.md       # createJaspState caching
    ├── jasp-tables.md                 # Table building patterns
    ├── jasp-plots.md                  # Plot building patterns
    ├── jasp-containers-and-errors.md  # Container patterns, error handling
    └── jasp-output-structure.md       # Serialized output format

.agents/
└── skills/
    └── fix-debug-analysis/
        └── SKILL.md                   # Debugging skill (cross-platform)
```

## Setup

### 1. Trust the project

On first launch, Codex prompts to trust the project. Accept to load `.codex/config.toml` and `.codex/rules/`.

### 2. R Setup

Once per checkout:

```bash
Rscript --no-init-file -e 'source(".claude/session_startup.R")'
```

This restores dependencies, installs the module and configures jaspTools.

Thereafter call R directly, sourcing `.claude/r-preamble.R` in each `Rscript` call.

### 3. Using Skills

The `fix-debug-analysis` skill is available at `.agents/skills/fix-debug-analysis/SKILL.md`. Invoke explicitly via `$fix-debug-analysis` or let Codex auto-trigger it when debugging tasks are detected.

## How It Works

**AGENTS.md** (project root) is automatically loaded at session start. It contains the main project instructions and references to rule files in `.codex/rules/`.

**Rule files** in `.codex/rules/` are NOT auto-loaded by path pattern (Codex doesn't support path-scoping). Instead, `AGENTS.md` instructs Codex to read the relevant rule file when working on matching file types.

**Execution policy** in `.codex/rules/default.rules` uses Starlark syntax to gate shell commands (e.g., forbid force-push, prompt before push).

**config.toml** configures sandbox mode, approval policy and reasoning. Shared between Codex CLI and the IDE extension.

## Differences from Claude Code

| Feature | Claude Code (`.claude/`) | Codex CLI (`.codex/`) |
|---------|--------------------------|------------------------|
| Main instructions | `CLAUDE.md` (auto-loaded) | `AGENTS.md` (auto-loaded) |
| Rule files | `.claude/rules/*.md` with `paths:` frontmatter (auto-scoped) | `.codex/rules/*.md` (referenced explicitly from AGENTS.md) |
| Skills | `.claude/skills/<name>/SKILL.md` | `.agents/skills/<name>/SKILL.md` |
| Permissions | `settings.local.json` (granular per-tool) | `config.toml` sandbox + approval |
| Hooks | `hooks/*.js`, `*.py` (PreToolUse, Stop) | Not available (instruction-only) |
| Execution policy | Not available | `.codex/rules/default.rules` (Starlark) |
| Config format | JSON | TOML |

## Copying to Other JASP Modules

1. Copy `AGENTS.md` to the target module root
2. Copy `.codex/` directory to the target module
3. Copy `.agents/` directory to the target module
4. The `.claude/r-preamble.R` and `.claude/session_startup.R` scripts are shared and should already exist
