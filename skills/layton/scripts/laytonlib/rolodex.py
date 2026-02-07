"""Rolodex card management for Layton.

Rolodex cards are stored in .layton/rolodex/<name>.md with YAML frontmatter.
The CLI can list known cards, discover new cards, and bootstrap card files.
"""

import re
from dataclasses import dataclass
from pathlib import Path

from laytonlib.doctor import find_git_root, get_layton_dir


@dataclass
class RolodexCard:
    """Parsed rolodex card information."""

    name: str
    description: str
    source: str
    path: Path

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "path": str(self.path),
        }


@dataclass
class DiscoveredCard:
    """Card discovered from skills/*/SKILL.md."""

    name: str
    description: str
    source: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
        }


def get_rolodex_template() -> str:
    """Read the rolodex card template from the templates directory.

    Returns:
        The rolodex card template content with {name} placeholder.
    """
    # Template is in assets/templates/ relative to the skill root
    template_path = (
        Path(__file__).parent.parent.parent / "assets" / "templates" / "rolodex.md"
    )
    return template_path.read_text()


# Keep for backwards compatibility with tests
ROLODEX_TEMPLATE = get_rolodex_template()


def get_rolodex_dir() -> Path:
    """Get the .layton/rolodex/ directory path."""
    return get_layton_dir() / "rolodex"


def parse_frontmatter(content: str) -> dict | None:
    """Parse YAML frontmatter from markdown content.

    Args:
        content: Markdown file content

    Returns:
        Dict of frontmatter fields, or None if no valid frontmatter
    """
    # Match frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    result = {}

    # Simple YAML parsing for key: value pairs
    for line in frontmatter_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip()

    return result if result else None


def list_cards() -> list[RolodexCard]:
    """List all known cards from .layton/rolodex/.

    Returns:
        List of RolodexCard objects, sorted by name
    """
    cards_dir = get_rolodex_dir()
    if not cards_dir.exists():
        return []

    cards = []
    for path in cards_dir.glob("*.md"):
        if path.name == ".gitkeep":
            continue

        try:
            content = path.read_text()
            frontmatter = parse_frontmatter(content)
            if frontmatter and "name" in frontmatter:
                cards.append(
                    RolodexCard(
                        name=frontmatter.get("name", path.stem),
                        description=frontmatter.get("description", ""),
                        source=frontmatter.get("source", ""),
                        path=path,
                    )
                )
        except Exception:
            # Skip files that can't be read
            continue

    return sorted(cards, key=lambda c: c.name)


def discover_cards() -> tuple[list[RolodexCard], list[DiscoveredCard]]:
    """Discover cards by scanning skills/*/SKILL.md.

    Returns:
        Tuple of (known cards, unknown cards)
        - known: Cards with files in .layton/rolodex/
        - unknown: Cards without files (need to be added)
    """
    git_root = find_git_root()
    base = git_root if git_root else Path.cwd()
    skills_root = base / "skills"

    if not skills_root.exists():
        return [], []

    # Get current known cards
    known_cards = {c.name: c for c in list_cards()}

    # Scan for SKILL.md files
    known = []
    unknown = []

    for skill_md in skills_root.glob("*/SKILL.md"):
        skill_name = skill_md.parent.name

        # Exclude layton itself
        if skill_name == "layton":
            continue

        # Parse frontmatter from SKILL.md
        try:
            content = skill_md.read_text()
            frontmatter = parse_frontmatter(content)
            description = frontmatter.get("description", "") if frontmatter else ""
        except Exception:
            description = ""

        source = f"skills/{skill_name}/SKILL.md"

        if skill_name in known_cards:
            known.append(known_cards[skill_name])
        else:
            unknown.append(
                DiscoveredCard(
                    name=skill_name,
                    description=description,
                    source=source,
                )
            )

    return known, unknown


def add_card(name: str) -> Path:
    """Create a new rolodex card from template.

    Args:
        name: Card name (lowercase identifier)

    Returns:
        Path to the created file

    Raises:
        FileExistsError: If card already exists (code: CARD_EXISTS)
    """
    cards_dir = get_rolodex_dir()
    card_path = cards_dir / f"{name}.md"

    if card_path.exists():
        raise FileExistsError(f"Rolodex card already exists: {card_path}")

    # Create directory if needed
    cards_dir.mkdir(parents=True, exist_ok=True)

    # Write template
    content = ROLODEX_TEMPLATE.format(name=name)
    card_path.write_text(content)

    return card_path
