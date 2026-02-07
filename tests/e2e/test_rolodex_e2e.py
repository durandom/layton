"""E2E tests for layton rolodex command."""

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


class TestRolodexCommand:
    """E2E tests for layton rolodex."""

    def test_rolodex_outputs_json(self, isolated_env):
        """rolodex outputs valid JSON by default."""
        result = run_layton("rolodex", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "rolodex" in data["data"]

    def test_rolodex_empty(self, temp_rolodex_dir):
        """rolodex returns empty array when no cards."""
        result = run_layton("rolodex", cwd=temp_rolodex_dir.parent.parent)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["rolodex"] == []
        assert "next_steps" in data

    def test_rolodex_lists_card(self, sample_rolodex_card):
        """rolodex lists cards from .layton/rolodex/."""
        cwd = sample_rolodex_card.parent.parent.parent
        result = run_layton("rolodex", cwd=cwd)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["data"]["rolodex"]) == 1
        card = data["data"]["rolodex"][0]
        assert card["name"] == "sample"
        assert "description" in card

    def test_rolodex_human_output(self, temp_rolodex_dir):
        """rolodex --human outputs human-readable format."""
        result = run_layton("rolodex", "--human", cwd=temp_rolodex_dir.parent.parent)

        # Human output should NOT be JSON
        try:
            json.loads(result.stdout)
            if result.stdout.strip():
                assert False, "Human output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected


class TestRolodexDiscover:
    """E2E tests for layton rolodex --discover."""

    def test_discover_finds_cards(self, isolated_env, temp_skills_root):
        """rolodex --discover finds cards from skills/*/SKILL.md."""
        skill_dir = temp_skills_root / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: myskill
description: Test skill
---
"""
        )

        result = run_layton("rolodex", "--discover", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "unknown" in data["data"]
        unknown_names = [c["name"] for c in data["data"]["unknown"]]
        assert "myskill" in unknown_names

    def test_discover_excludes_layton(self, isolated_env, temp_skills_root):
        """rolodex --discover excludes skills/layton/."""
        layton_dir = temp_skills_root / "layton"
        layton_dir.mkdir()
        (layton_dir / "SKILL.md").write_text(
            """---
name: layton
description: Should be excluded
---
"""
        )

        result = run_layton("rolodex", "--discover", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        unknown_names = [c["name"] for c in data["data"]["unknown"]]
        known_names = [c["name"] for c in data["data"]["known"]]
        assert "layton" not in unknown_names
        assert "layton" not in known_names


class TestRolodexAdd:
    """E2E tests for layton rolodex add."""

    def test_add_creates_file(self, isolated_env):
        """rolodex add creates card file."""
        result = run_layton("rolodex", "add", "newcard", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "newcard" in data["data"]["created"]

        # Verify file exists
        card_path = isolated_env / ".layton" / "rolodex" / "newcard.md"
        assert card_path.exists()

    def test_add_creates_directory(self, isolated_env):
        """rolodex add creates .layton/rolodex/ if missing."""
        rolodex_dir = isolated_env / ".layton" / "rolodex"
        if rolodex_dir.exists():
            rolodex_dir.rmdir()

        result = run_layton("rolodex", "add", "newcard", cwd=isolated_env)

        assert result.returncode == 0
        assert rolodex_dir.exists()

    def test_add_error_if_exists(self, sample_rolodex_card):
        """rolodex add returns error if card exists."""
        cwd = sample_rolodex_card.parent.parent.parent
        result = run_layton("rolodex", "add", "sample", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "CARD_EXISTS"
