import argparse
import sys

from rich.panel import Panel

from sonos_fade.discovery import discover_speakers, get_groups
from sonos_fade.fade import (
    DEFAULT_SECONDS_PER_STEP,
    choose_group,
    choose_target_volume,
    fade_volume,
    find_group_by_name,
    group_label,
)
from sonos_fade.ui import UserQuit, console, groups_table


def _fail(message: str) -> None:
    console.print(Panel(message, title="[bold red]Error", border_style="red", expand=False))
    sys.exit(1)


def _load_groups_or_exit():
    with console.status(
        "[cyan]Discovering Sonos speakers on your LAN…", spinner="dots"
    ) as status:
        speakers = discover_speakers()
        if not speakers:
            status.stop()
            _fail("No Sonos speakers found on the network.")

        status.update("[cyan]Resolving speaker groups…")
        groups = get_groups(speakers)
    if not groups:
        _fail("No speaker groups found.")

    console.print(f"[green]✓[/green] [white]Found {len(groups)} group(s).[/white]")
    return groups


def cmd_list(_args):
    groups = _load_groups_or_exit()
    console.print()
    console.print(groups_table(groups, group_label))


def cmd_fade(args):
    groups = _load_groups_or_exit()

    group = None
    if args.group:
        group = find_group_by_name(groups, args.group)
        if group is None:
            console.print(
                f"[yellow]No group matching[/yellow] '[bold]{args.group}[/bold]'. "
                "Falling back to selection."
            )
    if group is None:
        group = choose_group(groups)

    if args.target is None:
        target = choose_target_volume(group)
    else:
        target = args.target

    fade_volume(group, target, seconds_per_step=args.seconds_per_step)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="sonos-fade",
        description="Gradually fade the volume of a Sonos group on your LAN.",
    )
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="List discovered Sonos groups and exit.")
    p_list.set_defaults(func=cmd_list)

    p_fade = sub.add_parser("fade", help="Fade a group's volume to a target level.")
    p_fade.add_argument(
        "--group",
        help="Group label (comma-joined member names) or coordinator name. "
             "Prompts if omitted or no match.",
    )
    p_fade.add_argument(
        "--target",
        type=_volume,
        help="Target volume (0-100). Prompts if omitted.",
    )
    p_fade.add_argument(
        "--seconds-per-step",
        type=_positive_number,
        default=DEFAULT_SECONDS_PER_STEP,
        help=f"Seconds between each 1-unit volume change (default: {DEFAULT_SECONDS_PER_STEP}).",
    )
    p_fade.set_defaults(func=cmd_fade)

    return parser


def _volume(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not an integer")
    if not 0 <= n <= 100:
        raise argparse.ArgumentTypeError("must be between 0 and 100")
    return n


def _positive_number(value):
    try:
        n = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} is not a number")
    if n <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return n


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        args = parser.parse_args(["fade", *(argv or [])])

    try:
        args.func(args)
    except UserQuit:
        console.print("[yellow]Quit.[/yellow]")
        sys.exit(0)
    except (KeyboardInterrupt, EOFError):
        console.print()
        console.print("[yellow]Cancelled.[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    main()
