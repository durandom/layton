## ADDED Requirements

### Requirement: Focus protocol is an example

The focus protocol SHALL be an example protocol at `skills/layton/examples/focus-suggestion.md`.

#### Scenario: Example location

- **WHEN** user wants focus suggestions
- **THEN** they SHALL first create a protocol using `layton protocols add focus-suggestion`
- **AND** they MAY reference `skills/layton/examples/focus-suggestion.md` for guidance

---

### Requirement: Focus protocol considers context

The focus protocol SHALL consider temporal and energy context.

#### Scenario: Temporal context

- **WHEN** AI follows a focus protocol
- **THEN** it SHALL run `layton context` to understand time of day and work hours

#### Scenario: Energy matching

- **WHEN** suggesting focus during morning work hours
- **THEN** AI SHALL prefer high-energy tasks
- **WHEN** suggesting focus during evening or low-energy periods
- **THEN** AI SHALL prefer low-energy tasks

---

### Requirement: Focus protocol queries available work

The focus protocol SHALL query available tasks from rolodex cards.

#### Scenario: GTD integration

- **WHEN** user has `.layton/rolodex/gtd.md`
- **THEN** focus protocol SHALL query GTD for active tasks
- **AND** it SHALL consider task context labels (focus, async, meetings)

#### Scenario: Beads integration

- **WHEN** AI follows a focus protocol
- **THEN** it SHALL check `bd list --label watching --json` for tracked items

---

### Requirement: Focus protocol presents options

The focus protocol SHALL present focus options to user.

#### Scenario: Option presentation

- **WHEN** AI has gathered available work
- **THEN** it SHALL present 2-3 recommended options
- **AND** each option SHALL include rationale (why this task, why now)

#### Scenario: User selection

- **WHEN** user selects a focus option
- **THEN** AI SHALL use the set-focus protocol to set it
