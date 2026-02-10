# JASP Agent Instructions

Common resource for AI workflows across JASP R modules.

## Purpose

This repository contains instruction files that guide AI coding assistants (GitHub Copilot, Claude, etc.) when working with JASP modules. These instructions ensure consistent development practices, coding standards, and best practices across all JASP R packages when using AI coding assistants.

## Usage

To use these instructions in a JASP module:

1. **Copy the instruction directories** from this repository to your module repository:
   - Copy `.github/` directory (contains GitHub Copilot instructions)
   - Copy `.claude/` directory (contains Claude-specific instructions)

2. The AI assistants will automatically detect and use these instructions when working in your module.

## Prerequisites

For AI agents to function properly with JASP modules, ensure the following:

### System PATH Requirements

- **Rscript**: Must be accessible from PATH for R session management and MCP server execution
- **qml**: Qt's qml tools (specifically `qmllint`) must be on PATH for QML validation and linting

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

3. AI agents will connect via `list_r_sessions` / `select_r_session` and execute R code in your live session

This enables the agent to access your loaded packages, environment objects, and run analyses interactively.

## Contributing

This repository is continuously updated as instruction files are refined and best practices evolve.

To contribute:
1. Create a pull request with your proposed changes
2. Assign either **@fbartos** or **@vandenman** as reviewers

## Maintenance

When updating instructions:
- Ensure changes align with JASP development standards
- Update this README if structural changes are made
