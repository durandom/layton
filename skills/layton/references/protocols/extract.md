---
name: extract
description: Extract or refine a primitive (rolodex card, protocol, errand) from conversation context
triggers:
  - extract
  - extract rolodex
  - extract protocol
  - extract errand
  - capture this
  - refine card
  - update card from context
  - that should be a card
  - that should be a protocol
  - that should be an errand
---

<philosophy>
Layton improves by noticing gaps and friction — not by chasing perfection.

- Extract when something is **genuinely missing** or **demonstrably wrong**.
- Don't polish for the sake of polishing.
- One good refinement beats three speculative new primitives.
- Prefer refining an existing primitive over creating a new one.
- **One extraction per conversation** unless the user asks for more.
- Never auto-apply — always show, always ask.
</philosophy>

<required_reading>
**Read the authoring guide for the target primitive type:**

- Rolodex card → `references/rolodex-authoring.md`
- Protocol → `references/protocol-authoring.md`
- Errand → `references/errand-authoring.md`
</required_reading>

## Objective

Capture knowledge from the current conversation as a new or improved primitive. This protocol handles two paths:

- **Create** — Something new was done that has no corresponding primitive yet
- **Refine** — Something was done that reveals a gap or improvement in an existing primitive

This can be triggered by the user ("extract a rolodex card") or suggested by Layton when it notices a pattern worth capturing.

---

## When to Suggest Extraction

Layton may suggest running this protocol when it notices:

| Signal | Primitive | Example |
|--------|-----------|---------|
| Queried an external system with no rolodex card | Rolodex card | "I had to figure out how to query PagerDuty from scratch" |
| Rolodex card was missing a command or section we needed | Rolodex card | "The gmail card didn't cover filtering by label" |
| Followed a multi-step process that could be repeatable | Protocol | "We just did a 4-step triage flow manually" |
| Ran a task that could be scheduled autonomously | Errand | "This review could run every Friday unattended" |
| An errand's retrospective flagged a change to another primitive | Any | Retrospective proposed-updates table has entries |

**When suggesting, be brief:**

> "We just queried PagerDuty manually — there's no rolodex card for it. Want me to extract one from what we did?"

If the user declines, move on. Don't re-suggest in the same session.

---

## Steps

### 1. Identify Type and Mode

If the user specified a type (e.g., "extract rolodex"), skip to step 2.

Otherwise, analyze the conversation and propose:

> "Based on what we just did, I'd suggest extracting a **{type}**:
>
> - **{brief description of what to capture}**
>
> Does that sound right, or did you have something else in mind?"

**Wait for response.**

### 2. Check for Existing Primitive

```bash
layton rolodex        # if type is rolodex
layton protocols      # if type is protocol
layton errands        # if type is errand
```

Scan the list for a primitive that covers the same domain or workflow.

- **Match found** → Refine path (step 3a)
- **No match** → Create path (step 3b)

Present your finding:

> "There's already a `{name}` card that covers {domain}. I think we should **refine** it rather than create a new one."

or:

> "Nothing covers this yet. I'll **create** a new {type}."

---

## Refine Path

### 3a. Read and Diff

Read the existing primitive file. Compare it against what happened in the conversation.

Identify specific gaps:

- Missing commands or steps
- Outdated instructions
- Missing metrics, extraction criteria, or variables
- Missing context adaptations or edge cases

Draft the proposed changes as a **concrete diff** — show exactly what lines change and why.

> "Here's what I'd update in `.layton/rolodex/{name}.md`:
>
> **Add to `## Commands`:**
> ```
> # Filter by label
> mcp-cli google_workspace/search_gmail_messages '{"query": "is:starred label:urgent"}'
> ```
>
> **Add to `## What to Extract`:**
> - Label-filtered counts (when user asks about specific categories)
>
> Want me to apply this?"

**Wait for approval.** Apply only after explicit yes.

Continue to step 4.

---

## Create Path

### 3b. Draft from Conversation Context

Scan the conversation for:

- **Rolodex card**: Commands run, output parsed, data extracted, key metrics identified
- **Protocol**: Sequence of steps, decisions made, context adaptations, success conditions
- **Errand**: Repeatable task, required variables, acceptance criteria, completion steps

Draft the full primitive following the authoring guide for that type.

Present the draft:

> "Here's the draft `{name}` {type}:
>
> ```markdown
> {full file content}
> ```
>
> Want me to save this?"

**Wait for approval.**

If approved, create the file:

```bash
layton {type} add {name}
```

Then overwrite the skeleton with the drafted content.

Continue to step 4.

---

### 4. Validate

After applying (refine) or saving (create), verify:

- [ ] Frontmatter fields are complete and valid
- [ ] No skeleton placeholders remain
- [ ] Commands are executable from repo root
- [ ] Content matches the authoring guide for this type

If validation fails, fix and show the correction.

---

## Context Adaptation

| Context | Adaptation |
|---------|------------|
| User explicitly asked to extract | Skip the suggestion framing, go directly to type identification |
| Layton is suggesting | Be brief, don't oversell. One sentence + "Want me to?" |
| Conversation had a clear single workflow | Propose that specific extraction, don't ask open-ended questions |
| Conversation touched multiple potential extractions | Pick the highest-value one. Mention the others only if asked |
| Errand retrospective flagged updates | Propose the specific changes from the proposed-updates table |

## Success Criteria

- [ ] Correct primitive type identified (or confirmed with user)
- [ ] Existing primitives checked before creating new ones
- [ ] Draft or diff presented for review before any changes
- [ ] User explicitly approved before file was modified
- [ ] Result validates against the authoring guide
