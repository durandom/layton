# Protocol Authoring Guide

This reference explains how to create protocol files for Layton. Protocol files are AI-readable instructions that define multi-step processes like briefings, reviews, and data gathering.

## Template

The protocol template is in `assets/templates/protocol.md`. The CLI uses this when you run:

```bash
layton protocols add <name>
```text

This creates `.layton/protocols/<name>.md` with the template structure.

## Field Guide

### Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `name` | Yes | Lowercase with hyphens, matches filename | `morning-briefing` |
| `description` | Yes | One-line summary of what this protocol does | `Context-aware morning status update` |
| `triggers` | Yes | Phrases that activate this protocol (2-5 recommended) | `["good morning", "daily standup"]` |

### Section Guide

#### `## Objective`

What to include:

- Clear statement of the protocol's purpose
- What the user should have when it completes
- Any important constraints or scope

Good example:

```markdown
## Objective

Provide a context-aware status update at the start of the day. Synthesize current focus, attention items, and schedule into a cohesive briefing using the Layton persona voice.
```text

Bad example:

```markdown
## Objective

Do the morning briefing.
```text

#### `## Steps`

What to include:

- Numbered steps in execution order
- Concrete commands where applicable
- What to do with the results of each step

Good example:

```markdown
## Steps

### 1. Get Context

Gather temporal and environmental context:

```bash
layton context
```text

Parse the output to understand:

- Current time of day (morning, afternoon, evening)
- Whether currently in work hours
- Day of week (workday vs weekend)

### 2. Get Attention Items

Query items being actively tracked:

```bash
bd list --label watching --json
```text

### 3. Synthesize Briefing

Combine context and items into a briefing. Present in this order:

1. Current focus (if any)
1. Attention items (sorted by priority)
1. Time-appropriate suggestions

```text

Bad example:
```markdown
## Steps

1. Check stuff
1. Get the data
1. Tell the user about it
```text

#### `## Context Adaptation`

What to include:

- How the protocol should adapt to different situations
- Time-based variations (morning vs evening, workday vs weekend)
- Load-based variations (high vs low attention count)

Good example:

```markdown
## Context Adaptation

| Context | Adaptation |
|---------|------------|
| Morning + work hours | Full briefing with all details |
| Evening + not work hours | Brief summary only |
| Attention count > 5 | Suggest triage before detailed review |
| Weekend | Lighter touch, acknowledge personal time |
| Monday morning | Include weekly perspective |
```text

#### `## Success Criteria`

What to include:

- Checkable conditions for protocol completion
- What the user should have/know when done
- Any side effects that should have occurred

Good example:

```markdown
## Success Criteria

- [ ] Briefing adapts to time of day and work status
- [ ] Focus item mentioned first (if one exists)
- [ ] Attention items summarized with accurate counts
- [ ] Actionable next step suggested
```text

## Examples

### Minimal Protocol

```markdown
---
name: quick-status
description: Fast status check of focus and watching items
triggers:
  - quick status
  - what am I doing
  - status check
---

## Objective

Provide a rapid status snapshot without full briefing ceremony.

## Steps

1. Get current focus:
   ```bash
   bd list --label focus --json
   ```

1. Get watching count:

   ```bash
   bd list --label watching --json | jq length
   ```

1. Report in one sentence:
   - "You're focused on [X], watching [N] items."
   - Or: "No current focus. Watching [N] items."

## Context Adaptation

- Always brief, regardless of time
- If focus is stale (> 1 day old), mention it

## Success Criteria

- [ ] Focus reported (or absence noted)
- [ ] Watching count accurate
- [ ] Response is one sentence

```text

### Complex Protocol

```markdown
---
name: weekly-review
description: End-of-week reflection on completed work and planning for next week
triggers:
  - weekly review
  - end of week
  - friday review
  - week in review
---

## Objective

Guide user through a structured weekly review: celebrate wins, clear completed items, identify carryover, and set intentions for next week.

## Steps

### 1. Get Context

```bash
layton context
```text

Confirm it's end of week (Thursday PM or Friday).

### 2. Review Completed Items

```bash
bd list --label closed --since "7 days ago" --json
```text

Summarize what was accomplished this week.

### 3. Review Watching Items

```bash
bd list --label watching --json
```text

For each item:

- Still relevant? → Keep
- Completed? → Close it
- Stale? → Discuss with user

### 4. Check Focus

```bash
bd list --label focus --json
```text

Is current focus still the right priority for next week?

### 5. Plan Next Week

Ask user:

- What's the most important thing for next week?
- Anything to add to watching list?
- Any deadlines coming up?

### 6. Summarize

Provide a summary:

- This week: [wins]
- Cleared: [closed items]
- Carrying forward: [active watching]
- Next week focus: [intention]

## Context Adaptation

| Context | Adaptation |
|---------|------------|
| Friday afternoon | Full review |
| Friday morning | Abbreviated, offer to continue later |
| Thursday evening | Proactive, "getting a head start" |
| Monday | "Let's do a quick retrospective instead" |

## Success Criteria

- [ ] Wins from this week acknowledged
- [ ] Stale watching items addressed
- [ ] Next week intention captured
- [ ] User feels closure on the week

```text

## Optional Sections

### `## Example Output`

Show what the protocol result should look like. This helps AI understand the expected format and tone:

```markdown
## Example Output

> Good morning.
>
> **Focus:** You're currently focused on "API refactoring for v2"
>
> **Watching:** 3 items (1 PR awaiting review, 2 issues tracked)
>
> **GTD:** Inbox clear ✓ | 4 focus tasks ready | 2 active projects
>
> **Suggestion:** Your high-energy morning slot is ideal for the architecture review. I'd start there.
```text

This is especially valuable for:

- Briefings (shows expected structure and tone)
- Reports (shows formatting expectations)
- Any protocol where output format matters

## Common Mistakes

1. **Vague steps** - "Check the status" doesn't tell AI what command to run
1. **Missing commands** - If a step needs data, include the exact command
1. **No adaptation** - Protocols should flex based on context
1. **Too many triggers** - 2-5 focused triggers beat 10 overlapping ones
1. **Rigid structure** - Leave room for AI judgment within steps
1. **No success criteria** - How do you know when it's done?
1. **No example output** - For briefings/reports, show what good looks like
1. **Reinventing existing skills** — Before writing a protocol that does code review, debugging, planning, or auditing from scratch, check if an installed Claude Code skill already handles it. Delegate the domain work; keep the protocol focused on orchestration and context.
