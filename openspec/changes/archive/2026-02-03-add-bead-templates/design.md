## Context

Layton already manages skills and workflows using a consistent pattern:

- Markdown files with YAML-like frontmatter (`---` delimited)
- Simple key-value parsing (no external YAML dependency)
- `.format(name=name)` for template instantiation
- Directory structure: `.layton/skills/`, `.layton/workflows/`

Beads extend this pattern to support schedulable work units. External executors (ralph-tui) watch for beads with specific labels and execute them. Labels drive state management—the CLI and workflow own the label conventions, not individual templates.

## Goals / Non-Goals

**Goals:**

- Follow existing skills/workflows pattern exactly (stdlib only, same frontmatter format)
- Enable CLI-driven bead scheduling with JSON variable input
- Support label-based state management for external executors
- Store epic configuration in existing config file

**Non-Goals:**

- No ralph-tui integration (beads are just created; execution is external)
- No Jinja2 or external templating dependencies
- No configurable labels per template (labels are workflow machinery)
- No nested/hierarchical bead relationships

## Decisions

### Decision 1: Two-phase variable substitution

**Choice**: Use Python's `.format()` for template installation and `string.Template` (`$var`) for runtime scheduling.

**Rationale**:

- `.format()` uses `{var}` syntax—already used by skills/workflows
- `string.Template` uses `$var` syntax—distinct, stdlib-only
- Phase 1: `{name}` filled when `layton beads add` creates template
- Phase 2: `${file_path}` filled when `layton beads schedule` runs

**Alternatives considered**:

- Single-phase with only `.format()`: Ambiguous when both template name and runtime vars needed
- Jinja2: External dependency, violates stdlib-only constraint

### Decision 2: Labels are fixed by CLI, not templates

**Choice**: The CLI hardcodes label conventions. Templates contain only content.

**Rationale**:

- Labels are workflow machinery for external tools (ralph-tui)
- Consistent label semantics across all beads
- Simpler templates (no label configuration to get wrong)

**Fixed labels**:

- `scheduled`: Applied on create, signals ready for pickup
- `type:<template-name>`: Applied on create, categorizes the bead
- `needs-review`: Applied on close by executor (not by CLI)

### Decision 3: JSON input for variables

**Choice**: Variables passed as JSON argument or stdin, not CLI flags.

**Rationale**:

- Composable with other tools (piping, scripting)
- No flag proliferation as templates grow
- Matches Layton's JSON-first output philosophy

**Usage**:

```bash
layton beads schedule code-review '{"file_path": "src/auth.py"}'
echo '{"file_path": "src/auth.py"}' | layton beads schedule code-review
```

### Decision 4: Single epic per project

**Choice**: Store one epic ID in config at `beads.epic`. All scheduled beads become children of this epic.

**Rationale**:

- Simple mental model (one project = one epic)
- Matches ralph-tui's expected structure
- Epic can be changed if workflow needs shift

## Risks / Trade-offs

**[Risk] Missing variables silently ignored** → `safe_substitute()` leaves `${var}` as-is if not provided. Could cause confusion.

- Mitigation: Document behavior. Consider optional strict mode later.

**[Risk] bd CLI unavailable** → Scheduling fails if bd not installed.

- Mitigation: Already a Layton prerequisite; doctor check exists.

**[Risk] Epic not configured** → First schedule attempt fails.

- Mitigation: Clear error message with `next_steps` pointing to `layton beads epic set`.
