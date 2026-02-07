---
name: layton
description: Personal AI secretary for attention management. Manages focus, tracking, briefings, and orientation across connected systems. Invoke for morning briefings, status checks, scheduling background tasks, tracking items, setting focus, or querying external tools (calendar, email, tasks).
---

<objective>
Layton is your personal secretary—managing attention, synthesizing information from multiple systems, and providing context-aware briefings. It uses three primitives (skill files, workflows, bead templates) and a thin CLI for orientation, health checks, temporal context, configuration, and discovery.
</objective>

<essential_principles>

- Use `bd` directly for all state operations (never wrap it)
- Always include `--json` flag for machine-readable output
- Always include `layton` label on beads Layton creates
- Only ONE bead should have `focus` label at any time
- Workflows are AI instructions—Layton follows them, not executes them as code
- Skill files in `.layton/skills/` define how to query external tools
- User workflows in `.layton/workflows/` are customizable by users
- **ALWAYS** run `$LAYTON` at session start before any other action
- **NEVER** query external tools without first reading their skill file in `.layton/skills/`
- **NEVER** skip a workflow if the routing table matches the user's intent
</essential_principles>

<primitives>

## Three Primitives

Layton has three building blocks. Each serves a distinct role:

| Primitive | What it is | Execution model | Stored in |
| --- | --- | --- | --- |
| **Skill** | How to query an external tool (Gmail, Jira, calendar) | Referenced by workflows and beads | `.layton/skills/` |
| **Workflow** | Interactive multi-step process (briefings, reviews, authoring) | AI + human in conversation — can pause, branch, ask questions | `.layton/workflows/` |
| **Bead template** | Autonomous background task (syncs, checks, reviews) | AI alone, no human — runs unattended, results reviewed later | `.layton/beads/` |

**When to use which:**

- Need to **query data** from an external system? → Write a **skill** file.
- Need to **guide a conversation** with decision points? → Write a **workflow**.
- Need to **run something unattended** and review the result later? → Write a **bead template**.

Workflows and beads both reference skills for external tool access. The key difference is human involvement: workflows are interactive, beads are autonomous.

See `references/skill-authoring.md`, `references/workflow-authoring.md`, and `references/bead-authoring.md` for authoring guides.

</primitives>

<decision_framework>

## WORKFLOW-FIRST DECISION FRAMEWORK

Before taking ANY action, follow this sequence:

1. **Orient:** Run `$LAYTON` to discover state, skills, and workflows.
2. **Route:** Scan `<routing>` for intent matches. If found, read the workflow file and follow it exactly.
3. **Skill lookup:** If the task involves an external tool, read its skill file in `.layton/skills/` before querying. Never guess commands.
4. **Fallback:** Only if no routing match — clarify intent with user, then select a workflow.

**Never skip orientation. Never query external tools without reading their skill file first.**

</decision_framework>

<intake>
## Step 1: Run CLI

```bash
$LAYTON
```

## Step 2: Menu

What would you like to do?

1. Get oriented (full status check)
2. Track something (add to attention list)
3. Set focus (designate current work item)
4. Retrospect on workflow (reflect on what worked)
5. Something else

**Wait for response before proceeding.**
</intake>

<routing>
| Response | Workflow |
| --- | --- |
| 1, "orient", "status", "check", "what's going on" | Run `$LAYTON` (no args) |
| 2, "track", "watch", "monitor", "keep eye on" | `references/workflows/track-item.md` |
| 3, "focus", "working on", "what should I do", "next task", "priority" | `references/workflows/set-focus.md` |
| 4, "retrospect", "reflect", "retro", "what worked" | `references/workflows/retrospect.md` |
| 5, other | Clarify intent, then select |

**Intent-based routing (bypass menu):**

| Intent / Trigger Phrases | Workflow |
| --- | --- |
| "setup", "configure", "onboard", "first time" | `references/workflows/setup.md` |
| "audit", "review instructions", "check CLAUDE.md" | `references/workflows/audit-project-instructions.md` |
| "skill", "add skill", "create skill", "capture skill", "new skill" | `references/workflows/author-skill.md` |
| "workflow", "add workflow", "create workflow", "capture workflow", "new workflow" | `references/workflows/author-workflow.md` |
| "bead template", "create bead template", "new bead template", "author bead" | `references/workflows/author-bead-template.md` |
| "schedule bead", "run template", "background task" | `references/workflows/schedule-bead.md` |
| "review beads", "pending review", "check completed", "what finished" | `references/workflows/review-beads.md` |

**External tool queries (calendar, tasks, email, etc.):**

| Intent / Trigger Phrases | Action |
| --- | --- |
| "calendar", "schedule", "meetings", "agenda" | Check `.layton/skills/` for calendar skill |
| "tasks", "todos", "inbox", "gtd", "things to do" | Check `.layton/skills/` for task skill |
| "email", "messages", "mail" | Check `.layton/skills/` for email skill |
| "git", "commits", "PRs", "code" | Check `.layton/skills/` for git skill |

**After selecting a workflow, read and follow it exactly.**
</routing>

<quick_start>

**Get oriented** (full status):

```bash
$LAYTON
```

**Setup for first-time users**: Run workflow in `references/workflows/setup.md`

**Morning briefing**: Follow `references/examples/morning-briefing.md` (or create your own via `layton workflows add morning-briefing`)

**Track something**: Run workflow in `references/workflows/track-item.md`

**Set focus**: Run workflow in `references/workflows/set-focus.md`

**Gather data from skills**: Follow `references/examples/gather.md`

**Focus suggestions**: Follow `references/examples/focus-suggestion.md`
</quick_start>

<cli_setup>
**Locate and set the CLI variable:**

The CLI script is at `scripts/layton` **relative to this SKILL.md file** (not the working directory).

When you read this file, note its path and derive the script location:

- If SKILL.md is at `/path/to/skills/layton/SKILL.md`
- Then the CLI is at `/path/to/skills/layton/scripts/layton`

```bash
LAYTON="/path/to/skills/layton/scripts/layton"  # Use the actual path
```

</cli_setup>

<cli_commands>

**Orientation (no args):**

```bash
$LAYTON
```

Returns combined doctor checks + skills inventory + workflows inventory. Use this for full AI orientation at start of any briefing or workflow.

**Health check:**

```bash
$LAYTON doctor
```

**Temporal context:**

```bash
$LAYTON context
```

Output: timestamp, time_of_day, day_of_week, work_hours, timezone

**Configuration:**

```bash
$LAYTON config show       # Display config
$LAYTON config init       # Create default config
$LAYTON config get <key>  # Get specific value
$LAYTON config set <key> <value>  # Set value
```

**Skills:**

```bash
$LAYTON skills                 # List known skills from .layton/skills/
$LAYTON skills --discover      # Find skills in skills/*/SKILL.md
$LAYTON skills add <name>      # Create new skill file from template
```

**Workflows:**

```bash
$LAYTON workflows              # List workflows from .layton/workflows/
$LAYTON workflows add <name>   # Create new workflow file from template
```

**Bead Templates:**

```bash
$LAYTON beads                  # List bead templates from .layton/beads/
$LAYTON beads add <name>       # Create new bead template from skeleton
$LAYTON beads schedule <name> [json]  # Schedule bead from template with variables
```

</cli_commands>

<file_index>

**Workflows** (in `references/workflows/`):

| File | Purpose |
| --- | --- |
| setup.md | Interactive onboarding for new users |
| track-item.md | Add item to attention list |
| set-focus.md | Set current focus (only one at a time) |
| retrospect.md | Reflect on a completed workflow |
| audit-project-instructions.md | Review CLAUDE.md/AGENTS.md against best practices |
| author-skill.md | Create or capture a skill file |
| author-workflow.md | Create or capture a workflow file |
| author-bead-template.md | Create or capture a bead template |
| schedule-bead.md | Schedule a bead from a template for background execution |
| review-beads.md | Find and review completed beads needing attention |

**References** (in `references/`):

| File | Content |
| --- | --- |
| persona.md | Layton's voice and persona characteristics |
| beads-commands.md | bd CLI command reference for state operations |
| bead-authoring.md | Guide for writing bead templates |
| project-instructions.md | Best practices for CLAUDE.md/AGENTS.md files |
| skill-authoring.md | Guide for writing skill files |
| workflow-authoring.md | Guide for writing workflow files |

**Examples** (in `references/examples/`): `morning-briefing.md`, `gather.md`, `focus-suggestion.md` — study for patterns, then create your own via `$LAYTON workflows add <name>`.

</file_index>
