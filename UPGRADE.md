# Upgrading to v1.0.0 — Secretary Metaphor

Layton's three primitives have been renamed:

| Before | After | What it is |
| --- | --- | --- |
| **skill** | **rolodex card** | How to query an external tool |
| **workflow** | **protocol** | Interactive multi-step process |
| **bead template** | **errand** | Autonomous background task |

## Step 1: Rename Directories

```bash
cd <your-project>
mv .layton/skills/    .layton/rolodex/
mv .layton/workflows/ .layton/protocols/
mv .layton/beads/     .layton/errands/
```

The `.beads/` directory (managed by `bd`) is **unchanged** — only `.layton/beads/` moves.

## Step 2: Update Internal References in Your Files

Your `.layton/` markdown files likely contain path references and terminology that need updating. Here's what to look for:

### Path references

Search and replace these paths in all `.layton/` files:

| Find | Replace |
| --- | --- |
| `.layton/skills/` | `.layton/rolodex/` |
| `.layton/workflows/` | `.layton/protocols/` |
| `.layton/beads/` | `.layton/errands/` |

**Typical locations** (based on real-world usage):

- **Errands** referencing protocols: e.g. `"Follow: .layton/workflows/process-starred-emails.md"` → `"Follow: .layton/protocols/process-starred-emails.md"`
- **Protocols** referencing rolodex cards: e.g. `"Read the skill file from .layton/skills/calendar.md"` → `"Read the rolodex card from .layton/rolodex/calendar.md"`
- **Protocols** referencing errands: e.g. `"Read the bead template from .layton/beads/<name>.md"` → `"Read the errand from .layton/errands/<name>.md"`
- **Skill-file mapping tables** inside protocols that list `.layton/skills/<name>.md` paths

Quick way to find them all:

```bash
grep -rn '\.layton/\(skills\|workflows\|beads\)/' .layton/
```

### Terminology in prose

These are less critical (the files still work), but worth cleaning up:

| Find | Replace with |
| --- | --- |
| "skill card" / "skill file" | "rolodex card" |
| "bead template" | "errand" |
| "workflow" (as Layton primitive) | "protocol" |
| "Skill File" (in tables) | "Rolodex Card" |
| "Bead Template" (in tables) | "Errand" |

Note: "workflow" in generic English prose (e.g. "the orchestrating workflow handles bead lifecycle") may be fine to leave as-is. Only rename when it refers to Layton's `.layton/protocols/` primitive.

## Step 3: Update config.json

The config file itself **does not need changes**. The `beads.epic` key is still correct — it refers to `bd` beads, not Layton's errand primitive.

## Step 4: Update Project Instructions

If your `CLAUDE.md` or `AGENTS.md` references Layton primitives, update them:

```diff
-Run `layton skills` to list available integrations.
+Run `layton rolodex` to list available integrations.

-See `.layton/workflows/` for available workflows.
+See `.layton/protocols/` for available protocols.
```

## Step 5: CLI Command Changes

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

## Verification

```bash
layton doctor        # Health check — should show all green
layton rolodex       # Should list your cards (calendar, gmail, gtd, etc.)
layton protocols     # Should list your protocols (morning-briefing, etc.)
layton errands       # Should list your errands (calendar-gather, etc.)
```

Then confirm no stale paths remain:

```bash
grep -rn '\.layton/\(skills\|workflows\|beads\)/' .layton/
```

This should return no results.
