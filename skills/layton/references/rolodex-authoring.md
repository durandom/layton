# Rolodex Card Authoring Guide

This reference explains how to create rolodex cards for Layton. Rolodex cards define how to query external data sources (Gmail, Jira, Slack, etc.) and what information to extract.

## Template

The rolodex card template is in `assets/templates/rolodex.md`. The CLI uses this when you run:

```bash
layton rolodex add <name>
```text

This creates `.layton/rolodex/<name>.md` with the template structure.

## Field Guide

### Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `name` | Yes | Lowercase identifier matching filename | `gmail` |
| `description` | Yes | When/why Layton should query this card | `Query Gmail for starred emails requiring attention` |
| `source` | No | Where data comes from (MCP server, CLI, API) | `skills/gmail/SKILL.md` or `google_workspace MCP` |

### Section Guide

#### `## Commands`

What to include:

- Exact commands that work from repo root
- Any required setup (environment variables, auth)
- Multiple commands if needed (in order)

Good example:

```markdown
## Commands

```bash
# Requires: JIRA_TOKEN environment variable
jira-cli issue list --project PROJ --status "In Progress" --json
```text

```text

Bad example:
```markdown
## Commands

Query Jira for issues.
```text

#### `## What to Extract`

What to include:

- Specific data points to surface
- What counts as "needs attention"
- Any filtering or prioritization criteria

Good example:

```markdown
## What to Extract

- Count of items assigned to me
- Items blocked or waiting (status = "Blocked")
- Items older than 7 days without update (stale)
- High priority items (P1, P2)
```text

Bad example:

```markdown
## What to Extract

- Important stuff
- Things I should know about
```text

#### `## Key Metrics`

What to include:

- Countable or measurable values
- Status indicators (healthy/warning/critical)
- Thresholds if applicable

Good example:

```markdown
## Key Metrics

| Metric | Meaning |
|--------|---------|
| inbox_count | Emails requiring triage |
| starred_stale | Starred items > 7 days old (decision debt) |
| unread_priority | Unread emails from VIPs |
```text

## Examples

### Minimal Card (CLI tool)

```markdown
---
name: gh-notifications
description: Query GitHub notifications for items needing attention
source: gh CLI
---

## Commands

```bash
gh api notifications --jq '.[] | {reason, subject: .subject.title, url: .subject.url}'
```text

## What to Extract

- Unread notification count
- Mentions and review requests (high priority)
- CI failures on my PRs

## Key Metrics

| Metric | Meaning |
|--------|---------|
| unread_count | Notifications not yet seen |
| review_requests | PRs waiting for my review |
| ci_failures | My PRs with failed checks |

```text

### Card with MCP Server

```markdown
---
name: gmail
description: Query Gmail for starred emails requiring attention
source: google_workspace MCP server
---

## Commands

```bash
mcp-cli google_workspace/search_gmail_messages '{"query": "is:starred"}'
```text

## What to Extract

- Starred count (items flagged for attention)
- Stale items (> 7 days old)
- Unread starred (new items needing attention)
- Sender patterns (who's waiting on me)

## Key Metrics

| Metric | Meaning |
|--------|---------|
| starred_count | Items flagged for attention |
| starred_stale | Decision debt accumulating |
| starred_unread | New items needing triage |

```text

## Optional Sections

Real-world rolodex cards often grow beyond the minimal template. Here are optional sections you can add:

### `## Quick Start`

A 30-second orientation for users who just want to use the card NOW:

```markdown
## Quick Start

```bash
GTD="./.claude/skills/gtd/scripts/gtd"
$GTD              # Status overview with next steps
$GTD list         # All tasks grouped by context
$GTD next         # Suggested next action
```text

The script output includes **Next steps** with available commands. Follow those.

```text

### `## Actions`

For cards that DO things (not just query), document the action commands:

```markdown
## Actions

| Action | Command |
|--------|---------|
| Read thread | `get_gmail_thread_content` with thread_id |
| Remove star | `modify_gmail_message_labels` remove `STARRED` |
| Archive | `modify_gmail_message_labels` remove `INBOX` |
| Archive + Unstar | Remove both `INBOX` and `STARRED` |
```text

### `## Errands Integration`

If the card creates or updates errands, document the integration:

```markdown
## Errands Integration

Email errands use `external-ref` for unique identification:

```bash
# Create email errand
bd create "<Subject>" \
  --type task \
  --label email \
  --external-ref "gmail:<message_id>"

# List tracked emails
bd list --label email --json
```text

### Errand Labels for This Card

| Label | Meaning |
|-------|---------|
| `email` | Item originates from email |
| `starred` | Still starred in Gmail |
| `needs-reply` | Reply required |

```text

### `## Common Patterns`

Frequent usage examples that save users time:

```markdown
## Common Patterns

```bash
# Close multiple items at once
$GTD bulk 17,7,3,25 --close

# Set due date
$GTD due 46 2026-01-30

# View task with full context
gh issue view 42 --repo owner/repo --comments
```text

```text

### `## Pitfalls`

What NOT to do — saves users from common mistakes:

```markdown
## Pitfalls

| Don't | Do |
|-------|-----|
| Start work without creating an Errand | `bd create ... --external-ref "gtd-<id>"` first |
| `gtd done 1 2 3` | `gtd bulk 1,2,3 --close` |
| Run from card dir | Run from **repo root** |
```text

### `## Domain Reference`

For cards with domain-specific syntax (like Gmail search operators):

```markdown
## Gmail Search Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `is:starred` | `is:starred` | Starred emails |
| `newer_than:` | `newer_than:7d` | Within last 7 days |
| `from:` | `from:boss` | From specific sender |
```text

## Common Mistakes

1. **Vague descriptions** - "Query Jira" doesn't tell Layton when to use it
1. **Missing commands** - AI can't gather data without executable commands
1. **Commands that require interaction** - Use `--json` flags, avoid prompts
1. **Credentials in card files** - Reference env vars, never embed secrets
1. **Overly complex extraction** - Keep metrics actionable, not comprehensive
1. **Query-only thinking** - Real cards often need Action commands too
1. **No Errands integration** - If items should be tracked, document how
