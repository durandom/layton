## ADDED Requirements

### Requirement: Bead template file format

Bead templates SHALL be markdown files with YAML-like frontmatter stored in `.layton/beads/`.

#### Scenario: Valid bead template structure

- **WHEN** a bead template file exists at `.layton/beads/<name>.md`
- **THEN** file SHALL contain frontmatter delimited by `---` markers
- **AND** frontmatter SHALL contain `name` field (string)
- **AND** frontmatter SHALL contain `description` field (string)
- **AND** frontmatter MAY contain `variables` section with key:description pairs
- **AND** file body after frontmatter SHALL contain task instructions

#### Scenario: Template with declared variables

- **WHEN** frontmatter contains a `variables:` section
- **THEN** each line under variables SHALL be parsed as `variable_name: description`
- **AND** variable descriptions SHALL be available for display in list output

#### Scenario: Template with runtime variables

- **WHEN** a bead template body contains `${variable_name}` patterns
- **THEN** these SHALL be preserved as-is until scheduling time
- **AND** `string.Template.safe_substitute()` SHALL be used for variable replacement

---

### Requirement: Bead template directory structure

The CLI SHALL manage bead templates in a dedicated directory.

#### Scenario: Beads directory location

- **WHEN** Layton is initialized
- **THEN** bead templates SHALL be stored in `.layton/beads/`
- **AND** directory SHALL be created on first template addition

#### Scenario: Template file naming

- **WHEN** a bead template is added with name `code-review`
- **THEN** file SHALL be created at `.layton/beads/code-review.md`

---

### Requirement: Frontmatter parsing

The CLI SHALL parse bead template frontmatter using stdlib-only parsing.

#### Scenario: Parse simple key-value frontmatter

- **WHEN** frontmatter contains `name: my-task`
- **THEN** parser SHALL extract `{"name": "my-task"}`

#### Scenario: Parse multiline description

- **WHEN** frontmatter contains description spanning multiple lines
- **THEN** parser SHALL capture the complete description value

#### Scenario: Invalid frontmatter handling

- **WHEN** a file has no `---` delimited frontmatter
- **THEN** parser SHALL return `None` for frontmatter
- **AND** CLI SHALL skip the file when listing templates

---

### Requirement: Bead template skeleton

The CLI SHALL provide a skeleton template for new beads.

#### Scenario: Skeleton source location

- **WHEN** `layton beads add` needs the skeleton template
- **THEN** CLI SHALL load skeleton from `skills/layton/templates/bead.md`
- **AND** skeleton SHALL use `{name}` placeholder for `.format()` substitution

#### Scenario: Template skeleton content

- **WHEN** user runs `layton beads add <name>`
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

#### Scenario: Add duplicate template

- **WHEN** user runs `layton beads add code-review` and `.layton/beads/code-review.md` exists
- **THEN** CLI SHALL return error with code `BEAD_EXISTS`
- **AND** `next_steps` SHALL suggest reviewing existing file or choosing different name
