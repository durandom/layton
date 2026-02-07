"""Unit tests for rolodex module."""

import sys
from pathlib import Path

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "skills" / "layton" / "scripts"),
)

from laytonlib.rolodex import (
    ROLODEX_TEMPLATE,
    DiscoveredCard,
    RolodexCard,
    add_card,
    discover_cards,
    list_cards,
    parse_frontmatter,
)


class TestParseFrontmatter:
    """Tests for parse_frontmatter function."""

    def test_valid_frontmatter(self):
        """Parses valid YAML frontmatter."""
        content = """---
name: test
description: A test card
source: skills/test/SKILL.md
---

# Body content
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test card"
        assert result["source"] == "skills/test/SKILL.md"

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
description: A test card
---

# Body
"""
        result = parse_frontmatter(content)
        assert result is not None
        assert result["name"] == "test"
        assert result["description"] == "A test card"


class TestListCards:
    """Tests for list_cards function."""

    def test_empty_dir(self, temp_rolodex_dir):
        """Returns empty list when rolodex directory is empty."""
        result = list_cards()
        assert result == []

    def test_missing_dir(self, isolated_env):
        """Returns empty list when rolodex directory doesn't exist."""
        rolodex_dir = isolated_env / ".layton" / "rolodex"
        if rolodex_dir.exists():
            rolodex_dir.rmdir()
        result = list_cards()
        assert result == []

    def test_multiple_cards(self, temp_rolodex_dir):
        """Lists multiple cards sorted by name."""
        (temp_rolodex_dir / "zebra.md").write_text(
            """---
name: zebra
description: Last card
source: skills/zebra/SKILL.md
---
"""
        )
        (temp_rolodex_dir / "alpha.md").write_text(
            """---
name: alpha
description: First card
source: skills/alpha/SKILL.md
---
"""
        )

        result = list_cards()
        assert len(result) == 2
        assert result[0].name == "alpha"
        assert result[1].name == "zebra"

    def test_ignores_gitkeep(self, temp_rolodex_dir):
        """Ignores .gitkeep file."""
        (temp_rolodex_dir / ".gitkeep").touch()
        result = list_cards()
        assert result == []

    def test_skips_invalid_files(self, temp_rolodex_dir):
        """Skips files without valid frontmatter."""
        (temp_rolodex_dir / "invalid.md").write_text("No frontmatter here")
        (temp_rolodex_dir / "valid.md").write_text(
            """---
name: valid
description: Valid card
source: skills/valid/SKILL.md
---
"""
        )

        result = list_cards()
        assert len(result) == 1
        assert result[0].name == "valid"


class TestDiscoverCards:
    """Tests for discover_cards function."""

    def test_finds_cards(self, isolated_env, temp_skills_root):
        """Discovers cards from skills/*/SKILL.md."""
        skill_dir = temp_skills_root / "myskill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: myskill
description: My test skill
---
"""
        )

        known, unknown = discover_cards()
        assert len(unknown) == 1
        assert unknown[0].name == "myskill"
        assert unknown[0].description == "My test skill"

    def test_excludes_layton(self, isolated_env, temp_skills_root):
        """Excludes skills/layton/ from discovery."""
        layton_dir = temp_skills_root / "layton"
        layton_dir.mkdir()
        (layton_dir / "SKILL.md").write_text(
            """---
name: layton
description: Should be excluded
---
"""
        )

        known, unknown = discover_cards()
        assert not any(c.name == "layton" for c in unknown)
        assert not any(c.name == "layton" for c in known)

    def test_known_vs_unknown(self, isolated_env, temp_skills_root, temp_rolodex_dir):
        """Separates known (with card file) from unknown cards."""
        skill_dir = temp_skills_root / "discovered"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(
            """---
name: discovered
description: A discovered skill
---
"""
        )

        # Create known card file
        (temp_rolodex_dir / "discovered.md").write_text(
            """---
name: discovered
description: A discovered skill
source: skills/discovered/SKILL.md
---
"""
        )

        known, unknown = discover_cards()
        assert len(known) == 1
        assert known[0].name == "discovered"
        assert len(unknown) == 0


class TestAddCard:
    """Tests for add_card function."""

    def test_creates_file(self, temp_rolodex_dir):
        """Creates card from template."""
        path = add_card("newcard")

        assert path.exists()
        assert path.name == "newcard.md"
        content = path.read_text()
        assert "name: newcard" in content

    def test_creates_directory(self, isolated_env):
        """Creates .layton/rolodex/ if it doesn't exist."""
        rolodex_dir = isolated_env / ".layton" / "rolodex"
        if rolodex_dir.exists():
            rolodex_dir.rmdir()

        path = add_card("newcard")

        assert rolodex_dir.exists()
        assert path.exists()

    def test_error_if_exists(self, temp_rolodex_dir):
        """Raises FileExistsError if card already exists."""
        (temp_rolodex_dir / "existing.md").write_text("existing content")

        try:
            add_card("existing")
            assert False, "Should have raised FileExistsError"
        except FileExistsError as e:
            assert "already exists" in str(e)


class TestRolodexTemplate:
    """Tests for rolodex template."""

    def test_has_required_sections(self):
        """Template has required sections."""
        assert "## Commands" in ROLODEX_TEMPLATE
        assert "## What to Extract" in ROLODEX_TEMPLATE
        assert "## Key Metrics" in ROLODEX_TEMPLATE

    def test_has_frontmatter_placeholders(self):
        """Template has frontmatter placeholders."""
        assert "name: {name}" in ROLODEX_TEMPLATE
        assert "description:" in ROLODEX_TEMPLATE
        assert "source:" in ROLODEX_TEMPLATE


class TestRolodexCard:
    """Tests for RolodexCard dataclass."""

    def test_to_dict(self, tmp_path):
        """to_dict returns proper dictionary."""
        path = tmp_path / "test.md"
        card = RolodexCard(
            name="test",
            description="Test card",
            source="skills/test/SKILL.md",
            path=path,
        )
        d = card.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test card"
        assert d["source"] == "skills/test/SKILL.md"
        assert d["path"] == str(path)


class TestDiscoveredCard:
    """Tests for DiscoveredCard dataclass."""

    def test_to_dict(self):
        """to_dict returns proper dictionary."""
        card = DiscoveredCard(
            name="test",
            description="Test card",
            source="skills/test/SKILL.md",
        )
        d = card.to_dict()

        assert d["name"] == "test"
        assert d["description"] == "Test card"
        assert d["source"] == "skills/test/SKILL.md"
