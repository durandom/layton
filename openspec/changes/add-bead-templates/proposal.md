## Why

Layton currently manages skills and workflows as templated markdown files, but has no mechanism for scheduling discrete work units that external executors (like ralph-tui) can pick up and process. Users need a way to define reusable task templates and schedule them as beads for background execution with human-in-the-loop review.

## What Changes

- Add `beads/` directory structure alongside existing `skills/` and `workflows/`
- Add bead template format (frontmatter + body, matching existing patterns)
- Add `layton beads` CLI subcommand for listing, creating, and scheduling beads
- Store project epic ID in existing config under `beads.epic`
- Apply fixed labels (`scheduled`, `type:<name>`) for state management by external tools

## Capabilities

### New Capabilities

- `bead-templates`: Defines the bead template file format, directory structure, frontmatter parsing, and template variable substitution using `string.Template`
- `bead-scheduling`: CLI commands for scheduling beads from templates with JSON variable input, epic management, and `bd` CLI integration
- `bead-workflows`: User-facing workflows for scheduling beads and reviewing completed beads

### Modified Capabilities

- `cli-framework`: Add `layton beads` to orientation output alongside skills and workflows

## Impact

- **New files**: `laytonlib/beads.py`, `templates/bead.md`
- **Modified files**: `laytonlib/cli.py` (add beads subcommand), `laytonlib/config.py` (add beads.epic schema)
- **New directory**: `.layton/beads/` for user templates
- **External dependency**: Requires `bd` CLI for scheduling (already a Layton prerequisite)
