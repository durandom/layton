## 1. Skeleton Template

- [x] 1.1 Create `skills/layton/templates/bead.md` with frontmatter (name, description, variables placeholders)
- [x] 1.2 Add Task and Acceptance Criteria body sections to skeleton
- [x] 1.3 Add "When Complete" section with `bd comments add` and `bd close --add-label needs-review` instructions

## 2. Core Module

- [x] 2.1 Create `laytonlib/beads.py` with `BeadInfo` dataclass (name, description, variables, path)
- [x] 2.2 Implement `parse_frontmatter()` with variables section parsing (key:description pairs)
- [x] 2.3 Implement `get_beads_dir()` returning `.layton/beads/` path
- [x] 2.4 Implement `get_bead_template()` loading skeleton from `templates/bead.md`
- [x] 2.5 Implement `list_beads()` returning list of BeadInfo from `.layton/beads/`
- [x] 2.6 Implement `add_bead(name)` creating template with `.format(name=name)` substitution
- [x] 2.7 Implement `load_bead_template(name)` reading specific template for scheduling

## 3. Scheduling Module

- [x] 3.1 Add `LABEL_SCHEDULED = "scheduled"` and `LABEL_NEEDS_REVIEW = "needs-review"` constants
- [x] 3.2 Implement `schedule_bead(name, variables)` with `string.Template.safe_substitute()`
- [x] 3.3 Implement `bd_create()` wrapper executing `bd create` with title, parent, labels, description
- [x] 3.4 Implement epic config helpers: `get_epic()` and `set_epic(epic_id)`
- [x] 3.5 Add error handling for BD_UNAVAILABLE, BD_ERROR, NO_EPIC, TEMPLATE_NOT_FOUND

## 4. CLI Integration

- [x] 4.1 Add `beads` subparser to `create_parser()` in cli.py
- [x] 4.2 Add `beads add <name>` subcommand
- [x] 4.3 Add `beads schedule <name> [json]` subcommand with stdin support
- [x] 4.4 Add `beads epic` and `beads epic set <id>` subcommands
- [x] 4.5 Implement `run_beads()` handler routing to subcommands
- [x] 4.6 Wire beads list (no subcommand) to `list_beads()` with variables in output

## 5. Orientation Integration

- [x] 5.1 Update `run_orientation()` in cli.py to include `bead_templates` field
- [x] 5.2 Add bead templates to orientation output with name, description, variables
- [x] 5.3 Add `beads_pending_review` field querying bd for closed beads with `needs-review` label
- [x] 5.4 Add `beads_scheduled` field querying bd for open beads with `scheduled` label
- [x] 5.5 Implement `get_beads_by_label()` helper to query bd list with label filter

## 6. Config Integration

- [x] 6.1 Add `beads.epic` field support to config schema
- [x] 6.2 Update config validation to handle beads section

## 7. Unit Tests

- [x] 7.1 Create `tests/unit/test_beads.py`
- [x] 7.2 Add test for `parse_frontmatter()` with variables section
- [x] 7.3 Add test for `list_beads()` with empty directory
- [x] 7.4 Add test for `list_beads()` with valid templates
- [x] 7.5 Add test for `add_bead()` success case
- [x] 7.6 Add test for `add_bead()` duplicate error (BEAD_EXISTS)
- [x] 7.7 Add test for `schedule_bead()` variable substitution

## 8. E2E Tests

- [x] 8.1 Create `tests/e2e/test_beads_e2e.py`
- [x] 8.2 Add test for `layton beads` list command
- [x] 8.3 Add test for `layton beads add <name>` creates file
- [x] 8.4 Add test for `layton beads epic set` and `layton beads epic`
- [x] 8.5 Add test for orientation includes bead_templates array
- [x] 8.6 Add test for orientation includes beads_pending_review
- [x] 8.7 Add test for orientation includes beads_scheduled

## 9. Workflows

- [x] 9.1 Create `skills/layton/workflows/schedule-bead.md` with steps to list templates and schedule
- [x] 9.2 Create `skills/layton/workflows/review-beads.md` with steps to find and review completed beads
- [x] 9.3 Add workflow references to beads CLI commands and orientation fields

## 10. SKILL.md Integration

- [x] 10.1 Add bead intents to `<routing>` section (schedule bead, review beads)
- [x] 10.2 Add `$LAYTON beads` commands to `<cli_commands>` section
- [x] 10.3 Add schedule-bead.md and review-beads.md to `<workflows_index>` table
- [x] 10.4 Add bead-related items to `<success_criteria>` checklist
