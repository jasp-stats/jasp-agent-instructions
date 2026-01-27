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

## Repository Structure

```
.
├── .github/
│   ├── copilot-instructions.md          # Main GitHub Copilot instructions
│   └── instructions/
│       ├── R.instructions.md            # R backend development rules
│       └── inst.qml.instructions.md     # QML interface development rules
│
└── .claude/
    ├── CLAUDE.md                        # Claude configuration
    ├── README.md                        # Claude setup guide
    └── rules/
        ├── r-instructions.md            # R development guidelines
        ├── qml-instructions.md          # QML interface guidelines
        ├── testing-instructions.md      # Testing best practices
        ├── translation-instructions.md  # Internationalization rules
        └── git-workflow.md              # Git workflow standards
```

## Contributing

This repository is continuously updated as instruction files are refined and best practices evolve.

To contribute:
1. Create a pull request with your proposed changes
2. Assign either **@fbartos** or **@vandenman** as reviewers

## Maintenance

When updating instructions:
- Ensure changes align with JASP development standards
- Update this README if structural changes are made
