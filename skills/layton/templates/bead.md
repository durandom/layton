---
name: {name}
description: <what this bead accomplishes when scheduled>
variables:
  # variable_name: description of what this variable is for
---

## Task

<!-- AI-readable instructions for completing this bead -->

## Acceptance Criteria

<!-- Conditions that must be met for this bead to be considered complete -->

- [ ]
- [ ]

## When Complete

<!-- Standard closing instructions for the executor -->

1. Add your findings as comments:

   ```bash
   bd comments add "## Summary\n\n<your findings>"
   ```

2. Close the bead and signal for review:

   ```bash
   bd close --add-label needs-review
   ```

   The `needs-review` label signals that a human should review the completed work.
