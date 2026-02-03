<workflow name="schedule-bead">
<objective>Schedule a bead from a template for background execution.</objective>

<steps>
1. List available bead templates:
   ```bash
   layton beads
   ```

2. If user hasn't specified a template, show them the list and ask which to use

3. Gather any required variables from the user (check template's `variables` field)

4. Schedule the bead with variables as JSON:

   ```bash
   layton beads schedule <template-name> '{"var1": "value1", "var2": "value2"}'
   ```

   (The epic is auto-created on first use if not configured)

5. Confirm to user with the created bead ID
</steps>

<examples>
User: "Schedule a code review for src/auth.py"
```bash
# Check available templates
layton beads

# Schedule with variables

layton beads schedule code-review '{"file_path": "src/auth.py"}'

```

User: "I want to run the standup template"
```bash
layton beads schedule standup
```

</examples>

<success_criteria>

- Bead created with `scheduled` label
- Bead is a child of the configured epic
- User received confirmation with bead ID
</success_criteria>
</workflow>
