---
name: beads-commands
description: Command reference for the bd CLI used by Layton for state operations
---

<overview>
Command reference for the `bd` (errands) CLI used by Layton for state operations.
</overview>

<creating_errands>
**Track external item:**

```bash
bd create "JIRA-1234: blocking release" -t task -p 2 -l watching,jira,layton --json
```

Output:

```json
{"id": "beads-abc", "title": "JIRA-1234: blocking release", "labels": ["watching", "jira", "layton"]}
```

</creating_errands>

<querying_errands>

| Query | Command |
| --- | --- |
| Watched items | `bd list --label watching --json` |
| Current focus | `bd list --label focus --json` |
| All Layton errands | `bd list --label layton --json` |
| Ready work | `bd ready --json` |

</querying_errands>

<updating_errands>
**Add label:**

```bash
bd update <id> --add-label <label> --json
```

**Remove label:**

```bash
bd update <id> --remove-label <label> --json
```

</updating_errands>

<closing_errands>

```bash
bd close <id> --reason "..." --json
```

</closing_errands>

<label_conventions>

| Label | Purpose |
| --- | --- |
| `layton` | Namespace - all Layton-managed errands |
| `watching` | Items user wants tracked |
| `focus` | Current work item (only one) |
| `jira`, `github`, etc. | Source system |

</label_conventions>
