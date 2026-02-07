<protocol name="run-errand">
<objective>Execute errands via background Task agents for autonomous completion.</objective>

<steps>
1. Schedule the errand (if not already scheduled):
   ```bash
   $LAYTON errands run <errand-name> '{"var1": "value1"}'
   ```
   Returns `{bead_id, title}` — the prompt is NOT included (token efficiency).

   If the errand is already scheduled (e.g., from orientation `beads_scheduled`), skip this step — you already have the `bead_id`.

2. Spawn a Task agent to execute it:

   Use the Task tool with `subagent_type: "general-purpose"` and this bootstrap prompt:

   > You are an errand executor. Your bead ID is {bead_id}.
   > Run `$LAYTON errands prompt {bead_id}` to get your full instructions, then follow them exactly.
   > The LAYTON CLI is at: `$LAYTON`

   **Critical**: Include the `$LAYTON` CLI path in the subagent prompt — the subagent has no other way to discover it.

   For fire-and-forget execution, set `run_in_background: true`.

3. Post-flight check (after agent returns or when checking background results):
   ```bash
   bd show <bead-id> --json
   ```
   If the bead is not closed, escalate:
   ```bash
   bd label add <bead-id> needs-human
   ```

</steps>

<variants>

**Already-scheduled beads** (from orientation):
Skip step 1. The `errands.queue.scheduled` array from `$LAYTON` output already contains bead IDs. Proceed directly to step 2.

**Batch execution**:
Iterate over `beads_scheduled` from orientation output. Spawn one Task agent per bead, all with `run_in_background: true` for parallel execution.

</variants>

<examples>
User: "Run the code-review errand for src/auth.py"
```bash
# Schedule
$LAYTON errands run code-review '{"file_path": "src/auth.py"}'
# → {"bead_id": "abc-123", "title": "[code-review] Review code for issues"}

# Spawn agent via Task tool:
#   prompt: "You are an errand executor. Your bead ID is abc-123.
#            Run `/path/to/layton errands prompt abc-123` for instructions."
#   subagent_type: general-purpose

# Post-flight
bd show abc-123 --json
```

User: "Execute all scheduled errands"
```bash
# Get scheduled beads from orientation
$LAYTON
# → errands.queue.scheduled: [{id: "abc-123", ...}, {id: "def-456", ...}]

# Spawn one Task agent per bead (all in background)
# Task(general-purpose, "Executor for abc-123. Run `$LAYTON errands prompt abc-123`...", run_in_background: true)
# Task(general-purpose, "Executor for def-456. Run `$LAYTON errands prompt def-456`...", run_in_background: true)
```

</examples>

<success_criteria>

- Errand bead created with `scheduled` label
- Task agent spawned with correct bead ID and LAYTON path
- Agent fetches its own instructions via `errands prompt` (transitions to `in-progress`)
- On completion: `in-progress` label removed, bead closed with `needs-review` label
- On failure: bead tagged `needs-human` in post-flight check
</success_criteria>
</protocol>
