## ADDED Requirements

### Requirement: Schedule bead protocol

A protocol SHALL guide users through scheduling beads from errands.

#### Scenario: Protocol file exists

- **WHEN** Layton is installed
- **THEN** `skills/layton/protocols/schedule-bead.md` SHALL exist
- **AND** protocol SHALL include steps for listing errands, selecting one, providing variables, and scheduling

#### Scenario: Protocol references errands CLI

- **WHEN** user follows schedule-bead protocol
- **THEN** protocol SHALL reference `layton errands` to list available errands
- **AND** SHALL reference `layton errands schedule` with JSON variable example

---

### Requirement: Review beads protocol

A protocol SHALL guide users through reviewing completed beads.

#### Scenario: Protocol file exists (review)

- **WHEN** Layton is installed
- **THEN** `skills/layton/protocols/review-beads.md` SHALL exist
- **AND** protocol SHALL include steps for finding beads pending review and processing them

#### Scenario: Protocol uses orientation

- **WHEN** user follows review-beads protocol
- **THEN** protocol SHALL reference `layton` orientation to find `beads_pending_review`
- **AND** SHALL include steps for reviewing findings, approving, and removing `needs-review` label

---

### Requirement: SKILL.md integration

The main skill file SHALL reference bead protocols and errand CLI commands.

#### Scenario: Routing includes bead intents

- **WHEN** SKILL.md routing section is read
- **THEN** it SHALL include routing for "schedule bead" intent to `protocols/schedule-bead.md`
- **AND** SHALL include routing for "review beads" intent to `protocols/review-beads.md`

#### Scenario: CLI commands include errands

- **WHEN** SKILL.md cli_commands section is read
- **THEN** it SHALL document `$LAYTON errands` command and subcommands

#### Scenario: Protocols index includes bead protocols

- **WHEN** SKILL.md protocols_index section is read
- **THEN** it SHALL list schedule-bead.md and review-beads.md with descriptions
