"""Unit tests for protocols module."""

import sys
from pathlib import Path

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "skills" / "layton" / "scripts"),
)

from laytonlib.protocols import (
    PROTOCOL_TEMPLATE,
    ProtocolInfo,
    add_protocol,
    list_protocols,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_valid_frontmatter(self):
        """Parses valid YAML frontmatter."""
        content = """---
name: test
description: A test protocol
triggers:
  - hello
  - hi there
---

# Body content
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test protocol"
        assert result["triggers"] == ["hello", "hi there"]

    def test_no_frontmatter(self):
        """Returns None for content without frontmatter."""
        content = "# Just a header\n\nSome content."
        result = parse_frontmatter(content)
        assert result is None

    def test_empty_frontmatter(self):
        """Returns None for empty frontmatter."""
        content = """---
---

# Body content
"""
        result = parse_frontmatter(content)
        assert result is None

    def test_frontmatter_with_comments(self):
        """Skips comment lines in frontmatter."""
        content = """---
name: test
# This is a comment
description: A test protocol
---

# Body
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test protocol"

    def test_frontmatter_with_list(self):
        """Parses list values correctly."""
        content = """---
name: test
triggers:
  - trigger one
  - trigger two
  - trigger three
---
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["triggers"] == ["trigger one", "trigger two", "trigger three"]


class TestListProtocols:
    """Tests for list_protocols function."""

    def test_empty_dir(self, temp_protocols_dir):
        """Returns empty list when protocols directory is empty."""
        result = list_protocols()
        assert result == []

    def test_missing_dir(self, isolated_env):
        """Returns empty list when protocols directory doesn't exist."""
        # Remove the protocols dir created by fixture
        protocols_dir = isolated_env / ".layton" / "protocols"
        if protocols_dir.exists():
            protocols_dir.rmdir()
        result = list_protocols()
        assert result == []

    def test_multiple_protocols(self, temp_protocols_dir):
        """Lists multiple protocol files sorted by name."""
        # Create protocol files
        (temp_protocols_dir / "zebra.md").write_text(
            """---
name: zebra
description: Last protocol
triggers:
  - z
---
"""
        )
        (temp_protocols_dir / "alpha.md").write_text(
            """---
name: alpha
description: First protocol
triggers:
  - a
---
"""
        )

        result = list_protocols()
        assert len(result) == 2
        assert result[0].name == "alpha"
        assert result[1].name == "zebra"

    def test_ignores_gitkeep(self, temp_protocols_dir):
        """Ignores .gitkeep file."""
        (temp_protocols_dir / ".gitkeep").touch()
        result = list_protocols()
        assert result == []

    def test_skips_invalid_files(self, temp_protocols_dir):
        """Skips files without valid frontmatter."""
        (temp_protocols_dir / "invalid.md").write_text("No frontmatter here")
        (temp_protocols_dir / "valid.md").write_text(
            """---
name: valid
description: Valid protocol
triggers:
  - test
---
"""
        )

        result = list_protocols()
        assert len(result) == 1
        assert result[0].name == "valid"


class TestAddProtocol:
    """Tests for add_protocol function."""

    def test_creates_file(self, temp_protocols_dir):
        """Creates protocol file from template."""
        path = add_protocol("newprotocol")

        assert path.exists()
        assert path.name == "newprotocol.md"
        content = path.read_text()
        assert "name: newprotocol" in content

    def test_creates_directory(self, isolated_env):
        """Creates .layton/protocols/ if it doesn't exist."""
        protocols_dir = isolated_env / ".layton" / "protocols"
        if protocols_dir.exists():
            protocols_dir.rmdir()

        path = add_protocol("newprotocol")

        assert protocols_dir.exists()
        assert path.exists()

    def test_error_if_exists(self, temp_protocols_dir):
        """Raises FileExistsError if protocol file already exists."""
        (temp_protocols_dir / "existing.md").write_text("existing content")

        try:
            add_protocol("existing")
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            assert "already exists" in str(e)


class TestProtocolTemplate:
    """Tests for protocol template."""

    def test_has_required_sections(self):
        """Template has required sections."""
        assert "## Objective" in PROTOCOL_TEMPLATE
        assert "## Steps" in PROTOCOL_TEMPLATE
        assert "## Context Adaptation" in PROTOCOL_TEMPLATE
        assert "## Success Criteria" in PROTOCOL_TEMPLATE

    def test_has_frontmatter_placeholders(self):
        """Template has frontmatter placeholders."""
        assert "name: {name}" in PROTOCOL_TEMPLATE
        assert "description:" in PROTOCOL_TEMPLATE
        assert "triggers:" in PROTOCOL_TEMPLATE


class TestProtocolInfo:
    """Tests for ProtocolInfo dataclass."""

    def test_to_dict(self, tmp_path):
        """to_dict returns proper dictionary."""
        path = tmp_path / "test.md"
        protocol = ProtocolInfo(
            name="test",
            description="Test protocol",
            triggers=["hello", "hi"],
            path=path,
        )
        d = protocol.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test protocol"
        assert d["triggers"] == ["hello", "hi"]
        assert d["path"] == str(path)

    def test_to_dict_no_path(self):
        """to_dict without path."""
        protocol = ProtocolInfo(
            name="test",
            description="Test protocol",
            triggers=["hello"],
        )
        d = protocol.to_dict()

        assert d["name"] == "test"
        assert "path" not in d

    def test_default_triggers(self):
        """Default triggers is empty list."""
        protocol = ProtocolInfo(name="test", description="Test")
        assert protocol.triggers == []


# Path to the Layton skill directory
LAYTON_SKILL_DIR = Path(__file__).parent.parent.parent / "skills" / "layton"


class TestBuiltinProtocols:
    """Tests for built-in protocol files in skills/layton/protocols/."""

    def test_audit_protocol_exists(self):
        """Audit protocol file exists at expected path."""
        protocol_path = (
            LAYTON_SKILL_DIR
            / "references"
            / "protocols"
            / "audit-project-instructions.md"
        )
        assert protocol_path.exists(), f"Missing protocol at {protocol_path}"

    def test_audit_protocol_triggers(self):
        """Audit protocol has appropriate triggers."""
        protocol_path = (
            LAYTON_SKILL_DIR
            / "references"
            / "protocols"
            / "audit-project-instructions.md"
        )
        content = protocol_path.read_text()
        fm = parse_frontmatter(content)

        assert fm is not None, "Protocol should have valid frontmatter"
        assert "triggers" in fm, "Protocol should have triggers"

        triggers_lower = [t.lower() for t in fm["triggers"]]
        # Check for expected trigger phrases
        assert any("audit" in t for t in triggers_lower), (
            "Should have trigger with 'audit'"
        )
        assert any("claude" in t or "instruction" in t for t in triggers_lower), (
            "Should have trigger mentioning claude or instructions"
        )

    def test_retrospect_protocol_exists(self):
        """Retrospect protocol file exists at expected path."""
        protocol_path = LAYTON_SKILL_DIR / "references" / "protocols" / "retrospect.md"
        assert protocol_path.exists(), f"Missing protocol at {protocol_path}"

    def test_retrospect_protocol_triggers(self):
        """Retrospect protocol has appropriate triggers."""
        protocol_path = LAYTON_SKILL_DIR / "references" / "protocols" / "retrospect.md"
        content = protocol_path.read_text()
        fm = parse_frontmatter(content)

        assert fm is not None, "Protocol should have valid frontmatter"
        assert "triggers" in fm, "Protocol should have triggers"

        triggers_lower = [t.lower() for t in fm["triggers"]]
        # Check for expected trigger phrases
        assert any("retrospect" in t or "reflect" in t for t in triggers_lower), (
            "Should have trigger with 'retrospect' or 'reflect'"
        )

    def test_setup_mentions_audit_protocol(self):
        """Setup protocol mentions audit protocol as optional step."""
        protocol_path = LAYTON_SKILL_DIR / "references" / "protocols" / "setup.md"
        content = protocol_path.read_text().lower()

        assert "audit" in content, "Setup protocol should mention audit protocol"
        # Check it's presented as optional
        assert "would you like" in content or "optional" in content, (
            "Audit mention should be presented as optional"
        )
