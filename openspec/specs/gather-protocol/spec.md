## ADDED Requirements

### Requirement: Gather protocol is an example

The gather protocol SHALL be an example protocol at `skills/layton/examples/gather.md`.

#### Scenario: Example location

- **WHEN** user wants to gather data from rolodex cards
- **THEN** they SHALL first create a protocol using `layton protocols add gather`
- **AND** they MAY reference `skills/layton/examples/gather.md` for guidance

---

### Requirement: Gather reads rolodex cards

The gather protocol SHALL read rolodex cards from `.layton/rolodex/`.

#### Scenario: Rolodex card iteration

- **WHEN** AI follows a gather protocol
- **THEN** it SHALL read each file in `.layton/rolodex/`
- **AND** for each card, it SHALL follow the documented commands

---

### Requirement: Gather executes rolodex card commands

The gather protocol SHALL execute commands documented in rolodex cards.

#### Scenario: Command execution

- **WHEN** AI reads a rolodex card's `## Commands` section
- **THEN** it SHALL execute those commands
- **AND** it SHALL capture the output for aggregation

#### Scenario: Command failure handling

- **WHEN** a rolodex card command fails (non-zero exit or error)
- **THEN** AI SHALL note the failure in aggregated results
- **AND** AI SHALL continue with remaining cards

---

### Requirement: Gather extracts key information

The gather protocol SHALL extract information per rolodex card guidance.

#### Scenario: Extraction guidance

- **WHEN** a rolodex card has a `## What to Extract` section
- **THEN** AI SHALL use that guidance to identify key information from output
- **AND** AI SHALL aggregate extracted information for other protocols

---

### Requirement: Gather aggregates results

The gather protocol SHALL produce aggregated results for consumption.

#### Scenario: Aggregation structure

- **WHEN** AI completes gathering from all rolodex cards
- **THEN** results SHALL be organized by card name
- **AND** results SHALL include extracted key information per card
