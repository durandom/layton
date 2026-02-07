## ADDED Requirements

### Requirement: List errands

The CLI SHALL list all available errands.

#### Scenario: List errands with no args

- **WHEN** user runs `layton errands` with no subcommand
- **THEN** CLI SHALL return JSON array of errands from `.layton/errands/`
- **AND** each errand SHALL include `name` and `description` from frontmatter
- **AND** each errand SHALL include `variables` object with variable names as keys and descriptions as values

#### Scenario: Empty errands directory

- **WHEN** user runs `layton errands` and `.layton/errands/` is empty or missing
- **THEN** CLI SHALL return empty array `{"errands": []}`
- **AND** `next_steps` SHALL include `layton errands add <name>`

#### Scenario: Errand not found for schedule

- **WHEN** user runs `layton errands schedule nonexistent`
- **THEN** CLI SHALL return error with code `ERRAND_NOT_FOUND`
- **AND** `next_steps` SHALL suggest `layton errands` to list available errands

---

### Requirement: Schedule errand

The CLI SHALL create beads from errands with variable substitution.

#### Scenario: Schedule with JSON variables

- **WHEN** user runs `layton errands schedule code-review '{"file_path": "src/auth.py"}'`
- **THEN** CLI SHALL load errand from `.layton/errands/code-review.md`
- **AND** CLI SHALL substitute `${file_path}` with `src/auth.py` in body
- **AND** CLI SHALL call `bd create` with rendered description

#### Scenario: Schedule with stdin variables

- **WHEN** user pipes JSON to `layton errands schedule code-review`
- **THEN** CLI SHALL read variables from stdin
- **AND** CLI SHALL process identically to inline JSON

#### Scenario: Schedule with no variables

- **WHEN** user runs `layton errands schedule standup` with no JSON argument
- **THEN** CLI SHALL use empty variables `{}`
- **AND** any `${var}` patterns SHALL remain as-is in output

#### Scenario: Invalid JSON input

- **WHEN** user provides malformed JSON
- **THEN** CLI SHALL return error with code `INVALID_JSON`
- **AND** exit code SHALL be 1

---

### Requirement: Fixed label application

The CLI SHALL apply fixed labels to all scheduled beads.

#### Scenario: Labels on bead creation

- **WHEN** a bead is scheduled from errand `code-review`
- **THEN** CLI SHALL apply label `scheduled`
- **AND** CLI SHALL apply label `type:code-review`

#### Scenario: Labels are not configurable per errand

- **WHEN** an errand file contains any label-related frontmatter
- **THEN** CLI SHALL ignore it
- **AND** CLI SHALL apply only the fixed labels

---

### Requirement: Epic configuration

The CLI SHALL manage a project epic for bead scheduling.

#### Scenario: Epic stored in config

- **WHEN** user runs `layton errands epic set beads-xyz123`
- **THEN** CLI SHALL store epic ID at `beads.epic` in config file
- **AND** CLI SHALL return success with stored value

#### Scenario: Show current epic

- **WHEN** user runs `layton errands epic`
- **THEN** CLI SHALL return current epic ID from config
- **AND** if no epic configured, SHALL return error with code `NO_EPIC`

#### Scenario: Schedule requires epic

- **WHEN** user runs `layton errands schedule` without epic configured
- **THEN** CLI SHALL return error with code `NO_EPIC`
- **AND** `next_steps` SHALL include `layton errands epic set <id>`

---

### Requirement: Bead creation via bd CLI

The CLI SHALL delegate bead creation to the `bd` CLI.

#### Scenario: Successful bead creation

- **WHEN** `layton errands schedule` is invoked with valid errand and epic
- **THEN** CLI SHALL execute `bd create` with title, parent, labels, and description
- **AND** CLI SHALL return created bead ID in response

#### Scenario: bd CLI unavailable

- **WHEN** `bd` command is not found
- **THEN** CLI SHALL return error with code `BD_UNAVAILABLE`
- **AND** `next_steps` SHALL include installation instructions

#### Scenario: bd create failure

- **WHEN** `bd create` returns non-zero exit code
- **THEN** CLI SHALL return error with code `BD_ERROR`
- **AND** error message SHALL include bd stderr output
