---
name: author-protocol
description: Create or capture a protocol file for Layton
triggers:
  - create a protocol
  - new protocol
  - add protocol
  - turn this into a protocol
  - save as protocol
  - capture protocol
  - make this repeatable
  - protocol authoring
---

<required_reading>
**Read before starting:**

1. references/protocol-authoring.md - Template and field guide
</required_reading>

## Objective

Help the user create a well-populated protocol file. This protocol handles both:

- **Creating** a new protocol from scratch (guided Q&A)
- **Capturing** a protocol from recent conversation (retrospective extraction)

## Steps

### 1. Determine Mode

Ask the user:

> "I can help you create a protocol file. Which mode?
>
> 1. **Create from scratch** - I'll guide you through defining a new protocol
> 2. **Capture from conversation** - I'll extract a protocol from what we just did
> 3. **Edit existing** - Update a protocol file you already have"

**Wait for response.**

Route based on answer:

- 1 → Continue to "Create Mode" section
- 2 → Continue to "Capture Mode" section
- 3 → Ask which protocol, then read and edit it

---

## Create Mode

### 2a. Understand the Purpose

Ask the user:

> "What protocol do you want to create?
>
> 1. **Name**: What should we call it? (lowercase with hyphens, e.g., 'morning-briefing')
> 2. **Purpose**: What does it accomplish? When would you run it?"

**Wait for response.** Extract `name` and `description`.

### 3a. Define Triggers

Ask the user:

> "What phrases should trigger this protocol? These are things you might say.
>
> Examples for a morning briefing: 'good morning', 'daily standup', 'what should I know'
>
> What 2-5 phrases work for yours?"

**Wait for response.** Extract triggers list.

### 4a. Map the Steps

Guide through steps one at a time:

> "Walk me through what this protocol should do, step by step.
>
> For each step:
>
> - What action? (run a command, query something, synthesize)
> - What data is needed?
> - Any decisions based on results?
>
> Start with step 1..."

**Wait for each step.** Continue until user indicates completion.

### 5a. Identify Adaptations

Ask the user:

> "Should this protocol behave differently based on context?
>
> Examples:
>
> - Morning vs evening
> - Workday vs weekend
> - High vs low workload
>
> Any adaptations?"

**Wait for response.** Extract context rules.

### 6a. Define Success

Ask the user:

> "How do you know this protocol completed successfully?
> What should be true when it's done?"

**Wait for response.** Extract success criteria.

Continue to "Create the File" section.

---

## Capture Mode

### 2b. Review Conversation

Scan recent conversation for:

- **Sequence of actions**: What steps were taken, in what order
- **Commands run**: bash, MCP calls, queries
- **Decisions made**: conditional logic, branching
- **Synthesis**: how information was combined

Present findings:

> "From our conversation, I identified these steps:
>
> 1. {step 1}
> 2. {step 2}
> ...
>
> Is this the process to save? Anything to add or change?"

**Wait for confirmation.**

### 3b. Name and Triggers

If not obvious, ask:

> "What should we call this protocol?
> And what phrases should trigger it?"

**Wait for response.**

Continue to "Create the File" section.

---

## Create the File

### 7. Check for Existing

```bash
layton protocols
```

If protocol name already exists, ask if user wants to overwrite or pick a different name.

### 8. Generate the Protocol File

```bash
layton protocols add <name>
```

This creates a file from `assets/templates/protocol.md`. Edit it to replace the skeleton placeholders with the gathered/captured information.

Reference `references/protocol-authoring.md` for field guidance and optional sections.

### 9. Validate and Confirm

Show the user the created file.

> "Here's the protocol. Does this capture what you wanted?
>
> Want to do a dry-run walkthrough?"

If dry-run:

- Walk through each step
- Show what would happen
- Confirm the flow makes sense

## Context Adaptation

- **If user says "turn this into a protocol"**: Go directly to Capture Mode
- **If user says "create a protocol for X"**: Go directly to Create Mode
- **If process was simple** (2-3 steps): Keep it concise
- **If process was complex**: Consider breaking into phases
- **If steps overlap with existing protocols**: Note and suggest extension

## Success Criteria

- [ ] Protocol file created at `.layton/protocols/<name>.md`
- [ ] All sections populated (not skeleton placeholders)
- [ ] Triggers are natural phrases the user would say
- [ ] Steps are clear enough for AI to follow
- [ ] User confirms the protocol looks correct
