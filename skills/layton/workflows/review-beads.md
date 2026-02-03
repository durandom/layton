<workflow name="review-beads">
<objective>Find and review completed beads that need human attention.</objective>

<steps>
1. Get orientation to see beads pending review:
   ```bash
   layton
   ```
   Look at the `beads_pending_review` field for closed beads with `needs-review` label

2. For each bead pending review:
   a. Show bead details:

      ```bash
      bd show <bead-id>
      ```

   b. Show comments (contains executor's findings):

      ```bash
      bd comments <bead-id>
      ```

3. After reviewing, either:
   - Accept the work and remove the review label:

     ```bash
     bd label remove <bead-id> needs-review
     ```

   - Request changes by reopening:

     ```bash
     bd open <bead-id>
     bd comments add <bead-id> "Changes needed: <feedback>"
     ```

4. Summarize review status to user
</steps>

<examples>
User: "What beads need my review?"
```bash
# Get orientation to see pending reviews
layton

# Show details for each pending bead

bd show <bead-id>
bd comments <bead-id>

```

User: "Accept bead abc-123"
```bash
bd label remove abc-123 needs-review
```

</examples>

<success_criteria>

- User informed of all beads pending review
- Each reviewed bead either has `needs-review` removed or is reopened with feedback
</success_criteria>
</workflow>
