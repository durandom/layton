---
name: author-errand
description: Create or capture an errand for scheduling background tasks
triggers:
  - create an errand
  - new errand
  - add errand
  - author errand
  - turn this into an errand
  - save as errand
  - capture errand
  - make this a scheduled task
---

<required_reading>
**Read before starting:**

1. assets/templates/errand.md - The skeleton template structure
2. references/errand-authoring.md - Authoring guide with field descriptions, examples, and common mistakes
</required_reading>

## Objective

Help the user create a well-populated errand file. This protocol handles both:

- **Creating** a new errand from scratch (guided Q&A)
- **Capturing** an errand from recent conversation (retrospective extraction)

Errands define repeatable background tasks that can be scheduled for execution.

## Steps

### 1. Determine Mode

Ask the user:

> "I can help you create an errand. Which mode?
>
> 1. **Create from scratch** - I'll guide you through defining a new errand
> 2. **Capture from conversation** - I'll extract an errand from what we just did
> 3. **Edit existing** - Update an errand you already have"

**Wait for response.**

Route based on answer:

- 1 → Continue to "Create Mode" section
- 2 → Continue to "Capture Mode" section
- 3 → Ask which errand, then read and edit it

---

## Create Mode

### 2a. Understand the Purpose

Ask the user:

> "What errand do you want to create?
>
> 1. **Name**: What should we call it? (lowercase with hyphens, e.g., 'code-review')
> 2. **Purpose**: What does it accomplish? When would you schedule it?"

**Wait for response.** Extract `name` and `description`.

### 3a. Define Variables

Ask the user:

> "What information does this errand need at scheduling time?
>
> These become variables that get filled in when scheduling.
>
> Examples for a code-review errand:
>
> - `file_path`: The file or directory to review
> - `focus_area`: What aspect to focus on (security, performance, etc.)
>
> What variables does yours need? (name: description for each)"

**Wait for response.** Extract variables dict.

### 4a. Define the Task

Guide through the task instructions:

> "What should the AI do when executing this errand?
>
> Write clear, step-by-step instructions:
>
> - What actions to take
> - What to look for
> - What decisions to make
>
> This goes in the '## Task' section..."

**Wait for response.** Extract task instructions.

### 5a. Define Acceptance Criteria

Ask the user:

> "How do we know this errand is complete?
>
> List the conditions that must be met:
>
> - What outputs are expected?
> - What quality bar must be met?
> - Any specific deliverables?
>
> These become checkboxes in '## Acceptance Criteria'..."

**Wait for response.** Extract criteria list.

Continue to "Create the File" section.

---

## Capture Mode

### 2b. Review Conversation

Scan recent conversation for:

- **Repeatable pattern**: Is this something that could be scheduled again?
- **Inputs needed**: What information varied or would vary?
- **Steps taken**: What actions were performed?
- **Success criteria**: How was completion judged?

Present findings:

> "From our conversation, I identified this repeatable task:
>
> **Purpose**: {description}
>
> **Variables needed**:
>
> - {var1}: {desc1}
> - {var2}: {desc2}
>
> **Steps**:
>
> 1. {step 1}
> 2. {step 2}
> ...
>
> Is this what you want to capture? Anything to add or change?"

**Wait for confirmation.**

### 3b. Name the Errand

If not obvious, ask:

> "What should we call this errand?"

**Wait for response.**

Continue to "Create the File" section.

---

## Create the File

### 6. Check for Existing

```bash
layton errands
```

If errand name already exists, ask if user wants to overwrite or pick a different name.

### 7. Generate the Errand File

```bash
layton errands add <name>
```

This creates a file from `assets/templates/errand.md`. Edit it to replace the skeleton placeholders with the gathered/captured information:

- Set `name` and `description` in frontmatter
- Add variables to `variables:` section (name: description format)
- Fill in `## Task` with AI instructions
- Fill in `## Acceptance Criteria` with checkbox items
- Customize the `## Retrospective` proposed-updates table with relevant file targets (the errand itself, related rolodex cards, related protocols)

### 8. Validate and Confirm

Show the user the created file.

> "Here's the errand. Does this capture what you wanted?
>
> You can schedule it with:
>
> ```bash
> layton errands schedule <name> '{"var1": "value1"}'
> ```"

## Context Adaptation

- **If user says "turn this into an errand"**: Go directly to Capture Mode
- **If user says "create an errand for X"**: Go directly to Create Mode
- **If task is simple** (1-2 steps): Keep the errand concise
- **If task is complex**: Ensure clear structure in Task section
- **If similar errand exists**: Note and suggest extending or modifying

## Success Criteria

- [ ] Errand file created at `.layton/errands/<name>.md`
- [ ] Frontmatter has name, description, and variables
- [ ] Task section has clear AI instructions
- [ ] Acceptance criteria defined as checkboxes
- [ ] User confirms the errand looks correct
