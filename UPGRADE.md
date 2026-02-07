# Upgrading to the Secretary Metaphor

Layton's three primitives have been renamed to align with the secretary metaphor:

| Before | After | What it is |
| --- | --- | --- |
| **skill** | **rolodex card** | How to query an external tool |
| **workflow** | **protocol** | Interactive multi-step process |
| **bead template** | **errand** | Autonomous background task |

## Directory Renames

Rename your `.layton/` directories:

```bash
mv .layton/skills/    .layton/rolodex/
mv .layton/workflows/ .layton/protocols/
mv .layton/beads/     .layton/errands/      # template directory only
```

No changes are needed inside `.beads/` (the beads state directory used by `bd`).

## CLI Commands

| Before | After |
| --- | --- |
| `layton skills` | `layton rolodex` |
| `layton skills add <name>` | `layton rolodex add <name>` |
| `layton skills --discover` | `layton rolodex --discover` |
| `layton workflows` | `layton protocols` |
| `layton workflows add <name>` | `layton protocols add <name>` |
| `layton beads` | `layton errands` |
| `layton beads add <name>` | `layton errands add <name>` |
| `layton beads schedule <name>` | `layton errands schedule <name>` |
| `layton beads epic get/set` | `layton errands epic get/set` |

## File Content Updates

Inside your `.layton/` markdown files, update any references:

1. **Directory paths** in instructions:
   - `.layton/skills/` → `.layton/rolodex/`
   - `.layton/workflows/` → `.layton/protocols/`

2. **Terminology** in prose:
   - "skill card" → "rolodex card"
   - "workflow" → "protocol" (when referring to Layton's primitive)
   - "bead template" → "errand"

## Project Instructions

If your `CLAUDE.md` or `AGENTS.md` references Layton primitives, update them:

```diff
-Layton manages skills, workflows, and bead templates.
+Layton manages rolodex cards, protocols, and errands.

-Run `layton skills` to list available integrations.
+Run `layton rolodex` to list available integrations.

-See `.layton/workflows/` for available workflows.
+See `.layton/protocols/` for available protocols.
```

## Verification

After upgrading, run:

```bash
layton doctor        # Health check — should show all green
layton rolodex       # Lists your cards
layton protocols     # Lists your protocols
layton errands       # Lists your errands
```
