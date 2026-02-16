"""Layton CLI - argparse structure with global options."""

import argparse
import sys

from laytonlib import __version__
from laytonlib.formatters import OutputFormatter


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser with all commands."""
    parser = argparse.ArgumentParser(
        prog="layton",
        description="Personal AI assistant for attention management",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--human",
        action="store_true",
        help="Human-readable output (default is JSON)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include debug information",
    )

    subparsers = parser.add_subparsers(dest="command")

    # doctor command
    doctor_parser = subparsers.add_parser("doctor", help="Check system health")
    # Hidden --fix flag (not shown in help, but works)
    doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help=argparse.SUPPRESS,  # Hidden from help
    )

    # config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command")

    # config init
    config_init = config_subparsers.add_parser("init", help="Create default config")
    config_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing config",
    )

    # config show
    config_subparsers.add_parser("show", help="Display current config")

    # config keys
    config_subparsers.add_parser("keys", help="List all config keys")

    # config get
    config_get = config_subparsers.add_parser("get", help="Get a config value")
    config_get.add_argument(
        "key", help="Key in dot notation (e.g., work.schedule.start)"
    )

    # config set
    config_set = config_subparsers.add_parser("set", help="Set a config value")
    config_set.add_argument("key", help="Key in dot notation")
    config_set.add_argument("value", help="Value to set (JSON parsed if valid)")

    # context command
    subparsers.add_parser("context", help="Show temporal context")

    # rolodex command
    rolodex_parser = subparsers.add_parser("rolodex", help="Manage rolodex cards")
    rolodex_parser.add_argument(
        "--discover",
        action="store_true",
        help="Discover cards from skills/*/SKILL.md",
    )
    rolodex_subparsers = rolodex_parser.add_subparsers(dest="rolodex_command")

    # rolodex add
    rolodex_add = rolodex_subparsers.add_parser("add", help="Create new rolodex card")
    rolodex_add.add_argument("name", help="Card name (lowercase identifier)")

    # protocols command
    protocols_parser = subparsers.add_parser("protocols", help="Manage protocols")
    protocols_subparsers = protocols_parser.add_subparsers(dest="protocols_command")

    # protocols add
    protocols_add = protocols_subparsers.add_parser(
        "add", help="Create new protocol file"
    )
    protocols_add.add_argument("name", help="Protocol name (lowercase identifier)")

    # errands command
    errands_parser = subparsers.add_parser("errands", help="Manage errands")
    errands_subparsers = errands_parser.add_subparsers(dest="errands_command")

    # errands add
    errands_add = errands_subparsers.add_parser("add", help="Create new errand")
    errands_add.add_argument("name", help="Errand name (lowercase identifier)")

    # errands schedule
    errands_schedule = errands_subparsers.add_parser(
        "schedule", help="Schedule an errand"
    )
    errands_schedule.add_argument("name", help="Errand name")
    errands_schedule.add_argument(
        "json_vars",
        nargs="?",
        default=None,
        help="Variables as JSON (or pipe via stdin)",
    )

    # errands epic (get/set)
    errands_epic = errands_subparsers.add_parser("epic", help="Manage epic ID")
    errands_epic.add_argument(
        "action",
        nargs="?",
        choices=["set"],
        help="Action (omit to show current epic)",
    )
    errands_epic.add_argument("epic_id", nargs="?", help="Epic ID to set")

    # errands run — schedule + return bead ID (subagent fetches prompt separately)
    errands_run = errands_subparsers.add_parser(
        "run", help="Schedule errand for execution"
    )
    errands_run.add_argument("name", help="Errand name")
    errands_run.add_argument(
        "json_vars",
        nargs="?",
        default=None,
        help="Variables as JSON",
    )

    # errands prompt — subagent calls this to get execution instructions
    errands_prompt = errands_subparsers.add_parser(
        "prompt", help="Get execution prompt for a scheduled bead"
    )
    errands_prompt.add_argument("bead_id", help="Bead ID")

    return parser


def run_orientation(formatter: OutputFormatter) -> int:
    """Run orientation - combined doctor + rolodex + protocols + errands.

    Args:
        formatter: Output formatter

    Returns:
        Exit code (0=success, 1=fixable, 2=critical)
    """
    from laytonlib.errands import (
        get_beads_in_progress,
        get_beads_pending_review,
        get_beads_scheduled,
        list_errands,
    )
    from laytonlib.doctor import (
        check_beads_available,
        check_beads_initialized,
        check_config_exists,
        check_config_valid,
    )
    from laytonlib.rolodex import list_cards
    from laytonlib.protocols import list_protocols

    # Run doctor checks
    checks = []
    next_steps = []

    beads_check = check_beads_available()
    checks.append(beads_check)

    if beads_check.status == "fail":
        formatter.error(
            "BEADS_UNAVAILABLE",
            beads_check.message,
            next_steps=["Install Beads CLI: https://github.com/steveyegge/beads"],
        )
        return 2

    beads_init_check = check_beads_initialized()
    checks.append(beads_init_check)
    if beads_init_check.status == "warn":
        next_steps.append("Run 'bd init' to initialize Beads")

    config_exists_check = check_config_exists()
    checks.append(config_exists_check)

    needs_setup = config_exists_check.status == "fail"

    if config_exists_check.status == "pass":
        config_valid_check = check_config_valid()
        checks.append(config_valid_check)

    if needs_setup:
        next_steps.append("Follow references/protocols/setup.md for guided onboarding")
        next_steps.append("Or run 'layton config init' for quick setup")

    # Get rolodex cards inventory
    cards = list_cards()
    cards_data = [{"name": c.name, "description": c.description} for c in cards]

    if not cards:
        next_steps.append("Run 'layton rolodex --discover' to find available cards")

    # Get protocols inventory
    protocols = list_protocols()
    protocols_data = [
        {"name": w.name, "description": w.description, "triggers": w.triggers}
        for w in protocols
    ]

    if not protocols:
        next_steps.append("Run 'layton protocols add <name>' to create a protocol")

    # Get errands inventory
    errands = list_errands()
    errands_data = [
        {"name": e.name, "description": e.description, "variables": e.variables}
        for e in errands
    ]

    # Get errand queue states (from bd)
    beads_scheduled = get_beads_scheduled()
    beads_in_progress = get_beads_in_progress()
    beads_pending_review = get_beads_pending_review()

    # Add protocol hints based on beads status
    if beads_pending_review:
        next_steps.append(
            f"{len(beads_pending_review)} bead(s) pending review - see references/protocols/review-beads.md"
        )

    # Build output
    data = {
        "needs_setup": needs_setup,
        "checks": [c.to_dict() for c in checks],
        "rolodex": cards_data,
        "protocols": protocols_data,
        "errands": {
            "templates": errands_data,
            "queue": {
                "scheduled": beads_scheduled,
                "in_progress": beads_in_progress,
                "pending_review": beads_pending_review,
            },
        },
    }

    if next_steps:
        data["next_steps"] = next_steps

    formatter.success(data, next_steps=next_steps if next_steps else None)
    return 0


def run_rolodex(
    formatter: OutputFormatter,
    command: str | None,
    discover: bool,
    name: str | None,
) -> int:
    """Run rolodex command.

    Args:
        formatter: Output formatter
        command: Subcommand (add, or None for list)
        discover: Whether to run discovery
        name: Card name for add command

    Returns:
        Exit code (0=success, 1=error)
    """
    from laytonlib.rolodex import add_card, discover_cards, list_cards

    if command == "add":
        if not name:
            formatter.error("MISSING_NAME", "Card name is required")
            return 1

        try:
            path = add_card(name)
            formatter.success(
                {"created": str(path), "name": name},
                next_steps=[f"Edit {path} to configure the card"],
            )
            return 0
        except FileExistsError as e:
            formatter.error(
                "CARD_EXISTS",
                str(e),
                next_steps=["Review existing card or choose a different name"],
            )
            return 1

    elif discover:
        known, unknown = discover_cards()
        next_steps = []
        if unknown:
            next_steps.append(
                f"Run 'layton rolodex add <name>' to create cards for: "
                f"{', '.join(c.name for c in unknown)}"
            )
        formatter.success(
            {
                "known": [c.to_dict() for c in known],
                "unknown": [c.to_dict() for c in unknown],
            },
            next_steps=next_steps if next_steps else None,
        )
        return 0

    else:
        # Default: list cards
        cards = list_cards()
        next_steps = []
        if not cards:
            next_steps.append("Run 'layton rolodex --discover' to find available cards")
            next_steps.append("Run 'layton rolodex add <name>' to create a card")
        formatter.success(
            {"rolodex": [c.to_dict() for c in cards]},
            next_steps=next_steps if next_steps else None,
        )
        return 0


def run_protocols(
    formatter: OutputFormatter,
    command: str | None,
    name: str | None,
) -> int:
    """Run protocols command.

    Args:
        formatter: Output formatter
        command: Subcommand (add, or None for list)
        name: Protocol name for add command

    Returns:
        Exit code (0=success, 1=error)
    """
    from laytonlib.protocols import add_protocol, list_protocols

    if command == "add":
        if not name:
            formatter.error("MISSING_NAME", "Protocol name is required")
            return 1

        try:
            path = add_protocol(name)
            formatter.success(
                {"created": str(path), "name": name},
                next_steps=[f"Edit {path} to configure the protocol"],
            )
            return 0
        except FileExistsError as e:
            formatter.error(
                "PROTOCOL_EXISTS",
                str(e),
                next_steps=["Review existing protocol file or choose a different name"],
            )
            return 1

    else:
        # Default: list protocols
        protocols = list_protocols()
        next_steps = []
        if not protocols:
            next_steps.append("Run 'layton protocols add <name>' to create a protocol")
        formatter.success(
            {"protocols": [w.to_dict() for w in protocols]},
            next_steps=next_steps if next_steps else None,
        )
        return 0


def _parse_json_vars(json_vars_arg: str | None) -> dict | None:
    """Parse JSON variables from argument or stdin.

    Args:
        json_vars_arg: JSON string from CLI argument, or None

    Returns:
        Parsed dict, empty dict if no input, or None on parse error
        (caller should emit INVALID_JSON error on None)
    """
    import json
    import select
    import sys

    if json_vars_arg:
        try:
            parsed = json.loads(json_vars_arg)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    elif not sys.stdin.isatty():
        try:
            if select.select([sys.stdin], [], [], 0.0)[0]:
                stdin_data = sys.stdin.read().strip()
                if stdin_data:
                    parsed = json.loads(stdin_data)
                    return parsed if isinstance(parsed, dict) else None
        except (json.JSONDecodeError, OSError, ValueError, AttributeError):
            return None
    return {}


def run_errands(
    formatter: OutputFormatter,
    command: str | None,
    name: str | None,
    json_vars: str | None,
    epic_action: str | None,
    epic_id: str | None,
    bead_id: str | None = None,
) -> int:
    """Run errands command.

    Args:
        formatter: Output formatter
        command: Subcommand (add, schedule, run, prompt, epic, or None for list)
        name: Errand name for add/schedule/run
        json_vars: JSON variables for schedule/run (or read from stdin)
        epic_action: Epic action (set, or None for show)
        epic_id: Epic ID for set action
        bead_id: Bead ID for prompt command

    Returns:
        Exit code (0=success, 1=error)
    """
    from laytonlib.errands import (
        add_errand,
        build_prompt,
        ensure_epic,
        get_epic,
        list_errands,
        schedule_errand,
        set_epic,
    )

    if command == "add":
        if not name:
            formatter.error("MISSING_NAME", "Errand name is required")
            return 1

        try:
            path = add_errand(name)
            formatter.success(
                {"created": str(path), "name": name},
                next_steps=[f"Edit {path} to configure the errand"],
            )
            return 0
        except FileExistsError as e:
            formatter.error(
                "ERRAND_EXISTS",
                str(e),
                next_steps=["Review existing errand or choose a different name"],
            )
            return 1

    elif command == "schedule":
        if not name:
            formatter.error("MISSING_NAME", "Errand name is required")
            return 1

        variables = _parse_json_vars(json_vars)
        if variables is None:
            formatter.error("INVALID_JSON", "Invalid JSON variables")
            return 1

        try:
            result = schedule_errand(name, variables)
            formatter.success({"scheduled": result})
            return 0
        except FileNotFoundError:
            formatter.error(
                "ERRAND_NOT_FOUND",
                f"Errand '{name}' not found",
                next_steps=["Run 'layton errands' to list available errands"],
            )
            return 1
        except RuntimeError as e:
            error_str = str(e)
            if "BD_UNAVAILABLE" in error_str:
                formatter.error(
                    "BD_UNAVAILABLE",
                    "bd CLI not found",
                    next_steps=[
                        "Install Beads CLI: https://github.com/steveyegge/beads"
                    ],
                )
            elif "NO_EPIC" in error_str:
                formatter.error(
                    "NO_EPIC",
                    "Epic not configured",
                    next_steps=["Run 'layton errands epic set <id>' to configure epic"],
                )
            else:
                formatter.error("BD_ERROR", error_str)
            return 1

    elif command == "epic":
        if epic_action == "set":
            if not epic_id:
                formatter.error("MISSING_EPIC_ID", "Epic ID is required for set")
                return 1
            if set_epic(epic_id):
                formatter.success({"epic": epic_id})
                return 0
            else:
                formatter.error("WRITE_FAILED", "Failed to save epic to config")
                return 1
        else:
            # Show current epic
            epic = get_epic()
            if epic:
                formatter.success({"epic": epic})
                return 0
            else:
                formatter.error(
                    "NO_EPIC",
                    "Epic not configured",
                    next_steps=["Run 'layton errands epic set <id>' to configure epic"],
                )
                return 1

    elif command == "run":
        if not name:
            formatter.error("MISSING_NAME", "Errand name is required")
            return 1

        variables = _parse_json_vars(json_vars)
        if variables is None:
            formatter.error("INVALID_JSON", "Invalid JSON variables")
            return 1

        try:
            ensure_epic()
        except RuntimeError as e:
            error_str = str(e)
            if "BD_UNAVAILABLE" in error_str:
                formatter.error(
                    "BD_UNAVAILABLE",
                    "bd CLI not found",
                    next_steps=[
                        "Install Beads CLI: https://github.com/steveyegge/beads"
                    ],
                )
            else:
                formatter.error("BD_ERROR", error_str)
            return 1

        try:
            result = schedule_errand(name, variables)
            # Return only bead_id and title — NO prompt (subagent fetches that)
            bead_id_val = result.get("id") or result.get("number")
            title = result.get("title", "")
            if not bead_id_val:
                formatter.error(
                    "BD_ERROR",
                    "Failed to schedule errand: missing bead ID in response",
                )
                return 1
            formatter.success({"bead_id": bead_id_val, "title": title})
            return 0
        except FileNotFoundError:
            formatter.error(
                "ERRAND_NOT_FOUND",
                f"Errand '{name}' not found",
                next_steps=["Run 'layton errands' to list available errands"],
            )
            return 1
        except RuntimeError as e:
            formatter.error("BD_ERROR", str(e))
            return 1

    elif command == "prompt":
        if not bead_id:
            formatter.error("MISSING_BEAD_ID", "Bead ID is required")
            return 1

        prompt = build_prompt(bead_id)
        if prompt is None:
            formatter.error(
                "BEAD_NOT_FOUND",
                f"Bead '{bead_id}' not found",
                next_steps=["Check bead ID with 'bd show <id>'"],
            )
            return 1

        formatter.success({"bead_id": bead_id, "prompt": prompt})
        return 0

    else:
        # Default: list errands
        errands = list_errands()
        next_steps = []
        if not errands:
            next_steps.append("Run 'layton errands add <name>' to create an errand")
        else:
            next_steps.append(
                "See references/protocols/schedule-errand.md for scheduling protocol"
            )
        formatter.success(
            {"errands": [e.to_dict() for e in errands]},
            next_steps=next_steps if next_steps else None,
        )
        return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0=success, 1=fixable, 2=critical)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # Create formatter based on --human flag
    formatter = OutputFormatter(human=args.human, verbose=args.verbose)

    # Check for vault (except for 'config init' which creates one)
    is_config_init = args.command == "config" and getattr(args, "config_command", None) == "init"
    if not is_config_init:
        from laytonlib.config import detect_skill_directory, find_vault_root

        vault_root = find_vault_root()
        if vault_root is None:
            from pathlib import Path

            cwd = str(Path.cwd())
            if detect_skill_directory():
                formatter.error(
                    "WRONG_DIRECTORY",
                    f"Running from the Layton skill directory, not a project vault (cwd: {cwd})",
                    next_steps=[
                        "Do not cd into the skill directory before invoking the script",
                        "Call the script with its full path from your project root",
                    ],
                )
            else:
                formatter.error(
                    "NO_VAULT",
                    f"No .layton/config.json found in {cwd} or any parent directory",
                    next_steps=[
                        "Run 'layton config init' to create a vault in the current directory",
                        "Or cd into a project that has a .layton/ vault",
                    ],
                )
            return 1

    # No-arg default: run orientation (doctor + rolodex + protocols)
    if args.command is None:
        return run_orientation(formatter)

    # Route to command handlers
    if args.command == "doctor":
        from laytonlib.doctor import run_doctor

        return run_doctor(formatter, fix=getattr(args, "fix", False))

    elif args.command == "config":
        from laytonlib.config import run_config

        # No subcommand default: show
        config_cmd = args.config_command or "show"
        return run_config(
            formatter,
            config_cmd,
            key=getattr(args, "key", None),
            value=getattr(args, "value", None),
            force=getattr(args, "force", False),
        )

    elif args.command == "context":
        from laytonlib.context import run_context

        return run_context(formatter)

    elif args.command == "rolodex":
        return run_rolodex(
            formatter,
            command=getattr(args, "rolodex_command", None),
            discover=getattr(args, "discover", False),
            name=getattr(args, "name", None),
        )

    elif args.command == "protocols":
        return run_protocols(
            formatter,
            command=getattr(args, "protocols_command", None),
            name=getattr(args, "name", None),
        )

    elif args.command == "errands":
        return run_errands(
            formatter,
            command=getattr(args, "errands_command", None),
            name=getattr(args, "name", None),
            json_vars=getattr(args, "json_vars", None),
            epic_action=getattr(args, "action", None),
            epic_id=getattr(args, "epic_id", None),
            bead_id=getattr(args, "bead_id", None),
        )

    else:
        # Unknown command - shouldn't happen with argparse
        formatter.error("UNKNOWN_COMMAND", f"Unknown command: {args.command}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
