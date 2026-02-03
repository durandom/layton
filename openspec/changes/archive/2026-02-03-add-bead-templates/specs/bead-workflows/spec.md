## ADDED Requirements

### Requirement: Schedule bead workflow

A workflow SHALL guide users through scheduling beads from templates.

#### Scenario: Workflow file exists

- **WHEN** Layton is installed
- **THEN** `skills/layton/workflows/schedule-bead.md` SHALL exist
- **AND** workflow SHALL include steps for listing templates, selecting one, providing variables, and scheduling

#### Scenario: Workflow references beads CLI

- **WHEN** user follows schedule-bead workflow
- **THEN** workflow SHALL reference `layton beads` to list available templates
- **AND** SHALL reference `layton beads schedule` with JSON variable example

---

### Requirement: Review beads workflow

A workflow SHALL guide users through reviewing completed beads.

#### Scenario: Workflow file exists (review)

- **WHEN** Layton is installed
- **THEN** `skills/layton/workflows/review-beads.md` SHALL exist
- **AND** workflow SHALL include steps for finding beads pending review and processing them

#### Scenario: Workflow uses orientation

- **WHEN** user follows review-beads workflow
- **THEN** workflow SHALL reference `layton` orientation to find `beads_pending_review`
- **AND** SHALL include steps for reviewing findings, approving, and removing `needs-review` label

---

### Requirement: SKILL.md integration

The main skill file SHALL reference bead workflows and CLI commands.

#### Scenario: Routing includes bead intents

- **WHEN** SKILL.md routing section is read
- **THEN** it SHALL include routing for "schedule bead" intent to `workflows/schedule-bead.md`
- **AND** SHALL include routing for "review beads" intent to `workflows/review-beads.md`

#### Scenario: CLI commands include beads

- **WHEN** SKILL.md cli_commands section is read
- **THEN** it SHALL document `$LAYTON beads` command and subcommands

#### Scenario: Workflows index includes bead workflows

- **WHEN** SKILL.md workflows_index section is read
- **THEN** it SHALL list schedule-bead.md and review-beads.md with descriptions
