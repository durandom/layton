## ADDED Requirements

### Requirement: Errand file format

Errands SHALL be markdown files with YAML-like frontmatter stored in `.layton/errands/`.

#### Scenario: Valid errand structure

- **WHEN** an errand file exists at `.layton/errands/<name>.md`
- **THEN** file SHALL contain frontmatter delimited by `---` markers
- **AND** frontmatter SHALL contain `name` field (string)
- **AND** frontmatter SHALL contain `description` field (string)
- **AND** frontmatter MAY contain `variables` section with key:description pairs
- **AND** file body after frontmatter SHALL contain task instructions

#### Scenario: Errand with declared variables

- **WHEN** frontmatter contains a `variables:` section
- **THEN** each line under variables SHALL be parsed as `variable_name: description`
- **AND** variable descriptions SHALL be available for display in list output

#### Scenario: Errand with runtime variables

- **WHEN** an errand body contains `${variable_name}` patterns
- **THEN** these SHALL be preserved as-is until scheduling time
- **AND** `string.Template.safe_substitute()` SHALL be used for variable replacement

---

### Requirement: Errands directory structure

The CLI SHALL manage errands in a dedicated directory.

#### Scenario: Errands directory location

- **WHEN** Layton is initialized
- **THEN** errands SHALL be stored in `.layton/errands/`
- **AND** directory SHALL be created on first errand addition

#### Scenario: Errand file naming

- **WHEN** an errand is added with name `code-review`
- **THEN** file SHALL be created at `.layton/errands/code-review.md`

---

### Requirement: Frontmatter parsing

The CLI SHALL parse errand frontmatter using stdlib-only parsing.

#### Scenario: Parse simple key-value frontmatter

- **WHEN** frontmatter contains `name: my-task`
- **THEN** parser SHALL extract `{"name": "my-task"}`

#### Scenario: Parse multiline description

- **WHEN** frontmatter contains description spanning multiple lines
- **THEN** parser SHALL capture the complete description value

#### Scenario: Invalid frontmatter handling

- **WHEN** a file has no `---` delimited frontmatter
- **THEN** parser SHALL return `None` for frontmatter
- **AND** CLI SHALL skip the file when listing errands

---

### Requirement: Errand skeleton

The CLI SHALL provide a skeleton template for new errands.

#### Scenario: Skeleton source location

- **WHEN** `layton errands add` needs the skeleton template
- **THEN** CLI SHALL load skeleton from `skills/layton/templates/bead.md`
- **AND** skeleton SHALL use `{name}` placeholder for `.format()` substitution

#### Scenario: Skeleton content

- **WHEN** user runs `layton errands add <name>`
- **THEN** created file SHALL contain frontmatter with `name` set to provided name
- **AND** created file SHALL contain `description` placeholder
- **AND** created file SHALL contain `variables` section placeholder
- **AND** created file SHALL contain body sections for Task and Acceptance Criteria
- **AND** created file SHALL contain "When Complete" section with standard closing instructions

#### Scenario: Standard closing instructions in skeleton

- **WHEN** skeleton is created
- **THEN** "When Complete" section SHALL include instruction to add findings as comments
- **AND** SHALL include `bd close` command with `--add-label needs-review`
- **AND** SHALL explain that the `needs-review` label signals human review needed

#### Scenario: Retrospective section in skeleton

- **WHEN** skeleton is created
- **THEN** skeleton SHALL contain a "Retrospective" section after "When Complete"
- **AND** SHALL instruct executor to add issue comments during execution when steps fail
- **AND** SHALL instruct executor to always add a retrospective comment after closing
- **AND** retrospective comment SHALL include status, issues encountered count, and proposed updates table
- **AND** proposed updates table SHALL list targets (bead, rolodex card, protocol) with file, change, and reason columns
- **AND** SHALL state that `None` should be written if no updates are needed

#### Scenario: Add duplicate errand

- **WHEN** user runs `layton errands add code-review` and `.layton/errands/code-review.md` exists
- **THEN** CLI SHALL return error with code `ERRAND_EXISTS`
- **AND** `next_steps` SHALL suggest reviewing existing file or choosing different name
