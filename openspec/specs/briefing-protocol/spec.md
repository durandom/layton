## ADDED Requirements

### Requirement: Briefing protocol is an example

The briefing protocol SHALL be an example protocol at `skills/layton/references/examples/morning-briefing.md`.

#### Scenario: Example location

- **WHEN** user wants morning briefings
- **THEN** they SHALL first create a protocol using `layton protocols add morning-briefing`
- **AND** they MAY reference `skills/layton/references/examples/morning-briefing.md` for guidance

---

### Requirement: Briefing combines multiple data sources

The briefing protocol SHALL combine temporal context, beads state, and rolodex card data.

#### Scenario: Temporal context

- **WHEN** AI follows a briefing protocol
- **THEN** it SHALL run `layton context` to get time of day, work hours, timezone

#### Scenario: Beads state

- **WHEN** AI follows a briefing protocol
- **THEN** it SHALL run `bd list --label watching --json` to get attention items
- **AND** it SHALL run `bd list --label focus --json` to get current focus

#### Scenario: Rolodex card data

- **WHEN** AI follows a briefing protocol AND user has a gather protocol
- **THEN** it SHALL follow the gather protocol to collect rolodex card data

---

### Requirement: Briefing adapts to context

The briefing protocol SHALL adapt output based on temporal context.

#### Scenario: Morning work hours

- **WHEN** `time_of_day` is `morning` AND `work_hours` is `true`
- **THEN** briefing SHALL be comprehensive with focus suggestions

#### Scenario: Evening outside work hours

- **WHEN** `time_of_day` is `evening` AND `work_hours` is `false`
- **THEN** briefing SHALL be brief summary only

---

### Requirement: Briefing uses persona

The briefing protocol SHALL use the Elizabeth Layton persona.

#### Scenario: Persona voice

- **WHEN** AI delivers a briefing
- **THEN** it SHALL use tone and style from `references/persona.md`

---

### Requirement: Briefing prioritizes information

The briefing protocol SHALL prioritize information appropriately.

#### Scenario: Priority order

- **WHEN** AI synthesizes a briefing
- **THEN** it SHALL present: current focus first, then attention items, then suggestions
