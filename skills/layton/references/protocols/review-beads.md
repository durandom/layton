<protocol name="review-errands">
<objective>Find and review completed errands that need human attention.</objective>

<steps>
1. Get orientation to see errands pending review:
   ```bash
   layton
   ```
   Look at the `errands_pending_review` field for closed errands with `needs-review` label

1. For each errand pending review:
   a. Show errand details:

      ```bash
      bd show <errand-id>
      ```

   b. Show comments (contains executor's findings):

      ```bash
      bd comments <errand-id>
      ```

1. After reviewing, either:
   - Accept the work and remove the review label:

     ```bash
     bd label remove <errand-id> needs-review
     ```

   - Request changes by reopening:

     ```bash
     bd open <errand-id>
     bd comments add <errand-id> "Changes needed: <feedback>"
     ```

1. Summarize review status to user
</steps>

<examples>
User: "What errands need my review?"
```bash
# Get orientation to see pending reviews
layton

# Show details for each pending errand

bd show <errand-id>
bd comments <errand-id>

```text

User: "Accept errand abc-123"
```bash
bd label remove abc-123 needs-review
```text

</examples>

<success_criteria>

- User informed of all errands pending review
- Each reviewed errand either has `needs-review` removed or is reopened with feedback
</success_criteria>
</protocol>
