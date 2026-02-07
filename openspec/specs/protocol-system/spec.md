## ADDED Requirements

### Requirement: Protocol file format

Protocol files SHALL use YAML frontmatter with markdown body, stored in `.layton/protocols/<name>.md`.

#### Scenario: Valid protocol file structure

- **WHEN** a protocol file exists at `.layton/protocols/morning-briefing.md`
- **THEN** it SHALL have YAML frontmatter with `name`, `description`, and `triggers` fields
- **AND** the markdown body SHALL contain AI-readable instructions

#### Scenario: Frontmatter fields

- **WHEN** parsing a protocol file's frontmatter
- **THEN** `name` SHALL be a lowercase identifier matching the filename (without `.md`)
- **AND** `description` SHALL describe what this protocol does
- **AND** `triggers` SHALL be an array of phrases that activate this protocol

---

### Requirement: Protocol file template

The CLI SHALL provide a template for bootstrapping new protocol files.

#### Scenario: Template content

- **WHEN** `layton protocols add <name>` is run
- **THEN** CLI SHALL create `.layton/protocols/<name>.md` with this template:

```markdown
---
name: <name>
description: <what this protocol does>
triggers:
  - <phrase that activates this protocol>
  - <another trigger phrase>
---

## Objective

<!-- What this protocol accomplishes -->

## Steps

<!-- AI-readable instructions for executing this protocol -->

1. Get context:
   ```bash
   layton context
```text

1. <!-- Next step -->

1. <!-- Next step -->

## Context Adaptation

<!-- How to adapt based on time/context -->

- If morning + work hours: ...
- If evening: ...

## Success Criteria

<!-- How to know the protocol completed successfully -->

- [ ]
- [ ]

```text

#### Scenario: Template sections purpose

- **WHEN** AI reads a protocol file
- **THEN** `## Objective` SHALL describe the goal of the protocol
- **AND** `## Steps` SHALL contain numbered AI instructions with commands
- **AND** `## Context Adaptation` SHALL guide behavior based on temporal context
- **AND** `## Success Criteria` SHALL define completion conditions

#### Scenario: Template does not overwrite

- **WHEN** `layton protocols add <name>` is run AND `.layton/protocols/<name>.md` exists
- **THEN** CLI SHALL return error with code `PROTOCOL_EXISTS`
- **AND** error message SHALL suggest reviewing existing file

---

### Requirement: List user protocols

The CLI SHALL list protocols from `.layton/protocols/`.

#### Scenario: List with JSON output

- **WHEN** `layton protocols` is run
- **THEN** output SHALL be JSON with `success` and `protocols` array
- **AND** each protocol SHALL include `name`, `description`, `triggers` from frontmatter

#### Scenario: Empty protocols directory

- **WHEN** `layton protocols` is run AND `.layton/protocols/` is empty or missing
- **THEN** output SHALL have empty `protocols` array
- **AND** `next_steps` SHALL suggest `layton protocols add`

---

### Requirement: Protocols directory creation

The CLI SHALL create `.layton/protocols/` directory when needed.

#### Scenario: Auto-create on add

- **WHEN** `layton protocols add <name>` is run AND `.layton/protocols/` doesn't exist
- **THEN** CLI SHALL create the directory before creating the protocol file

---

### Requirement: Example protocols

Example protocols SHALL exist in `skills/layton/examples/` as reference patterns.

#### Scenario: Examples are reference only

- **WHEN** AI needs to help user create a protocol
- **THEN** AI MAY read examples from `skills/layton/examples/` for inspiration
- **AND** AI SHALL use `layton protocols add` to create user's protocol (not copy examples)
