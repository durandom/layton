"""Unit tests for beads module."""

import sys
from pathlib import Path

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "skills" / "layton" / "scripts"),
)

from laytonlib.beads import (
    BEAD_TEMPLATE,
    BeadInfo,
    add_bead,
    list_beads,
    parse_frontmatter,
    schedule_bead,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function with variables section."""

    def test_valid_frontmatter(self):
        """Parses valid YAML frontmatter."""
        content = """---
name: test
description: A test bead
---

## Task

Do something.
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test bead"

    def test_frontmatter_with_variables(self):
        """Parses frontmatter with variables section."""
        content = """---
name: code-review
description: Review code for issues
variables:
  file_path: The path to the file to review
  focus_area: What to focus on during review
---

## Task

Review ${file_path}.
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "code-review"
        assert "variables" in result
        assert result["variables"]["file_path"] == "The path to the file to review"
        assert result["variables"]["focus_area"] == "What to focus on during review"

    def test_no_frontmatter(self):
        """Returns None for content without frontmatter."""
        content = "# Just a header\n\nSome content."
        result = parse_frontmatter(content)
        assert result is None

    def test_empty_frontmatter(self):
        """Returns None for empty frontmatter."""
        content = """---
---

## Task
"""
        result = parse_frontmatter(content)
        assert result is None

    def test_frontmatter_with_comments(self):
        """Skips comment lines in frontmatter."""
        content = """---
name: test
# This is a comment
description: A test bead
---

## Task
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test bead"

    def test_variables_with_comments(self):
        """Parses variables section with comment lines."""
        content = """---
name: test
variables:
  # This is a comment in variables
  file_path: The file path
---

## Task
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert "variables" in result
        assert result["variables"]["file_path"] == "The file path"


class TestListBeads:
    """Tests for list_beads function."""

    def test_empty_dir(self, temp_beads_dir):
        """Returns empty list when beads directory is empty."""
        result = list_beads()
        assert result == []

    def test_missing_dir(self, isolated_env):
        """Returns empty list when beads directory doesn't exist."""
        # The beads dir doesn't exist by default in isolated_env
        beads_dir = isolated_env / ".layton" / "beads"
        if beads_dir.exists():
            beads_dir.rmdir()
        result = list_beads()
        assert result == []

    def test_multiple_beads(self, temp_beads_dir):
        """Lists multiple bead templates sorted by name."""
        (temp_beads_dir / "zebra.md").write_text(
            """---
name: zebra
description: Last bead
---
"""
        )
        (temp_beads_dir / "alpha.md").write_text(
            """---
name: alpha
description: First bead
---
"""
        )

        result = list_beads()
        assert len(result) == 2
        assert result[0].name == "alpha"
        assert result[1].name == "zebra"

    def test_beads_with_variables(self, temp_beads_dir):
        """Lists beads with their declared variables."""
        (temp_beads_dir / "review.md").write_text(
            """---
name: review
description: Code review
variables:
  file_path: File to review
  focus: Focus area
---
"""
        )

        result = list_beads()
        assert len(result) == 1
        assert result[0].name == "review"
        assert result[0].variables["file_path"] == "File to review"
        assert result[0].variables["focus"] == "Focus area"


class TestAddBead:
    """Tests for add_bead function."""

    def test_creates_file(self, temp_beads_dir):
        """Creates bead template from skeleton."""
        path = add_bead("newbead")

        assert path.exists()
        assert path.name == "newbead.md"
        content = path.read_text()
        assert "name: newbead" in content

    def test_creates_directory(self, isolated_env):
        """Creates .layton/beads/ if it doesn't exist."""
        beads_dir = isolated_env / ".layton" / "beads"
        if beads_dir.exists():
            beads_dir.rmdir()

        path = add_bead("newbead")

        assert beads_dir.exists()
        assert path.exists()

    def test_error_if_exists(self, temp_beads_dir):
        """Raises FileExistsError if bead template already exists."""
        (temp_beads_dir / "existing.md").write_text("existing content")

        try:
            add_bead("existing")
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            assert "already exists" in str(e)


class TestScheduleBead:
    """Tests for schedule_bead function with variable substitution."""

    def test_variable_substitution(self, temp_beads_dir, temp_config, monkeypatch):
        """Substitutes variables using string.Template."""
        import json
        import shutil
        import subprocess

        from laytonlib import beads as beads_module

        # Create template with variables
        (temp_beads_dir / "review.md").write_text(
            """---
name: review
description: Review code
variables:
  file_path: The file to review
---

## Task

Review the file at ${file_path} for issues.
Check ${missing_var} as well.
"""
        )

        # Configure epic in config file
        temp_config.write_text(json.dumps({"beads": {"epic": "test-epic"}}))

        # Mock get_beads_dir to return our temp dir
        monkeypatch.setattr(beads_module, "get_beads_dir", lambda: temp_beads_dir)

        # Mock get_epic to return our epic (since config path detection may differ)
        monkeypatch.setattr(beads_module, "get_epic", lambda: "test-epic")

        # Mock bd to avoid actual execution - capture the command for assertions
        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.extend(cmd)

            class Result:
                stdout = '{"id": "bead-123"}'
                returncode = 0

            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Mock shutil.which to return bd
        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None
        )

        result = schedule_bead("review", {"file_path": "src/auth.py"})

        # Result should come from mocked bd
        assert result["id"] == "bead-123"

        # Verify the rendered body was passed to bd (variable substituted)
        description_idx = captured_cmd.index("--description") + 1
        rendered_body = captured_cmd[description_idx]
        assert "src/auth.py" in rendered_body  # Variable was substituted
        assert "${missing_var}" in rendered_body  # Unsubstituted var remains as-is


class TestBeadTemplate:
    """Tests for bead template."""

    def test_has_required_sections(self):
        """Template has required sections."""
        assert "## Task" in BEAD_TEMPLATE
        assert "## Acceptance Criteria" in BEAD_TEMPLATE
        assert "## When Complete" in BEAD_TEMPLATE

    def test_has_frontmatter_placeholders(self):
        """Template has frontmatter placeholders."""
        assert "name: {name}" in BEAD_TEMPLATE
        assert "description:" in BEAD_TEMPLATE
        assert "variables:" in BEAD_TEMPLATE

    def test_has_closing_instructions(self):
        """Template has standard closing instructions."""
        assert "bd comments add" in BEAD_TEMPLATE
        assert "bd close --add-label needs-review" in BEAD_TEMPLATE


class TestBeadInfo:
    """Tests for BeadInfo dataclass."""

    def test_to_dict(self, tmp_path):
        """to_dict returns proper dictionary."""
        path = tmp_path / "test.md"
        bead = BeadInfo(
            name="test",
            description="Test bead",
            variables={"file_path": "File to process"},
            path=path,
        )
        d = bead.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test bead"
        assert d["variables"]["file_path"] == "File to process"
        assert d["path"] == str(path)

    def test_to_dict_without_path(self):
        """to_dict works without path."""
        bead = BeadInfo(
            name="test",
            description="Test bead",
            variables={},
        )
        d = bead.to_dict()

        assert d["name"] == "test"
        assert "path" not in d
