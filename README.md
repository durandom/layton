# Layton

**Your personal AI secretary.**

Named after [Elizabeth Layton](https://en.wikipedia.org/wiki/Elizabeth_Nel), Churchill's wartime secretary - a trusted assistant who anticipated needs, tracked what mattered, and synthesized information so her boss could focus on what only he could do.

## The Problem

Your AI assistant starts every conversation at zero. It doesn't know what you were working on, what you're waiting for, or what deserves your attention today. You end up repeating context, losing track of threads, and managing your own attention instead of doing the actual work.

## The Vision

Layton remembers for you:

- **What you're watching** - that PR waiting for review, the Jira ticket blocked on someone else
- **Where your focus is** - your current work, so you can context-switch and return
- **How you work** - your schedule, preferences, and patterns
- **What's happening** - synthesized briefings across all your connected systems

Ask "What should I know?" and get an answer that respects your time.

## How It Works

| Concept | What It Is |
|---------|------------|
| **Beads** | State backend - tracks items with labels (`watching`, `focus`, `layton`) |
| **Skills** | Data source definitions (Gmail, Jira, Slack) - AI instructions for querying systems |
| **Workflows** | Orchestration patterns (morning briefing, gather data) - AI instructions for synthesis |
| **.layton/** | Your personalization directory - config, skills, workflows |

Layton is a **knowledge repo skill** for building personalized AI workflows. Skills and workflows are AI instructions (markdown), not executable code - they tell Claude how to query your systems and synthesize information.

## Installation

```bash
claude plugin marketplace add durandom/layton
claude plugin install --scope project layton@layton
```

## Prerequisites

[Beads](https://github.com/beads-ai/beads-cli) - Layton's memory and state backend.

Beads stores everything Layton tracks: items you're watching, your current focus, and metadata from external systems. All state operations use beads labels for filtering (`bd list --label watching`).

```bash
bd --version  # verify it's installed
```

## What You'll Build

After setup, your project will have a `.layton/` directory with your personalized configuration:

```
your-project/
├── .layton/                  # YOUR personalizations
│   ├── config.json          # Timezone, work hours, user info
│   ├── skills/              # Data source definitions
│   │   ├── gmail.md         # How to query Gmail
│   │   ├── jira.md          # How to query Jira
│   │   └── slack.md         # How to query Slack
│   └── workflows/           # Custom orchestrations
│       ├── morning-briefing.md
│       └── process-inbox.md
├── CLAUDE.md                # Project instructions (with Layton integration)
└── AGENTS.md                # Agent behavior rules
```

### Example: config.json

```json
{
  "timezone": "America/New_York",
  "user": {
    "name": "Alex",
    "email": "alex@example.com"
  },
  "work": {
    "schedule": { "start": "09:00", "end": "17:00" },
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
  }
}
```

### Example: Skill File (.layton/skills/gmail.md)

```markdown
---
name: gmail
description: Query Gmail for starred emails requiring attention
source: google_workspace MCP server
---

## Commands

\`\`\`bash
# List starred emails
mcp-cli google_workspace/search_gmail_messages '{"query": "is:starred"}'
\`\`\`

## What to Extract

- Starred count (items flagged for attention)
- Stale items (> 7 days old)
- Unread starred (new items needing attention)

## Key Metrics

| Metric | Meaning |
|--------|---------|
| starred_count | Items flagged for attention |
| starred_stale | Decision debt accumulating |
```

### Example: Workflow File (.layton/workflows/morning-briefing.md)

```markdown
---
name: morning-briefing
triggers: [morning briefing, good morning, what should I know today]
---

## Steps

1. Get temporal context: `layton context`
2. Get current focus: `bd list --label focus --json`
3. Get watching items: `bd list --label watching --json`
4. Query configured skills
5. Synthesize briefing adapted to time of day

## Context Adaptation

| Context | Adaptation |
|---------|------------|
| Morning + workday | Full briefing, suggest high-energy focus work |
| Afternoon | Lighter briefing, check if focus needs updating |
| Evening | Brief summary, acknowledge end of day |
| Monday morning | Include weekly perspective |
```

## Getting Started

### First-Time Setup

```text
/layton
```

Select "setup" or say "configure layton" - Layton will guide you through:

1. Creating `.layton/config.json` with your preferences
2. Discovering available skills
3. Setting up CLAUDE.md/AGENTS.md integration

### Daily Usage

```text
/layton
```

This runs orientation: health checks + skills inventory + workflows inventory.

### Common Interactions

| Say This | Layton Does |
|----------|-------------|
| "Good morning" | Context-aware briefing |
| "What should I know?" | Synthesize status across all skills |
| "I'm working on X" | Set focus (one item at a time) |
| "Track this PR" | Add to watching list |
| "What am I watching?" | List tracked items |

## CLI Reference

```bash
LAYTON=".claude/skills/layton/scripts/layton"
```

| Command | Description |
|---------|-------------|
| `$LAYTON` | Full orientation (doctor + skills + workflows) |
| `$LAYTON doctor` | Health checks (beads, config) |
| `$LAYTON context` | Temporal context (time, work hours, day of week) |
| `$LAYTON config show` | Display current config |
| `$LAYTON config init` | Create default config |
| `$LAYTON config set <key> <value>` | Set config value (dot notation) |
| `$LAYTON skills` | List configured skills |
| `$LAYTON skills --discover` | Find skills in `skills/*/SKILL.md` |
| `$LAYTON skills add <name>` | Create skill file from template |
| `$LAYTON workflows` | List configured workflows |
| `$LAYTON workflows add <name>` | Create workflow from template |

### Beads Commands (State Backend)

```bash
bd list --label watching --json   # Items you're tracking
bd list --label focus --json      # Current focus (only one)
bd create "PR #123" -l watching,github,layton --json
bd update <id> --add-label focus --json
bd close <id> --reason "merged" --json
```

## Built-in Workflows

| Workflow | Purpose |
|----------|---------|
| **setup** | First-time configuration and discovery |
| **set-focus** | Designate current work (one item at a time) |
| **track-item** | Add external item to attention list |
| **retrospect** | Reflect on workflow and suggest improvements |

### Example Workflows (in `examples/`)

| Example | Purpose |
|---------|---------|
| `morning-briefing.md` | Context-aware daily status |
| `gather.md` | Aggregate data from all configured skills |
| `focus-suggestion.md` | Help decide what to work on next |

To copy an example to your `.layton/workflows/`:

```bash
$LAYTON workflows add morning-briefing
```

## Integration with CLAUDE.md / AGENTS.md

Layton works best when integrated into your project's AI instructions.

### Recommended AGENTS.md Section

```markdown
## Session Start Protocol

**BEFORE doing ANYTHING else in a new session, you MUST:**

1. **Invoke the Layton skill**: `/layton`

**NO EXCEPTIONS** - unless the user explicitly says "skip Layton".
```

Run `/layton` and select "setup" to have Layton analyze your existing instruction files and suggest integration points.

## License

MIT
