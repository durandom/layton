"""E2E tests for layton errands command."""

import json
import subprocess
import sys
from pathlib import Path


def run_layton(*args, cwd=None):
    """Run layton CLI and return result."""
    script_path = (
        Path(__file__).parent.parent.parent / "skills" / "layton" / "scripts" / "layton"
    )
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result


def extract_json(output: str):
    """Extract JSON object or array from bd output (which may have warning lines)."""
    # Find where JSON starts (first { or [)
    obj_start = output.find("{")
    arr_start = output.find("[")

    if obj_start == -1 and arr_start == -1:
        raise ValueError(f"No JSON found in output: {output}")

    # Use whichever comes first (or the one that exists)
    if obj_start == -1:
        start = arr_start
    elif arr_start == -1:
        start = obj_start
    else:
        start = min(obj_start, arr_start)

    json_str = output[start:]
    return json.loads(json_str)


class TestErrandsCommand:
    """E2E tests for layton errands."""

    def test_errands_outputs_json(self, isolated_env):
        """errands outputs valid JSON by default."""
        result = run_layton("errands", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "errands" in data["data"]

    def test_errands_empty(self, temp_errands_dir):
        """errands returns empty array when no errands."""
        result = run_layton("errands", cwd=temp_errands_dir.parent.parent)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["errands"] == []
        assert "next_steps" in data

    def test_errands_lists_errands(self, temp_errands_dir):
        """errands lists errands from .layton/errands/."""
        (temp_errands_dir / "review.md").write_text(
            """---
name: review
description: Code review task
variables:
  file_path: File to review
---

## Task

Review ${file_path}.
"""
        )

        cwd = temp_errands_dir.parent.parent
        result = run_layton("errands", cwd=cwd)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["data"]["errands"]) == 1
        errand = data["data"]["errands"][0]
        assert errand["name"] == "review"
        assert errand["description"] == "Code review task"
        assert errand["variables"]["file_path"] == "File to review"


class TestErrandsAdd:
    """E2E tests for layton errands add."""

    def test_add_creates_file(self, isolated_env):
        """errands add creates errand file."""
        result = run_layton("errands", "add", "newerrand", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "newerrand" in data["data"]["created"]

        # Verify file exists
        errand_path = isolated_env / ".layton" / "errands" / "newerrand.md"
        assert errand_path.exists()

        # Verify content
        content = errand_path.read_text()
        assert "name: newerrand" in content
        assert "## Task" in content
        assert "## When Complete" in content

    def test_add_creates_directory(self, isolated_env):
        """errands add creates .layton/errands/ if missing."""
        errands_dir = isolated_env / ".layton" / "errands"
        if errands_dir.exists():
            errands_dir.rmdir()

        result = run_layton("errands", "add", "newerrand", cwd=isolated_env)

        assert result.returncode == 0
        assert errands_dir.exists()

    def test_add_error_if_exists(self, temp_errands_dir):
        """errands add returns error if errand exists."""
        (temp_errands_dir / "existing.md").write_text("existing content")
        cwd = temp_errands_dir.parent.parent
        result = run_layton("errands", "add", "existing", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "ERRAND_EXISTS"


class TestErrandsEpic:
    """E2E tests for layton errands epic."""

    def test_epic_no_config(self, isolated_env):
        """errands epic returns error when no epic configured."""
        result = run_layton("errands", "epic", cwd=isolated_env)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "NO_EPIC"
        assert "next_steps" in data

    def test_epic_set_and_get(self, temp_config):
        """errands epic set stores epic ID and errands epic retrieves it."""
        # Initialize config first
        temp_config.write_text("{}")
        cwd = temp_config.parent.parent

        # Set epic
        result = run_layton("errands", "epic", "set", "test-epic-123", cwd=cwd)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["epic"] == "test-epic-123"

        # Get epic
        result = run_layton("errands", "epic", cwd=cwd)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["epic"] == "test-epic-123"


class TestErrandsSchedule:
    """E2E tests for layton errands schedule (full bd integration)."""

    def test_schedule_creates_bead_with_labels(
        self, temp_errands_dir, temp_config, real_beads_isolated
    ):
        """errands schedule creates a bead via bd with correct labels and variable substitution."""
        cwd = temp_config.parent.parent

        # 1. Initialize beads database
        subprocess.run(["bd", "init"], cwd=cwd, capture_output=True, check=True)

        # 2. Create an epic to be the parent
        epic_result = subprocess.run(
            ["bd", "create", "--title", "Test Epic", "--type", "epic", "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        epic_data = extract_json(epic_result.stdout)
        epic_id = epic_data["id"]

        # 3. Set the epic via layton
        result = run_layton("errands", "epic", "set", epic_id, cwd=cwd)
        assert result.returncode == 0

        # 4. Create an errand with variables
        (temp_errands_dir / "code-review.md").write_text(
            """---
name: code-review
description: Review code for issues
variables:
  file_path: File to review
  focus_area: What to focus on
---

## Task

Review the file at ${file_path} for ${focus_area}.

## Acceptance Criteria

- [ ] Code reviewed
- [ ] Issues documented
"""
        )

        # 5. Schedule the errand with variables
        variables = {
            "file_path": "src/auth.py",
            "focus_area": "security vulnerabilities",
        }
        result = run_layton(
            "errands", "schedule", "code-review", json.dumps(variables), cwd=cwd
        )

        assert result.returncode == 0, (
            f"Schedule failed: {result.stdout} {result.stderr}"
        )
        data = json.loads(result.stdout)
        assert data["success"] is True
        scheduled_data = data["data"]["scheduled"]
        bead_id = scheduled_data["id"]

        # 6. Verify the bead was created with correct labels
        label_result = subprocess.run(
            ["bd", "label", "list", bead_id, "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        labels = extract_json(label_result.stdout)

        assert "scheduled" in labels
        assert "type:code-review" in labels

        # 7. Verify the bead description has substituted variables
        show_result = subprocess.run(
            ["bd", "show", bead_id, "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        bead_data = extract_json(show_result.stdout)[0]

        assert "src/auth.py" in bead_data["description"]
        assert "security vulnerabilities" in bead_data["description"]
        # Ensure variable placeholders were replaced
        assert "${file_path}" not in bead_data["description"]
        assert "${focus_area}" not in bead_data["description"]

    def test_schedule_without_epic_fails(
        self, temp_errands_dir, temp_config, real_beads_isolated
    ):
        """errands schedule fails with NO_EPIC if epic not configured."""
        cwd = temp_config.parent.parent

        # Initialize beads and config but don't set epic
        subprocess.run(["bd", "init"], cwd=cwd, capture_output=True, check=True)
        temp_config.write_text("{}")

        # Create a simple errand
        (temp_errands_dir / "simple.md").write_text(
            """---
name: simple
description: Simple task
---

## Task

Do something.
"""
        )

        result = run_layton("errands", "schedule", "simple", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "NO_EPIC"

    def test_schedule_nonexistent_errand_fails(self, temp_config, real_beads_isolated):
        """errands schedule fails with ERRAND_NOT_FOUND for missing errand."""
        cwd = temp_config.parent.parent

        # Initialize beads and set epic
        subprocess.run(["bd", "init"], cwd=cwd, capture_output=True, check=True)
        epic_result = subprocess.run(
            ["bd", "create", "--title", "Epic", "--type", "epic", "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        epic_id = extract_json(epic_result.stdout)["id"]

        run_layton("errands", "epic", "set", epic_id, cwd=cwd)

        result = run_layton("errands", "schedule", "nonexistent", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "ERRAND_NOT_FOUND"


class TestOrientationIncludesErrands:
    """E2E tests for orientation output with errands."""

    def test_orientation_includes_errands_array(
        self, temp_errands_dir, temp_config, real_beads_isolated
    ):
        """layton (no args) orientation includes errands field."""
        # Initialize beads via bd init
        cwd = temp_config.parent.parent
        subprocess.run(["bd", "init"], cwd=cwd, capture_output=True)

        # Create an errand
        (temp_errands_dir / "standup.md").write_text(
            """---
name: standup
description: Daily standup notes
---

## Task

Capture standup notes.
"""
        )

        # Initialize config
        temp_config.write_text("{}")

        result = run_layton(cwd=cwd)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "errands" in data["data"]
        assert len(data["data"]["errands"]) == 1
        assert data["data"]["errands"][0]["name"] == "standup"
        # Verify new orientation fields exist
        assert "beads_scheduled" in data["data"]
        assert "beads_pending_review" in data["data"]

    def test_orientation_includes_beads_scheduled(
        self, temp_errands_dir, temp_config, real_beads_isolated
    ):
        """layton (no args) shows scheduled beads from bd."""
        cwd = temp_config.parent.parent

        # Initialize beads
        subprocess.run(["bd", "init"], cwd=cwd, capture_output=True, check=True)

        # Create an epic
        epic_result = subprocess.run(
            ["bd", "create", "--title", "Test Epic", "--type", "epic", "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        epic_data = extract_json(epic_result.stdout)
        epic_id = epic_data["id"]

        # Set epic
        run_layton("errands", "epic", "set", epic_id, cwd=cwd)

        # Create an errand and schedule it
        (temp_errands_dir / "test-task.md").write_text(
            """---
name: test-task
description: A test task
---

## Task

Do something.
"""
        )

        result = run_layton("errands", "schedule", "test-task", cwd=cwd)
        assert result.returncode == 0

        # Now check orientation
        result = run_layton(cwd=cwd)
        assert result.returncode == 0
        data = json.loads(result.stdout)

        # Should have at least one scheduled bead
        assert "beads_scheduled" in data["data"]
        assert len(data["data"]["beads_scheduled"]) >= 1
        scheduled_titles = [b["title"] for b in data["data"]["beads_scheduled"]]
        assert any("test-task" in t for t in scheduled_titles)

    def test_orientation_includes_beads_pending_review(
        self, temp_errands_dir, temp_config, real_beads_isolated
    ):
        """layton (no args) shows beads pending review from bd."""
        cwd = temp_config.parent.parent

        # Initialize beads
        subprocess.run(["bd", "init"], cwd=cwd, capture_output=True, check=True)

        # Create an epic
        epic_result = subprocess.run(
            ["bd", "create", "--title", "Test Epic", "--type", "epic", "--json"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        epic_data = extract_json(epic_result.stdout)
        epic_id = epic_data["id"]

        # Set epic
        run_layton("errands", "epic", "set", epic_id, cwd=cwd)

        # Create an errand and schedule it
        (temp_errands_dir / "review-me.md").write_text(
            """---
name: review-me
description: A task to review
---

## Task

Review this.
"""
        )

        result = run_layton("errands", "schedule", "review-me", cwd=cwd)
        assert result.returncode == 0
        scheduled_data = json.loads(result.stdout)
        bead_id = scheduled_data["data"]["scheduled"]["id"]

        # Close the bead and add needs-review label (simulating executor completion)
        subprocess.run(
            ["bd", "close", bead_id], cwd=cwd, capture_output=True, check=True
        )
        subprocess.run(
            ["bd", "label", "add", bead_id, "needs-review"],
            cwd=cwd,
            capture_output=True,
            check=True,
        )

        # Now check orientation
        result = run_layton(cwd=cwd)
        assert result.returncode == 0
        data = json.loads(result.stdout)

        # Should have one bead pending review
        assert "beads_pending_review" in data["data"]
        assert len(data["data"]["beads_pending_review"]) >= 1
        pending_ids = [b["id"] for b in data["data"]["beads_pending_review"]]
        assert bead_id in pending_ids
