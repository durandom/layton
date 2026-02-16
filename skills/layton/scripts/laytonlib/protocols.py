"""Protocol management for Layton.

Protocol files are stored in .layton/protocols/<name>.md with YAML frontmatter.
The CLI can list protocols and bootstrap new protocol files from templates.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from laytonlib.config import get_layton_dir


@dataclass
class ProtocolInfo:
    """Parsed protocol file information."""

    name: str
    description: str
    triggers: list[str] = field(default_factory=list)
    path: Path | None = None

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "triggers": self.triggers,
        }
        if self.path:
            result["path"] = str(self.path)
        return result


def get_protocol_template() -> str:
    """Read the protocol template from the templates directory.

    Returns:
        The protocol template content with {name} placeholder.
    """
    # Template is in assets/templates/ relative to the skill root
    template_path = (
        Path(__file__).parent.parent.parent / "assets" / "templates" / "protocol.md"
    )
    return template_path.read_text()


# Keep for backwards compatibility with tests
PROTOCOL_TEMPLATE = get_protocol_template()


def get_protocols_dir() -> Path:
    """Get the .layton/protocols/ directory path."""
    return get_layton_dir() / "protocols"


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
    current_key = None
    current_list = None

    # Simple YAML parsing for key: value pairs and lists
    for line in frontmatter_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check for list item (- value)
        if stripped.startswith("- ") and current_key:
            if current_list is None:
                current_list = []
            current_list.append(stripped[2:].strip())
            result[current_key] = current_list
            continue

        # Check for key: value
        if ":" in stripped:
            # Save previous list if any
            if current_list is not None and current_key:
                result[current_key] = current_list

            key, _, value = stripped.partition(":")
            current_key = key.strip()
            value = value.strip()

            if value:
                result[current_key] = value
                current_list = None
            else:
                # Might be start of a list
                current_list = []

    return result if result else None


def list_protocols() -> list[ProtocolInfo]:
    """List all protocols from .layton/protocols/.

    Returns:
        List of ProtocolInfo objects, sorted by name
    """
    protocols_dir = get_protocols_dir()
    if not protocols_dir.exists():
        return []

    protocols = []
    for path in protocols_dir.glob("*.md"):
        if path.name == ".gitkeep":
            continue

        try:
            content = path.read_text()
            frontmatter = parse_frontmatter(content)
            if frontmatter and "name" in frontmatter:
                triggers = frontmatter.get("triggers", [])
                if isinstance(triggers, str):
                    triggers = [triggers]
                protocols.append(
                    ProtocolInfo(
                        name=frontmatter.get("name", path.stem),
                        description=frontmatter.get("description", ""),
                        triggers=triggers,
                        path=path,
                    )
                )
        except Exception:
            # Skip files that can't be read
            continue

    return sorted(protocols, key=lambda w: w.name)


def add_protocol(name: str) -> Path:
    """Create a new protocol file from template.

    Args:
        name: Protocol name (lowercase identifier)

    Returns:
        Path to the created file

    Raises:
        FileExistsError: If protocol file already exists (code: PROTOCOL_EXISTS)
    """
    protocols_dir = get_protocols_dir()
    protocol_path = protocols_dir / f"{name}.md"

    if protocol_path.exists():
        raise FileExistsError(f"Protocol file already exists: {protocol_path}")

    # Create directory if needed
    protocols_dir.mkdir(parents=True, exist_ok=True)

    # Write template
    content = PROTOCOL_TEMPLATE.format(name=name)
    protocol_path.write_text(content)

    return protocol_path
