# Bead Template Authoring Guide

This reference explains how to create bead templates for Layton. Bead templates define **autonomous background tasks** — work that an AI executor completes without human interaction, with results tracked in bd for later review.

## How Beads Differ from Workflows

| | Workflows | Bead Templates |
|---|---|---|
| **Execution** | Interactive — AI + human in conversation | Autonomous — AI alone, no human |
| **Input** | Context from conversation | Declared variables, substituted at schedule time |
| **Control flow** | Can pause ("Wait for response"), branch on answers | Linear, fully self-contained |
| **Lifecycle** | Ephemeral (conversation-scoped) | Persistent (tracked as bd items) |
| **Output** | Direct conversation with user | Comments on bd item, reviewed later |

**Rule of thumb:** If the task needs human decisions mid-execution, it's a workflow. If it can run unattended and produce a reviewable result, it's a bead template.

## Template

The bead skeleton is in `templates/bead.md`. The CLI uses this when you run:

```bash
layton beads add <name>
```

This creates `.layton/beads/<name>.md` with the skeleton structure.

## Field Guide

### Frontmatter Fields

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| `name` | Yes | Lowercase with hyphens, matches filename | `starred-email-sync` |
| `description` | Yes | What this bead accomplishes when scheduled | `Sync starred Gmail emails to bd items` |
| `variables` | No | Key-value pairs of scheduling-time inputs | `date_range: How far back to look` |

### Variable Substitution

Bead templates use **two-phase substitution**:

1. **Template creation** (`layton beads add`): `{name}` is replaced via Python `.format()` — used only for the template name in frontmatter and the Retrospective table.
2. **Scheduling** (`layton beads schedule`): `${variable}` is replaced via `string.Template.safe_substitute()` — used for runtime variables in the Task section.

Use `${variable_name}` in the Task and Acceptance Criteria sections for values that change each time the bead is scheduled.

### Section Guide

#### `## Task`

The core instructions the executor follows. Must be **fully autonomous** — no "ask the user" steps.

What to include:

- Concrete commands to run (with `--json` flags)
- Decision logic the AI should apply
- What to do with edge cases
- References to skill files if external tools are needed ("Read `.layton/skills/gmail.md` for commands")

Good example:

```markdown
## Task

1. Read `.layton/skills/gmail.md` for Gmail query commands.

2. Query starred emails from the last ${date_range}:

   ```bash
   mcp-cli google_workspace/search_gmail_messages '{"query": "is:starred newer_than:${date_range}"}'
   ```

3. For each starred email, check if a bd item already exists:

   ```bash
   bd list --label email --json | jq '.[] | select(.external_ref == "gmail:<message_id>")'
   ```

4. Create bd items for new starred emails:

   ```bash
   bd create "<Subject>" --type task --label email --external-ref "gmail:<message_id>" --json
   ```

5. Close bd items for emails that are no longer starred.
```

Bad example:

```markdown
## Task

Sync starred emails to beads. Check for new ones and close old ones.
```

#### `## Acceptance Criteria`

Checkable conditions that must be met. The executor verifies these before closing.

Good example:

```markdown
## Acceptance Criteria

- [ ] All currently starred emails have corresponding bd items
- [ ] Bd items for unstarred emails are closed
- [ ] No duplicate bd items created (checked via external-ref)
- [ ] Summary comment includes counts (new, closed, unchanged)
```

#### `## When Complete`

Standard closing instructions. The skeleton provides sensible defaults:

1. Add findings as a bd comment
2. Close with `--add-label needs-review`

Customize the summary format if the bead produces specific outputs (counts, tables, recommendations).

#### `## Retrospective`

The feedback loop. Two parts:

1. **During execution** — log issues as they happen (step failures, unexpected results)
2. **After closing** — always leave a retrospective comment, even on clean runs

Customize the **Proposed updates** table rows to reference the specific bead, skill, and workflow files relevant to this template. This turns the executor into a contributor that flags improvements.

## Examples

### Minimal Bead Template

```markdown
---
name: stale-items-check
description: Flag watching items that haven't been updated in 7+ days
variables:
  # No variables needed — runs the same every time
---

## Task

1. Query watching items:

   ```bash
   bd list --label watching --json
   ```

2. For each item, check `updated_at`. If older than 7 days, add a comment:

   ```bash
   bd comments add <id> "Stale: no update in 7+ days. Still relevant?"
   ```

3. Add `stale` label to flagged items:

   ```bash
   bd update <id> --add-label stale
   ```

## Acceptance Criteria

- [ ] All watching items checked for staleness
- [ ] Stale items labeled and commented
- [ ] Summary includes count of stale vs active items

## When Complete

1. Add your findings as comments:

   ```bash
   bd comments add "## Summary\n\nChecked N watching items. M flagged as stale."
   ```

2. Close the bead and signal for review:

   ```bash
   bd close --add-label needs-review
   ```

## Retrospective

(standard retrospective section — see skeleton template)
```

### Template with Variables

```markdown
---
name: code-review
description: Review a file or directory for quality issues
variables:
  file_path: The file or directory to review
  focus_area: What to focus on (security, performance, readability, all)
---

## Task

1. Read the target:

   ```bash
   cat ${file_path}
   ```

2. Review with focus on **${focus_area}**. For each issue found, note:
   - File and line number
   - Severity (critical, warning, info)
   - Specific recommendation

3. If the target is a directory, review each file. Prioritize by:
   - Files changed recently (check git log)
   - Files with high complexity

## Acceptance Criteria

- [ ] All files in ${file_path} reviewed
- [ ] Each issue has severity, location, and recommendation
- [ ] Summary includes issue counts by severity
- [ ] No false positives from standard patterns (e.g., test fixtures)

## When Complete

1. Add findings:

   ```bash
   bd comments add "## Code Review: ${file_path}\n\nFocus: ${focus_area}\n\n### Issues\n\n<table of issues>\n\n### Summary\n\nN critical, M warnings, K info"
   ```

2. Close:

   ```bash
   bd close --add-label needs-review
   ```

## Retrospective

(standard retrospective section — customize proposed-updates table)
```

## Common Mistakes

1. **Interactive steps** — "Ask the user which files to review" breaks autonomous execution. All inputs must be variables declared in frontmatter.
2. **Missing commands** — "Query Gmail for starred emails" doesn't tell the executor what command to run. Include exact commands.
3. **No skill file references** — If the task uses external tools, point to the skill file: "Read `.layton/skills/gmail.md`"
4. **Vague acceptance criteria** — "Email sync works" isn't checkable. Use specific, verifiable conditions.
5. **Skipping the retrospective table customization** — Generic `...` rows don't help. List the actual bead, skill, and workflow files this template relates to.
6. **Using `{variable}` instead of `${variable}`** — Single braces are consumed by `.format()` at template creation time. Use `${variable}` for scheduling-time substitution.
7. **Overloading a single bead** — If a bead template has 10+ steps spanning multiple domains, split it into separate templates. Each bead should have a single, clear purpose.
