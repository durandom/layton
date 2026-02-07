"""E2E tests for layton protocols command."""

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


class TestProtocolsCommand:
    """E2E tests for layton protocols."""

    def test_protocols_outputs_json(self, isolated_env):
        """protocols outputs valid JSON by default."""
        result = run_layton("protocols", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "protocols" in data["data"]

    def test_protocols_empty(self, temp_protocols_dir):
        """protocols returns empty array when no protocols."""
        result = run_layton("protocols", cwd=temp_protocols_dir.parent.parent)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["data"]["protocols"] == []
        assert "next_steps" in data

    def test_protocols_lists_protocol(self, sample_protocol_file):
        """protocols lists protocol files from .layton/protocols/."""
        cwd = sample_protocol_file.parent.parent.parent
        result = run_layton("protocols", cwd=cwd)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["data"]["protocols"]) == 1
        protocol = data["data"]["protocols"][0]
        assert protocol["name"] == "sample"
        assert "description" in protocol
        assert "triggers" in protocol

    def test_protocols_human_output(self, temp_protocols_dir):
        """protocols --human outputs human-readable format."""
        result = run_layton(
            "protocols", "--human", cwd=temp_protocols_dir.parent.parent
        )

        # Human output should NOT be JSON
        try:
            json.loads(result.stdout)
            if result.stdout.strip():
                assert False, "Human output should not be JSON"
        except json.JSONDecodeError:
            pass  # Expected


class TestProtocolsAdd:
    """E2E tests for layton protocols add."""

    def test_add_creates_file(self, isolated_env):
        """protocols add creates protocol file."""
        result = run_layton("protocols", "add", "newprotocol", cwd=isolated_env)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "newprotocol" in data["data"]["created"]

        # Verify file exists
        protocol_path = isolated_env / ".layton" / "protocols" / "newprotocol.md"
        assert protocol_path.exists()

    def test_add_creates_directory(self, isolated_env):
        """protocols add creates .layton/protocols/ if missing."""
        protocols_dir = isolated_env / ".layton" / "protocols"
        if protocols_dir.exists():
            protocols_dir.rmdir()

        result = run_layton("protocols", "add", "newprotocol", cwd=isolated_env)

        assert result.returncode == 0
        assert protocols_dir.exists()

    def test_add_error_if_exists(self, sample_protocol_file):
        """protocols add returns error if protocol file exists."""
        cwd = sample_protocol_file.parent.parent.parent
        result = run_layton("protocols", "add", "sample", cwd=cwd)

        assert result.returncode == 1
        data = json.loads(result.stdout)
        assert data["error"]["code"] == "PROTOCOL_EXISTS"

    def test_add_template_has_required_sections(self, isolated_env):
        """protocols add creates file with required sections."""
        run_layton("protocols", "add", "testprotocol", cwd=isolated_env)

        protocol_path = isolated_env / ".layton" / "protocols" / "testprotocol.md"
        content = protocol_path.read_text()

        assert "## Objective" in content
        assert "## Steps" in content
        assert "## Context Adaptation" in content
        assert "## Success Criteria" in content
