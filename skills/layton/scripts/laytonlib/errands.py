"""Errand management for Layton.

Errands are stored in .layton/errands/<name>.md with YAML frontmatter.
Errands use `${variable}` syntax for runtime substitution via string.Template.
The CLI can list errands, add new ones, and schedule errands from definitions.
"""

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from string import Template

from laytonlib.config import get_nested, load_config, save_config, set_nested
from laytonlib.doctor import get_layton_dir


# Fixed labels for bead state management
LABEL_SCHEDULED = "scheduled"
LABEL_IN_PROGRESS = "in-progress"
LABEL_NEEDS_REVIEW = "needs-review"


@dataclass
class ErrandInfo:
    """Parsed errand information."""

    name: str
    description: str
    variables: dict[str, str] = field(default_factory=dict)
    path: Path | None = None

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "variables": self.variables,
        }
        if self.path:
            result["path"] = str(self.path)
        return result


def get_errand_template() -> str:
    """Read the errand template from the templates directory.

    Returns:
        The errand template content with {name} placeholder.
    """
    template_path = (
        Path(__file__).parent.parent.parent / "assets" / "templates" / "errand.md"
    )
    return template_path.read_text()


# Keep for backwards compatibility with tests
ERRAND_TEMPLATE = get_errand_template()


def get_errands_dir() -> Path:
    """Get the .layton/errands/ directory path."""
    return get_layton_dir() / "errands"


def parse_frontmatter(content: str) -> dict | None:
    """Parse YAML frontmatter from markdown content with variables section.

    Args:
        content: Markdown file content

    Returns:
        Dict of frontmatter fields, or None if no valid frontmatter.
        The 'variables' key contains a dict of {variable_name: description}.
    """
    # Match frontmatter between --- markers
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter_text = match.group(1)
    result = {}
    in_variables = False
    variables = {}

    for line in frontmatter_text.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check if this is the variables section start
        if stripped == "variables:":
            in_variables = True
            continue

        # Check for indented variable definition (in variables section)
        if in_variables and line.startswith("  ") and ":" in stripped:
            # Parse variable_name: description
            var_name, _, var_desc = stripped.partition(":")
            variables[var_name.strip()] = var_desc.strip()
            continue

        # Non-indented line ends variables section
        if in_variables and not line.startswith("  ") and ":" in stripped:
            in_variables = False

        # Regular key: value
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            result[key.strip()] = value.strip()

    # Add variables to result if any were found
    if variables:
        result["variables"] = variables

    return result if result else None


def list_errands() -> list[ErrandInfo]:
    """List all errands from .layton/errands/.

    Returns:
        List of ErrandInfo objects, sorted by name
    """
    errands_dir = get_errands_dir()
    if not errands_dir.exists():
        return []

    errands = []
    for path in errands_dir.glob("*.md"):
        if path.name == ".gitkeep":
            continue

        try:
            content = path.read_text()
            frontmatter = parse_frontmatter(content)
            if frontmatter and "name" in frontmatter:
                errands.append(
                    ErrandInfo(
                        name=frontmatter.get("name", path.stem),
                        description=frontmatter.get("description", ""),
                        variables=frontmatter.get("variables", {}),
                        path=path,
                    )
                )
        except Exception:
            # Skip files that can't be read
            continue

    return sorted(errands, key=lambda e: e.name)


def add_errand(name: str) -> Path:
    """Create a new errand from template.

    Args:
        name: Errand name (lowercase identifier)

    Returns:
        Path to the created file

    Raises:
        FileExistsError: If errand already exists (code: ERRAND_EXISTS)
    """
    errands_dir = get_errands_dir()
    errand_path = errands_dir / f"{name}.md"

    if errand_path.exists():
        raise FileExistsError(f"Errand already exists: {errand_path}")

    # Create directory if needed
    errands_dir.mkdir(parents=True, exist_ok=True)

    # Write template with name substituted
    content = ERRAND_TEMPLATE.format(name=name)
    errand_path.write_text(content)

    return errand_path


def load_errand(name: str) -> tuple[ErrandInfo, str] | None:
    """Load a specific errand for scheduling.

    Args:
        name: Errand name

    Returns:
        Tuple of (ErrandInfo, body_content) or None if not found
    """
    errands_dir = get_errands_dir()
    errand_path = errands_dir / f"{name}.md"

    if not errand_path.exists():
        return None

    content = errand_path.read_text()
    frontmatter = parse_frontmatter(content)
    if not frontmatter:
        return None

    # Extract body (everything after second ---)
    match = re.match(r"^---\s*\n.*?\n---\s*\n(.*)$", content, re.DOTALL)
    body = match.group(1) if match else ""

    info = ErrandInfo(
        name=frontmatter.get("name", name),
        description=frontmatter.get("description", ""),
        variables=frontmatter.get("variables", {}),
        path=errand_path,
    )

    return info, body


def get_epic() -> str | None:
    """Get the configured epic ID from config.

    Returns:
        Epic ID string, or None if not configured
    """
    config = load_config()
    if not config:
        return None
    try:
        return get_nested(config, "errands.epic")
    except KeyError:
        return None


def set_epic(epic_id: str) -> bool:
    """Set the epic ID in config.

    Args:
        epic_id: The epic ID to store

    Returns:
        True on success, False on failure
    """
    config = load_config()
    if config is None:
        config = {}

    set_nested(config, "errands.epic", epic_id)
    return save_config(config)


def create_epic(name: str = "Background Tasks") -> str:
    """Create a new epic via bd CLI and return its ID.

    Args:
        name: Epic title (defaults to "Background Tasks")

    Returns:
        The created epic's ID

    Raises:
        RuntimeError: If bd CLI unavailable (code: BD_UNAVAILABLE)
        RuntimeError: If bd create fails (code: BD_ERROR)
    """
    if not shutil.which("bd"):
        raise RuntimeError("BD_UNAVAILABLE: bd CLI not found")

    cmd = ["bd", "create", "--title", name, "--type", "epic", "--json"]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        # bd may return "id" or "number" depending on version
        epic_id = data.get("id") or data.get("number")
        if not epic_id:
            raise RuntimeError(f"BD_ERROR: No ID in response: {result.stdout}")
        return str(epic_id)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"BD_ERROR: {e.stderr or e.stdout or str(e)}")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"BD_ERROR: Invalid JSON response: {e}")


def ensure_epic() -> str:
    """Get or create the epic, storing in config.

    This function makes epic management transparent—users never need to
    manually create or configure an epic. On first errand schedule, the epic
    is auto-created.

    Returns:
        Epic ID string (existing or newly created)

    Raises:
        RuntimeError: If bd CLI unavailable (code: BD_UNAVAILABLE)
        RuntimeError: If epic creation fails (code: BD_ERROR)
    """
    epic = get_epic()
    if epic:
        return epic

    # Auto-create epic
    epic_id = create_epic()
    set_epic(epic_id)
    return epic_id


def get_beads_by_label(label: str, status: str | None = None) -> list[dict]:
    """Query bd for beads with a specific label.

    Args:
        label: Label to filter by (e.g., "scheduled", "needs-review")
        status: Optional status filter ("open", "closed", etc.)

    Returns:
        List of bead dicts from bd list, or empty list if bd unavailable/fails
    """
    if not shutil.which("bd"):
        return []

    cmd = ["bd", "list", "-l", label, "--json", "--limit", "0"]
    if status:
        cmd.extend(["-s", status])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse JSON output (may have warning lines before JSON)
        output = result.stdout
        # Find where JSON array starts
        arr_start = output.find("[")
        if arr_start == -1:
            return []
        return json.loads(output[arr_start:])
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return []


def get_beads_pending_review() -> list[dict]:
    """Get closed beads with the needs-review label.

    Returns:
        List of bead dicts awaiting review
    """
    return get_beads_by_label(LABEL_NEEDS_REVIEW, status="closed")


def get_beads_scheduled() -> list[dict]:
    """Get open beads with the scheduled label.

    Returns:
        List of bead dicts that are scheduled for execution
    """
    return get_beads_by_label(LABEL_SCHEDULED, status="open")


def get_beads_in_progress() -> list[dict]:
    """Get open beads with the in-progress label.

    Returns:
        List of bead dicts that are currently being executed
    """
    return get_beads_by_label(LABEL_IN_PROGRESS, status="open")


def schedule_errand(name: str, variables: dict[str, str] | None = None) -> dict:
    """Schedule an errand for execution.

    Args:
        name: Errand name
        variables: Variables to substitute (using string.Template)

    Returns:
        Dict with scheduled bead info or error

    Raises:
        FileNotFoundError: If errand not found (code: ERRAND_NOT_FOUND)
        RuntimeError: If bd CLI unavailable (code: BD_UNAVAILABLE)
        RuntimeError: If no epic configured (code: NO_EPIC)
        RuntimeError: If bd create fails (code: BD_ERROR)
    """
    # Check bd availability
    if not shutil.which("bd"):
        raise RuntimeError("BD_UNAVAILABLE: bd CLI not found")

    # Get epic (must be configured before scheduling)
    epic = get_epic()
    if not epic:
        raise RuntimeError("NO_EPIC: Epic not configured")

    # Load errand
    result = load_errand(name)
    if not result:
        raise FileNotFoundError(f"ERRAND_NOT_FOUND: {name}")

    info, body = result
    variables = variables or {}

    # Substitute variables using string.Template (safe_substitute leaves missing vars as-is)
    template = Template(body)
    rendered_body = template.safe_substitute(variables)

    # Build title from errand name
    title = f"[{name}] {info.description}" if info.description else f"[{name}]"

    # Create bead via bd
    return bd_create(
        title=title,
        parent=epic,
        labels=[LABEL_SCHEDULED, f"type:{name}"],
        description=rendered_body,
    )


def get_bead(bead_id: str) -> dict | None:
    """Fetch a single bead by ID via bd show.

    Args:
        bead_id: The bead ID to fetch

    Returns:
        Bead dict or None if not found / bd unavailable
    """
    if not shutil.which("bd"):
        return None

    try:
        result = subprocess.run(
            ["bd", "show", bead_id, "--json"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout
        # bd show --json returns an array with one element
        arr_start = output.find("[")
        if arr_start == -1:
            # Try parsing as object
            obj_start = output.find("{")
            if obj_start == -1:
                return None
            data = json.loads(output[obj_start:])
            return data
        data = json.loads(output[arr_start:])
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return None


def get_bead_comments(bead_id: str) -> str:
    """Fetch comments for a bead via bd comments.

    Args:
        bead_id: The bead ID

    Returns:
        Raw comments text, or empty string if none / bd unavailable
    """
    if not shutil.which("bd"):
        return ""

    try:
        result = subprocess.run(
            ["bd", "comments", bead_id],
            capture_output=True,
            text=True,
            check=True,
        )
        text = result.stdout.strip()
        # Filter out bd warning/note lines and check for "no comments" sentinel
        lines = [
            line for line in text.split("\n")
            if not line.startswith(("Note:", "Warning:", "⚠"))
        ]
        filtered = "\n".join(lines).strip()
        if filtered.startswith("No comments on"):
            return ""
        return filtered
    except subprocess.CalledProcessError:
        return ""


def _transition_to_in_progress(bead_id: str) -> bool:
    """Swap scheduled label to in-progress on a bead.

    Best-effort: never blocks prompt delivery. Returns False on any failure.

    Args:
        bead_id: The bead ID to transition

    Returns:
        True if both label commands succeeded, False otherwise
    """
    if not shutil.which("bd"):
        return False

    try:
        subprocess.run(
            ["bd", "label", "remove", bead_id, LABEL_SCHEDULED],
            capture_output=True,
            text=True,
            check=True,
        )
        subprocess.run(
            ["bd", "label", "add", bead_id, LABEL_IN_PROGRESS],
            capture_output=True,
            text=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def build_prompt(bead_id: str) -> str | None:
    """Assemble an execution prompt for a scheduled bead.

    Fetches the bead and its comments, then builds a self-contained
    prompt that a subagent can follow to execute the errand.
    Transitions the bead from scheduled to in-progress (best-effort).

    Args:
        bead_id: The bead ID

    Returns:
        Execution prompt string, or None if bead not found
    """
    bead = get_bead(bead_id)
    if not bead:
        return None

    _transition_to_in_progress(bead_id)

    title = bead.get("title", "Untitled")
    description = bead.get("description", "")
    comments = get_bead_comments(bead_id)

    parts = [f"# Errand: {bead_id} — {title}", "", description]

    if comments:
        parts.extend(["", "## Context (prior comments)", "", comments])

    parts.extend([
        "",
        "## Completion Protocol",
        "",
        "1. Add findings:",
        f'   ```bash',
        f'   bd comments add {bead_id} "## Summary\\n\\n<findings>"',
        f'   ```',
        "",
        "2. Remove in-progress label:",
        f'   ```bash',
        f'   bd label remove {bead_id} in-progress',
        f'   ```',
        "",
        "3. Close:",
        f'   ```bash',
        f'   bd close {bead_id}',
        f'   ```',
        "",
        "4. Label for review:",
        f'   ```bash',
        f'   bd label add {bead_id} needs-review',
        f'   ```',
        "",
        f'If BLOCKED: `bd comments add {bead_id} "BLOCKED: <reason>"` — do NOT close.',
    ])

    return "\n".join(parts)


def bd_create(
    title: str,
    parent: str,
    labels: list[str],
    description: str,
) -> dict:
    """Create a bead via bd CLI.

    Args:
        title: Bead title
        parent: Parent epic ID
        labels: Labels to apply
        description: Bead description/body

    Returns:
        Dict with created bead info

    Raises:
        RuntimeError: If bd create fails (code: BD_ERROR)
    """
    cmd = ["bd", "create", "--title", title, "--parent", parent, "--json"]

    if labels:
        cmd.extend(["--labels", ",".join(labels)])

    cmd.extend(["--description", description])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            stdin=subprocess.DEVNULL,
        )
        # Parse bd output - typically returns JSON with bead ID
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            # Return raw output if not JSON
            return {"output": result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"BD_ERROR: {e.stderr or e.stdout or str(e)}")
