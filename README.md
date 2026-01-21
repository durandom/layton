# Layton

**Personal AI secretary for attention management** - A Claude Code skill that helps you track what matters, maintain focus, and get context-aware briefings.

## The Problem

Managing attention across multiple projects is hard. You lose track of what you were working on, forget items you wanted to watch, and context-switch without closure. Your AI assistant starts each conversation with zero knowledge of your priorities.

## The Solution

Layton acts as your personal secretary:

- **Tracks attention items** - Things you're watching, waiting on, or want to remember
- **Maintains focus** - One designated "current work" item at any time
- **Provides orientation** - Combined status of health, skills, and workflows in one command
- **Adapts to context** - Time-of-day aware briefings that respect your work hours

## Installation

```bash
# Add the marketplace
/plugin marketplace add durandom/layton

# Install the plugin
/plugin install layton@layton
```

Or install directly:

```bash
/plugin marketplace add durandom/layton && /plugin install layton@layton
```

## Prerequisites

**Required:** [Beads CLI](https://github.com/beads-ai/beads-cli) (`bd`) must be installed and available on PATH.

Verify with:

```bash
bd --version
```

## Quick Start

After installation, run the setup workflow:

```text
/layton
# Select "setup" or type "configure"
```

This creates your configuration in `.layton/config.json`.

## Commands

| Command | Description |
|---------|-------------|
| `/layton` | Full orientation (doctor + skills + workflows) |
| `/layton doctor` | Health checks |
| `/layton context` | Temporal context (time, work hours, timezone) |
| `/layton config show` | Display configuration |
| `/layton config init` | Create default config |
| `/layton config get <key>` | Get specific value |
| `/layton config set <key> <value>` | Set value |
| `/layton skills` | List known skills |
| `/layton skills --discover` | Find available skills |
| `/layton skills add <name>` | Create new skill file |
| `/layton workflows` | List workflows |
| `/layton workflows add <name>` | Create new workflow |

## Workflows

| Workflow | Purpose |
|----------|---------|
| `setup.md` | Interactive onboarding for new users |
| `track-item.md` | Add item to attention list |
| `set-focus.md` | Set current focus (only one at a time) |
| `retrospect.md` | Reflect on a completed workflow |
| `audit-project-instructions.md` | Review CLAUDE.md against best practices |

## Examples

The `examples/` directory contains workflow patterns:

- `morning-briefing.md` - Context-aware daily briefing
- `gather.md` - Aggregate data from all skills
- `focus-suggestion.md` - Help decide what to work on
- `CLAUDE.md` - Example project instructions
- `AGENTS.md` - Example agent configuration

To use an example:

1. Study it in `examples/` for patterns
2. Create your version: `/layton workflows add <name>`
3. Customize in `.layton/workflows/`

## Configuration

Default config location: `.layton/config.json`

```json
{
  "timezone": "America/Los_Angeles",
  "work": {
    "schedule": {
      "start": "09:00",
      "end": "17:00"
    }
  }
}
```

## How It Works

Layton integrates with [Beads](https://github.com/beads-ai/beads-cli) for state management:

- Items you track become beads with the `watching` label
- Your current focus gets the `focus` label (only one at a time)
- All Layton-created beads have the `layton` label

## License

MIT
