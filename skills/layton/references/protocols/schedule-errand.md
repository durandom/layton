<protocol name="schedule-errand">
<objective>Schedule an errand from a template for background execution.</objective>

<steps>
1. List available errands:
   ```bash
   layton errands
   ```

1. If user hasn't specified an errand, show them the list and ask which to use

1. Gather any required variables from the user (check errand's `variables` field)

1. Schedule the errand with variables as JSON:

   ```bash
   layton errands schedule <errand-name> '{"var1": "value1", "var2": "value2"}'
   ```

   (The epic is auto-created on first use if not configured)

1. Confirm to user with the created errand ID
</steps>

<examples>
User: "Schedule a code review for src/auth.py"
```bash
# Check available errands
layton errands

# Schedule with variables

layton errands schedule code-review '{"file_path": "src/auth.py"}'

```text

User: "I want to run the standup errand"
```bash
layton errands schedule standup
```text

</examples>

<success_criteria>

- Errand created with `scheduled` label
- Errand is a child of the configured epic
- User received confirmation with errand ID
</success_criteria>
</protocol>
