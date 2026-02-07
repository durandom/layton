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

    return parser


def run_orientation(formatter: OutputFormatter) -> int:
    """Run orientation - combined doctor + rolodex + protocols + errands.

    Args:
        formatter: Output formatter

    Returns:
        Exit code (0=success, 1=fixable, 2=critical)
    """
    from laytonlib.errands import (
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

    # Get scheduled and pending review beads (from bd)
    beads_scheduled = get_beads_scheduled()
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
        "errands": errands_data,
        "beads_scheduled": beads_scheduled,
        "beads_pending_review": beads_pending_review,
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


def run_errands(
    formatter: OutputFormatter,
    command: str | None,
    name: str | None,
    json_vars: str | None,
    epic_action: str | None,
    epic_id: str | None,
) -> int:
    """Run errands command.

    Args:
        formatter: Output formatter
        command: Subcommand (add, schedule, epic, or None for list)
        name: Errand name for add/schedule
        json_vars: JSON variables for schedule (or read from stdin)
        epic_action: Epic action (set, or None for show)
        epic_id: Epic ID for set action

    Returns:
        Exit code (0=success, 1=error)
    """
    import json
    import select
    import sys

    from laytonlib.errands import (
        add_errand,
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

        # Parse variables from JSON arg or stdin
        variables = {}
        if json_vars:
            try:
                variables = json.loads(json_vars)
            except json.JSONDecodeError as e:
                formatter.error("INVALID_JSON", f"Invalid JSON: {e}")
                return 1
        elif not sys.stdin.isatty():
            # Read from stdin only if data is actually available (avoid blocking)
            try:
                if select.select([sys.stdin], [], [], 0.0)[0]:
                    stdin_data = sys.stdin.read().strip()
                    if stdin_data:
                        variables = json.loads(stdin_data)
            except json.JSONDecodeError as e:
                formatter.error("INVALID_JSON", f"Invalid JSON from stdin: {e}")
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
        )

    else:
        # Unknown command - shouldn't happen with argparse
        formatter.error("UNKNOWN_COMMAND", f"Unknown command: {args.command}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
