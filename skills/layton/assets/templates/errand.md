---
name: {name}
description: <what this errand accomplishes when scheduled>
variables:
  # variable_name: description of what this variable is for
---

## Task

<!-- AI-readable instructions for completing this errand -->

## Acceptance Criteria

<!-- Conditions that must be met for this errand to be considered complete -->

- [ ]
- [ ]

## When Complete

<!-- Standard closing instructions for the executor -->

1. Add your findings as comments:

   ```bash
   bd comments add "## Summary\n\n<your findings>"
   ```

2. Close the errand:

   ```bash
   bd close
   ```

3. Signal for review:

   ```bash
   bd label add needs-review
   ```

   The `needs-review` label signals that a human should review the completed work.

## Retrospective

**During execution**, whenever a step fails or produces unexpected results, immediately add a comment:

```bash
bd comments add <bead-id> "## Issue: <brief description>

**Step:** <which step failed>
**Expected:** <what should have happened>
**Actual:** <what actually happened>
**Workaround:** <how you recovered, if applicable>"
```

**After closing**, always add a retrospective comment — even if everything went smoothly:

```bash
bd comments add <bead-id> "## Retrospective

**Status:** clean run | had issues
**Issues encountered:** N

**Proposed updates:**
| Target | File | Change | Reason |
|--------|------|--------|--------|
| errand | .layton/errands/{name}.md | ... | ... |
| rolodex | ... | ... | ... |
| protocol | ... | ... | ... |

**Notes:**
- <observations, edge cases, things that were confusing or slow>"
```

If no updates are needed, write `None` in the table. The point is to always leave a trace.
