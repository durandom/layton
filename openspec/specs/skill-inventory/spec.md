## ADDED Requirements

### Requirement: Rolodex card format

Rolodex cards SHALL use YAML frontmatter with markdown body, stored in `.layton/rolodex/<name>.md`.

#### Scenario: Valid rolodex card structure

- **WHEN** a rolodex card exists at `.layton/rolodex/gtd.md`
- **THEN** it SHALL have YAML frontmatter with `name`, `description`, and `source` fields
- **AND** the markdown body SHALL contain instructions for querying the skill

#### Scenario: Frontmatter fields

- **WHEN** parsing a rolodex card's frontmatter
- **THEN** `name` SHALL be a lowercase identifier matching the filename (without `.md`)
- **AND** `description` SHALL describe when/why to query this skill
- **AND** `source` SHALL be the path to the source SKILL.md (e.g., `skills/gtd/SKILL.md`)

---

### Requirement: Rolodex card template

The CLI SHALL provide a template for bootstrapping new rolodex cards.

#### Scenario: Template content

- **WHEN** `layton rolodex add <name>` is run
- **THEN** CLI SHALL create `.layton/rolodex/<name>.md` with this template:

```markdown
---
name: <name>
description: <when/why to query this skill>
source: skills/<name>/SKILL.md
---

## Commands

<!-- Commands to run when gathering data from this skill -->
<!-- Run from repo root -->

```bash
# Example:
# SKILL="./.claude/skills/<name>/scripts/<name>"
# $SKILL <command>
```text

## What to Extract

<!-- Key information to look for in the output -->

-
-

## Key Metrics

<!-- Important numbers or states to surface in briefings -->

| Metric | Meaning |
|--------|---------|
|        |         |

```text

#### Scenario: Template sections purpose

- **WHEN** AI reads a rolodex card
- **THEN** `## Commands` SHALL contain bash commands to execute for data gathering
- **AND** `## What to Extract` SHALL guide what information matters from the output
- **AND** `## Key Metrics` SHALL define important indicators for briefings

#### Scenario: Template does not overwrite

- **WHEN** `layton rolodex add <name>` is run AND `.layton/rolodex/<name>.md` exists
- **THEN** CLI SHALL return error with code `CARD_EXISTS`
- **AND** error message SHALL suggest reviewing existing file

---

### Requirement: Skill discovery

The CLI SHALL discover external skills by scanning the `skills/` directory.

#### Scenario: Discover available skills

- **WHEN** `layton rolodex --discover` is run
- **THEN** CLI SHALL scan `skills/*/SKILL.md` for available skills
- **AND** output SHALL include `known` array (skills with cards in `.layton/rolodex/`)
- **AND** output SHALL include `unknown` array (skills without cards)

#### Scenario: Discovery extracts metadata

- **WHEN** scanning a SKILL.md file
- **THEN** CLI SHALL extract `name` and `description` from YAML frontmatter
- **AND** unknown skills output SHALL include this metadata

#### Scenario: Self-exclusion

- **WHEN** discovering skills
- **THEN** CLI SHALL exclude `skills/layton/SKILL.md` from results (Layton doesn't query itself)

---

### Requirement: List known rolodex cards

The CLI SHALL list rolodex cards from `.layton/rolodex/`.

#### Scenario: List with JSON output

- **WHEN** `layton rolodex` is run
- **THEN** output SHALL be JSON with `success` and `rolodex` array
- **AND** each card SHALL include `name`, `description`, `source` from frontmatter

#### Scenario: Empty rolodex directory

- **WHEN** `layton rolodex` is run AND `.layton/rolodex/` is empty or missing
- **THEN** output SHALL have empty `rolodex` array
- **AND** `next_steps` SHALL suggest `layton rolodex --discover` and `layton rolodex add`

---

### Requirement: Rolodex directory creation

The CLI SHALL create `.layton/rolodex/` directory when needed.

#### Scenario: Auto-create on add

- **WHEN** `layton rolodex add <name>` is run AND `.layton/rolodex/` doesn't exist
- **THEN** CLI SHALL create the directory before creating the rolodex card
