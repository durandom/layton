"""Unit tests for errands module."""

import sys
from pathlib import Path

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "skills" / "layton" / "scripts"),
)

from laytonlib.errands import (
    ERRAND_TEMPLATE,
    ErrandInfo,
    _transition_to_in_progress,
    add_errand,
    build_prompt,
    get_bead,
    get_beads_in_progress,
    list_errands,
    parse_frontmatter,
    schedule_errand,
)
from laytonlib.cli import _parse_json_vars


class TestParseFrontmatter:
    """Tests for parse_frontmatter function with variables section."""

    def test_valid_frontmatter(self):
        """Parses valid YAML frontmatter."""
        content = """---
name: test
description: A test errand
---

## Task

Do something.
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test errand"

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
description: A test errand
---

## Task
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test errand"

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


class TestListErrands:
    """Tests for list_errands function."""

    def test_empty_dir(self, temp_errands_dir):
        """Returns empty list when errands directory is empty."""
        result = list_errands()
        assert result == []

    def test_missing_dir(self, isolated_env):
        """Returns empty list when errands directory doesn't exist."""
        errands_dir = isolated_env / ".layton" / "errands"
        if errands_dir.exists():
            errands_dir.rmdir()
        result = list_errands()
        assert result == []

    def test_multiple_errands(self, temp_errands_dir):
        """Lists multiple errands sorted by name."""
        (temp_errands_dir / "zebra.md").write_text(
            """---
name: zebra
description: Last errand
---
"""
        )
        (temp_errands_dir / "alpha.md").write_text(
            """---
name: alpha
description: First errand
---
"""
        )

        result = list_errands()
        assert len(result) == 2
        assert result[0].name == "alpha"
        assert result[1].name == "zebra"

    def test_errands_with_variables(self, temp_errands_dir):
        """Lists errands with their declared variables."""
        (temp_errands_dir / "review.md").write_text(
            """---
name: review
description: Code review
variables:
  file_path: File to review
  focus: Focus area
---
"""
        )

        result = list_errands()
        assert len(result) == 1
        assert result[0].name == "review"
        assert result[0].variables["file_path"] == "File to review"
        assert result[0].variables["focus"] == "Focus area"


class TestAddErrand:
    """Tests for add_errand function."""

    def test_creates_file(self, temp_errands_dir):
        """Creates errand from template."""
        path = add_errand("newerrand")

        assert path.exists()
        assert path.name == "newerrand.md"
        content = path.read_text()
        assert "name: newerrand" in content

    def test_creates_directory(self, isolated_env):
        """Creates .layton/errands/ if it doesn't exist."""
        errands_dir = isolated_env / ".layton" / "errands"
        if errands_dir.exists():
            errands_dir.rmdir()

        path = add_errand("newerrand")

        assert errands_dir.exists()
        assert path.exists()

    def test_error_if_exists(self, temp_errands_dir):
        """Raises FileExistsError if errand already exists."""
        (temp_errands_dir / "existing.md").write_text("existing content")

        try:
            add_errand("existing")
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            assert "already exists" in str(e)


class TestScheduleErrand:
    """Tests for schedule_errand function with variable substitution."""

    def test_variable_substitution(self, temp_errands_dir, temp_config, monkeypatch):
        """Substitutes variables using string.Template."""
        import json
        import shutil
        import subprocess

        from laytonlib import errands as errands_module

        # Create errand with variables
        (temp_errands_dir / "review.md").write_text(
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
        temp_config.write_text(json.dumps({"errands": {"epic": "test-epic"}}))

        # Mock get_errands_dir to return our temp dir
        monkeypatch.setattr(errands_module, "get_errands_dir", lambda: temp_errands_dir)

        # Mock get_epic to return our epic (since config path detection may differ)
        monkeypatch.setattr(errands_module, "get_epic", lambda: "test-epic")

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

        result = schedule_errand("review", {"file_path": "src/auth.py"})

        # Result should come from mocked bd
        assert result["id"] == "bead-123"

        # Verify the rendered body was passed to bd (variable substituted)
        description_idx = captured_cmd.index("--description") + 1
        rendered_body = captured_cmd[description_idx]
        assert "src/auth.py" in rendered_body  # Variable was substituted
        assert "${missing_var}" in rendered_body  # Unsubstituted var remains as-is


class TestErrandTemplate:
    """Tests for errand template."""

    def test_has_required_sections(self):
        """Template has required sections."""
        assert "## Task" in ERRAND_TEMPLATE
        assert "## Acceptance Criteria" in ERRAND_TEMPLATE
        assert "## When Complete" in ERRAND_TEMPLATE

    def test_has_frontmatter_placeholders(self):
        """Template has frontmatter placeholders."""
        assert "name: {name}" in ERRAND_TEMPLATE
        assert "description:" in ERRAND_TEMPLATE
        assert "variables:" in ERRAND_TEMPLATE

    def test_has_closing_instructions(self):
        """Template has standard closing instructions."""
        assert "bd comments add" in ERRAND_TEMPLATE
        assert "bd close" in ERRAND_TEMPLATE
        assert "bd label add needs-review" in ERRAND_TEMPLATE


class TestErrandInfo:
    """Tests for ErrandInfo dataclass."""

    def test_to_dict(self, tmp_path):
        """to_dict returns proper dictionary."""
        path = tmp_path / "test.md"
        errand = ErrandInfo(
            name="test",
            description="Test errand",
            variables={"file_path": "File to process"},
            path=path,
        )
        d = errand.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test errand"
        assert d["variables"]["file_path"] == "File to process"
        assert d["path"] == str(path)

    def test_to_dict_without_path(self):
        """to_dict works without path."""
        errand = ErrandInfo(
            name="test",
            description="Test errand",
            variables={},
        )
        d = errand.to_dict()

        assert d["name"] == "test"
        assert "path" not in d


class TestGetBead:
    """Tests for get_bead function."""

    def test_returns_bead_dict(self, monkeypatch):
        """Parses bd show --json output into dict."""
        import shutil
        import subprocess

        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None
        )

        def mock_run(cmd, *args, **kwargs):
            class Result:
                stdout = '[{"id": "abc-123", "title": "Test", "description": "Body"}]'
                returncode = 0

            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = get_bead("abc-123")
        assert result is not None
        assert result["id"] == "abc-123"
        assert result["title"] == "Test"

    def test_returns_none_when_not_found(self, monkeypatch):
        """Returns None when bd show fails (bead not found)."""
        import shutil
        import subprocess

        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None
        )

        def mock_run(cmd, *args, **kwargs):
            raise subprocess.CalledProcessError(1, cmd)

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = get_bead("nonexistent")
        assert result is None

    def test_returns_none_when_bd_unavailable(self, monkeypatch):
        """Returns None when bd CLI is not installed."""
        import shutil

        monkeypatch.setattr(shutil, "which", lambda cmd: None)

        result = get_bead("abc-123")
        assert result is None


class TestGetBeadsInProgress:
    """Tests for get_beads_in_progress function."""

    def test_returns_empty_when_bd_unavailable(self, monkeypatch):
        """Returns empty list when bd CLI is not installed."""
        import shutil

        monkeypatch.setattr(shutil, "which", lambda cmd: None)

        result = get_beads_in_progress()
        assert result == []

    def test_queries_correct_label(self, monkeypatch):
        """Queries bd with in-progress label and open status."""
        import shutil
        import subprocess

        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None
        )

        captured_cmd = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmd.extend(cmd)

            class Result:
                stdout = '[{"id": "bead-1", "title": "Test"}]'
                returncode = 0

            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = get_beads_in_progress()
        assert len(result) == 1
        assert result[0]["id"] == "bead-1"
        assert "in-progress" in captured_cmd
        assert "open" in captured_cmd


class TestTransitionToInProgress:
    """Tests for _transition_to_in_progress helper."""

    def test_returns_false_when_bd_unavailable(self, monkeypatch):
        """Returns False when bd CLI is not installed."""
        import shutil

        monkeypatch.setattr(shutil, "which", lambda cmd: None)

        result = _transition_to_in_progress("bead-42")
        assert result is False

    def test_swaps_labels(self, monkeypatch):
        """Removes scheduled label and adds in-progress label."""
        import shutil
        import subprocess

        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None
        )

        captured_cmds = []

        def mock_run(cmd, *args, **kwargs):
            captured_cmds.append(list(cmd))

            class Result:
                stdout = ""
                returncode = 0

            return Result()

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = _transition_to_in_progress("bead-42")
        assert result is True
        assert len(captured_cmds) == 2
        assert captured_cmds[0] == ["bd", "label", "remove", "bead-42", "scheduled"]
        assert captured_cmds[1] == ["bd", "label", "add", "bead-42", "in-progress"]

    def test_returns_false_on_subprocess_error(self, monkeypatch):
        """Returns False when bd label command fails."""
        import shutil
        import subprocess

        monkeypatch.setattr(
            shutil, "which", lambda cmd: "/usr/bin/bd" if cmd == "bd" else None
        )

        def mock_run(cmd, *args, **kwargs):
            raise subprocess.CalledProcessError(1, cmd)

        monkeypatch.setattr(subprocess, "run", mock_run)

        result = _transition_to_in_progress("bead-42")
        assert result is False


class TestBuildPrompt:
    """Tests for build_prompt function."""

    def test_builds_prompt_with_all_sections(self, monkeypatch):
        """Prompt contains bead ID, title, description, and completion protocol."""
        from laytonlib import errands as errands_module

        monkeypatch.setattr(
            errands_module,
            "get_bead",
            lambda bid: {
                "id": "bead-42",
                "title": "[review] Code review",
                "description": "## Task\n\nReview src/auth.py",
            },
        )
        monkeypatch.setattr(
            errands_module, "get_bead_comments", lambda bid: "Previous finding here"
        )
        monkeypatch.setattr(
            errands_module, "_transition_to_in_progress", lambda bid: True
        )

        result = build_prompt("bead-42")
        assert result is not None
        assert "bead-42" in result
        assert "[review] Code review" in result
        assert "## Task" in result
        assert "Review src/auth.py" in result
        # Completion protocol commands with correct bead ID
        assert "bd close bead-42" in result
        assert "bd label add bead-42 needs-review" in result
        assert 'bd comments add bead-42' in result
        # New step: remove in-progress label
        assert "bd label remove bead-42 in-progress" in result
        # Context section with comments
        assert "## Context (prior comments)" in result
        assert "Previous finding here" in result

    def test_returns_none_for_missing_bead(self, monkeypatch):
        """Returns None when bead not found."""
        from laytonlib import errands as errands_module

        monkeypatch.setattr(errands_module, "get_bead", lambda bid: None)

        result = build_prompt("nonexistent")
        assert result is None

    def test_omits_context_when_no_comments(self, monkeypatch):
        """Context section is omitted when there are no comments."""
        from laytonlib import errands as errands_module

        monkeypatch.setattr(
            errands_module,
            "get_bead",
            lambda bid: {
                "id": "bead-99",
                "title": "Test bead",
                "description": "Do something",
            },
        )
        monkeypatch.setattr(errands_module, "get_bead_comments", lambda bid: "")
        monkeypatch.setattr(
            errands_module, "_transition_to_in_progress", lambda bid: True
        )

        result = build_prompt("bead-99")
        assert result is not None
        assert "## Context (prior comments)" not in result
        # But completion protocol is still there
        assert "bd close bead-99" in result

    def test_calls_transition_to_in_progress(self, monkeypatch):
        """build_prompt calls _transition_to_in_progress with the bead ID."""
        from laytonlib import errands as errands_module

        transition_calls = []

        monkeypatch.setattr(
            errands_module,
            "get_bead",
            lambda bid: {"id": bid, "title": "Test", "description": "Body"},
        )
        monkeypatch.setattr(errands_module, "get_bead_comments", lambda bid: "")

        def mock_transition(bid):
            transition_calls.append(bid)
            return True

        monkeypatch.setattr(
            errands_module, "_transition_to_in_progress", mock_transition
        )

        build_prompt("bead-77")
        assert transition_calls == ["bead-77"]

    def test_prompt_still_returned_when_transition_fails(self, monkeypatch):
        """Prompt is still returned even if label transition fails."""
        from laytonlib import errands as errands_module

        monkeypatch.setattr(
            errands_module,
            "get_bead",
            lambda bid: {"id": bid, "title": "Test", "description": "Body"},
        )
        monkeypatch.setattr(errands_module, "get_bead_comments", lambda bid: "")
        monkeypatch.setattr(
            errands_module, "_transition_to_in_progress", lambda bid: False
        )

        result = build_prompt("bead-88")
        assert result is not None
        assert "bead-88" in result
        assert "bd close bead-88" in result


class TestParseJsonVars:
    """Tests for _parse_json_vars helper."""

    def test_parses_json_string(self):
        """Parses valid JSON argument."""
        result = _parse_json_vars('{"key": "value"}')
        assert result == {"key": "value"}

    def test_returns_empty_dict_when_no_input(self, monkeypatch):
        """Returns empty dict when no argument and stdin is a tty."""
        import io

        monkeypatch.setattr("sys.stdin", io.StringIO(""))
        monkeypatch.setattr("sys.stdin.isatty", lambda: True)
        result = _parse_json_vars(None)
        assert result == {}

    def test_returns_none_on_invalid_json(self):
        """Returns None for invalid JSON (caller should emit error)."""
        result = _parse_json_vars("not json")
        assert result is None

    def test_parses_empty_object(self):
        """Parses empty JSON object."""
        result = _parse_json_vars("{}")
        assert result == {}

    def test_rejects_non_dict_json_array(self):
        """Returns None for valid JSON that isn't a dict (e.g. array)."""
        result = _parse_json_vars("[]")
        assert result is None

    def test_rejects_non_dict_json_string(self):
        """Returns None for valid JSON string literal."""
        result = _parse_json_vars('"hello"')
        assert result is None

    def test_rejects_non_dict_json_number(self):
        """Returns None for valid JSON number."""
        result = _parse_json_vars("42")
        assert result is None
