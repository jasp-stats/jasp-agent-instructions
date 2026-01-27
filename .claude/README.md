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
├── CLAUDE.md                          # Main project instructions
├── README.md                          # This file
└── rules/                             # Path-specific rules
    ├── r-instructions.md              # R backend guidelines (**/R/*.R)
    ├── qml-instructions.md            # QML interface guidelines (**/inst/qml/*.qml)
    ├── testing-instructions.md        # Test framework guidelines (**/tests/testthat/*.R)
    ├── git-workflow.md                # Git and commit conventions
    └── translation-instructions.md    # i18n/l10n guidelines
```

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

## Related Files

- `.github/copilot-instructions.md` - GitHub Copilot instructions
- `.github/instructions/` - Additional Copilot-specific rules

These files share similar content for consistency across AI coding assistants.

## More Information

For details about Claude Code's memory system:
- See the official documentation: https://github.com/anthropics/claude-code
- Run `/help` in Claude Code for in-CLI help
