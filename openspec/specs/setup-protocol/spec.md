## ADDED Requirements

### Requirement: Setup protocol location

The setup protocol SHALL be a core skill protocol at `skills/layton/references/protocols/setup.md`.

#### Scenario: Protocol exists in skill

- **WHEN** Layton skill is loaded
- **THEN** `skills/layton/references/protocols/setup.md` SHALL exist
- **AND** it SHALL be an AI-readable protocol document

---

### Requirement: Setup gathers user information

The setup protocol SHALL interactively gather user information.

#### Scenario: Required information

- **WHEN** AI follows the setup protocol
- **THEN** it SHALL prompt for: user name, email, timezone, work hours start, work hours end, work days

#### Scenario: Persist via config

- **WHEN** user provides information during setup
- **THEN** AI SHALL use `layton config set` to persist each value
- **AND** values SHALL be stored at appropriate keys (e.g., `user.name`, `user.email`, `work.schedule.start`)

---

### Requirement: Setup runs skill discovery

The setup protocol SHALL discover available skills.

#### Scenario: Discovery during setup

- **WHEN** AI follows the setup protocol
- **THEN** it SHALL run `layton rolodex --discover`
- **AND** it SHALL offer to create rolodex cards for discovered skills

---

### Requirement: Setup triggered by doctor

The setup protocol SHALL be suggested when config is missing.

#### Scenario: Doctor suggests setup

- **WHEN** `layton doctor` reports `CONFIG_MISSING` or incomplete config
- **THEN** `next_steps` SHALL suggest running the setup protocol

---

### Requirement: Setup persona

The setup protocol SHALL use the Elizabeth Layton persona.

#### Scenario: Persona voice

- **WHEN** AI follows the setup protocol
- **THEN** it SHALL introduce itself using the persona from `references/persona.md`
- **AND** interactions SHALL maintain professional, helpful tone
