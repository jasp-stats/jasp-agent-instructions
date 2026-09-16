# JASP Agent Instructions

Common resource for AI workflows across JASP R modules.

## Purpose

This repository contains instruction files that guide AI coding assistants (GitHub Copilot, Claude Code, OpenAI Codex CLI) when working with JASP modules. These instructions ensure consistent development practices, coding standards, and best practices across all JASP R packages when using AI coding assistants.

Three platforms are supported, each with its own configuration directory:

| Platform | Main instructions | Rules directory | Config |
| -------- | ----------------- | --------------- | ------ |
| **Claude Code** | `.claude/CLAUDE.md` | `.claude/rules/` | `.mcp.json` |
| **OpenAI Codex CLI** | `AGENTS.md` | `.codex/rules/` | `.codex/config.toml` |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/instructions/` | `.vscode/mcp.json` |

## Repository Structure

```text
repo/
├── AGENTS.md                           # Codex CLI main instructions
├── MIGRATION.md                        # Cross-platform sync guide
│
├── .claude/
│   ├── CLAUDE.md                       # Claude Code main instructions
│   ├── mcp-server.R                    # Shared MCP server script (all platforms)
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
│       ├── fix-debug-analysis.md       # Claude debugging skill
│       └── advisor/SKILL.md            # Consult a stronger model when stuck
│
├── .codex/
│   ├── config.toml                     # Codex MCP servers + execution policy
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
    └── mcp.json                        # Copilot MCP config (not committed)
```

## Usage

To use these instructions in a JASP module, copy **all** of the following into your module root:

- `.claude/` — shared R scripts (`mcp-server.R`, `session_startup.R`) and Claude Code rules. **Always required**, even if you only use Copilot or Codex, because all platform MCP configs reference these scripts.
- `.codex/` — OpenAI Codex CLI config and rules
- `.agents/` — cross-platform skills (e.g., `fix-debug-analysis`)
- `.github/` — GitHub Copilot instructions
- `AGENTS.md` — Codex CLI main instructions

Then create the platform-specific MCP config file(s) for the agents you use (see [MCP Server Configuration](#mcp-server-configuration) below). These are machine-specific and should not be committed.

The AI assistants will automatically detect and use these instructions when working in your module.

## Prerequisites

For AI agents to function properly with JASP modules, ensure the following:

### System PATH Requirements

- **Rscript**: Must be accessible from PATH for R session management and MCP server execution
- **qml**: Qt's qml tools (specifically `qmllint`) must be on PATH for QML validation and linting

### R Packages

The following R packages must be installed before using AI agents:

- **btw**: Provides the MCP server and session registration (`btw::btw_mcp_session()`)
- **mcptools**: Required by the MCP server for tool registration

```r
install.packages(c("btw", "mcptools"))
```

### R Session Handoff

When using AI agents with a JASP module, hand over your interactive R session to enable live R code execution:

1. In your R console (RStudio/Positron/radian), run:

   ```r
   source(".claude/session_startup.R")
   ```

2. This script will:
   - Configure locale and spinner settings
   - Restore dependencies via `renv::restore()`
   - Install the module locally
   - Configure jaspTools
   - Register the session with `btw::btw_mcp_session()`

3. AI agents connect via `list_r_sessions` / `select_r_session` and execute R code in your live session

This enables the agent to access your loaded packages, environment objects, and run analyses interactively.

## MCP Server Configuration

AI agents require MCP (Model Context Protocol) server configuration to access R session tools. All three platforms use the same shared `mcp-server.R` script but with different config file formats. These config files are machine-specific and should be added to `.gitignore`.

### Claude Code (`.mcp.json`)

Create `.mcp.json` in the module root:

```json
{
  "mcpServers": {
    "r-mcptools": {
      "type": "stdio",
      "command": "Rscript",
      "args": ["-e", "source('.claude/mcp-server.R')"]
    }
  }
}
```

Or via CLI: `claude mcp add r-mcptools -- Rscript -e "source('.claude/mcp-server.R')"`

### OpenAI Codex CLI (`.codex/config.toml`)

The Codex config is committed to the repo (sandbox and approval settings are not machine-specific):

```toml
[mcp_servers.r-mcptools]
command = "Rscript"
args = ["-e", "source('.claude/mcp-server.R')"]
```

### GitHub Copilot (`.vscode/mcp.json`)

Create `.vscode/mcp.json` in the module root:

```json
{
  "servers": {
    "r-mcptools": {
      "command": "Rscript",
      "args": ["-e", "source('.claude/mcp-server.R')"]
    }
  }
}
```

All three use the same `Rscript` command to launch `.claude/mcp-server.R`.

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
- [ ] MCP server list matches across `.mcp.json`, `.codex/config.toml`, `.vscode/mcp.json`
- [ ] New rules are linked in all three main instruction files
- [ ] Skills exist in both `.claude/skills/` and `.agents/skills/`
- [ ] Execution policy in `.codex/rules/default.rules` reflects any new safety constraints
- [ ] Claude hooks in `.claude/hooks/` reflect any new safety constraints

## Contributing

This repository is continuously updated as instruction files are refined and best practices evolve.

To contribute:

1. Create a pull request with your proposed changes
2. Assign either **@fbartos** or **@vandenman** as reviewers
