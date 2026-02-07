---
name: gather
description: Aggregate data from all configured rolodex cards into a unified view
triggers:
  - gather data
  - collect rolodex data
  - aggregate cards
  - what's happening across my tools
---

## Objective

Read all rolodex cards from `.layton/rolodex/`, execute their documented commands, and aggregate the results into a unified view. This protocol is a building block for other protocols like morning-briefing and focus-suggestion.

## Steps

### 1. List Configured Cards

Get the list of configured rolodex cards:

```bash
layton rolodex
```

If no cards are configured, suggest running `layton rolodex --discover` and `layton rolodex add <name>`.

### 2. Iterate Over Rolodex Cards

For each card in `.layton/rolodex/`:

1. **Read the card file** to understand:
   - `## Commands` section: what to execute
   - `## What to Extract` section: what information matters
   - `## Key Metrics` section: important numbers to surface

2. **Execute commands** from the Commands section:
   - Run each command from the repo root
   - Capture stdout and stderr
   - Note exit codes

3. **Extract key information** using the guidance from "What to Extract":
   - Look for the specific data points mentioned
   - Parse structured output (JSON if available)
   - Handle missing or error states gracefully

### 3. Handle Failures Gracefully

When a card's command fails:

- Note the failure in results (don't stop gathering)
- Include the error message for context
- Continue with remaining cards
- Flag cards with errors in final summary

### 4. Aggregate Results

Organize gathered data by card:

```text
Gathered Data
=============

## GTD
- Inbox: 3 items
- Next Actions: 12 tasks
- Waiting For: 5 items
- Status: OK

## Errands
- Watching: 8 items
- Focus: "Implement card integration"
- Status: OK

## <Other Cards>
...
```

## Context Adaptation

- **If a card has no commands**: Skip it but note in output
- **If all commands fail for a card**: Mark as "unavailable" but continue
- **If JSON output available**: Prefer structured data over text parsing
- **If gathering takes too long**: Report partial results with note

## Success Criteria

- All configured cards are queried
- Failures don't stop the gather process
- Results are organized by card name
- Key metrics extracted per card file guidance
- Errors are clearly noted but don't crash the protocol
