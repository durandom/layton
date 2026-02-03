## MODIFIED Requirements

### Requirement: No-arg invocation

Running `layton` with no arguments SHALL return full AI orientation (doctor + skills + workflows + beads).

#### Scenario: Layton with no args returns orientation

- **WHEN** user runs `layton` with no arguments
- **THEN** CLI SHALL return JSON with `checks` (doctor output), `skills` (from `.layton/skills/`), `workflows` (from `.layton/workflows/`), and `beads` (from `.layton/beads/`)
- **AND** output SHALL include `next_steps` for common actions

#### Scenario: Orientation includes doctor checks

- **WHEN** user runs `layton` with no arguments
- **THEN** `checks` field SHALL contain all doctor check results (beads CLI, config validity)

#### Scenario: Orientation includes skills inventory

- **WHEN** user runs `layton` with no arguments
- **THEN** `skills` field SHALL be an array of known skills
- **AND** each skill SHALL include `name` and `description` from frontmatter

#### Scenario: Orientation includes workflows inventory

- **WHEN** user runs `layton` with no arguments
- **THEN** `workflows` field SHALL be an array of user workflows
- **AND** each workflow SHALL include `name`, `description`, and `triggers` from frontmatter

#### Scenario: Orientation includes bead templates

- **WHEN** user runs `layton` with no arguments
- **THEN** `bead_templates` field SHALL be an array of bead templates from `.layton/beads/`
- **AND** each template SHALL include `name`, `description`, and `variables` from frontmatter

#### Scenario: Orientation includes beads pending review

- **WHEN** user runs `layton` with no arguments
- **THEN** `beads_pending_review` field SHALL be an array of beads with `needs-review` label and closed status
- **AND** each bead SHALL include `id`, `title`, and `closed_at` from bd
- **AND** if no beads pending review, field SHALL be empty array

#### Scenario: Orientation includes beads scheduled

- **WHEN** user runs `layton` with no arguments
- **THEN** `beads_scheduled` field SHALL be an array of beads with `scheduled` label and open status
- **AND** each bead SHALL include `id`, `title`, and `created_at` from bd
- **AND** if no beads scheduled, field SHALL be empty array

#### Scenario: Layton config with no subcommand

- **WHEN** user runs `layton config` with no subcommand
- **THEN** CLI SHALL run `layton config show` (safe, read-only)
- **AND** if config missing, SHALL suggest `layton config init`
