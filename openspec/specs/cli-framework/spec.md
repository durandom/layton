## MODIFIED Requirements

### Requirement: No-arg invocation

Running `layton` with no arguments SHALL return full AI orientation (doctor + rolodex + protocols + errands).

#### Scenario: Layton with no args returns orientation

- **WHEN** user runs `layton` with no arguments
- **THEN** CLI SHALL return JSON with `checks` (doctor output), `rolodex` (from `.layton/rolodex/`), `protocols` (from `.layton/protocols/`), and `errands` (from `.layton/errands/`)
- **AND** output SHALL include `next_steps` for common actions

#### Scenario: Orientation includes doctor checks

- **WHEN** user runs `layton` with no arguments
- **THEN** `checks` field SHALL contain all doctor check results (beads CLI, config validity)

#### Scenario: Orientation includes rolodex inventory

- **WHEN** user runs `layton` with no arguments
- **THEN** `rolodex` field SHALL be an array of known rolodex cards
- **AND** each card SHALL include `name` and `description` from frontmatter

#### Scenario: Orientation includes protocols inventory

- **WHEN** user runs `layton` with no arguments
- **THEN** `protocols` field SHALL be an array of user protocols
- **AND** each protocol SHALL include `name`, `description`, and `triggers` from frontmatter

#### Scenario: Orientation includes errands

- **WHEN** user runs `layton` with no arguments
- **THEN** `errands` field SHALL be an array of errands from `.layton/errands/`
- **AND** each errand SHALL include `name`, `description`, and `variables` from frontmatter

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
