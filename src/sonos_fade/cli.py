import argparse
import sys

from sonos_fade.discovery import discover_speakers, get_groups
from sonos_fade.fade import (
    DEFAULT_SECONDS_PER_STEP,
    choose_group,
    choose_target_volume,
    fade_volume,
    find_group_by_name,
    group_label,
)


def _load_groups_or_exit():
    print("Discovering Sonos speakers...")
    speakers = discover_speakers()
    if not speakers:
        print("No Sonos speakers found on the network.")
        sys.exit(1)

    groups = get_groups(speakers)
    if not groups:
        print("No speaker groups found.")
        sys.exit(1)

    return groups


def cmd_list(_args):
    groups = _load_groups_or_exit()
    print("\nAvailable speakers/groups:\n")
    for i, group in enumerate(groups, 1):
        state = group.coordinator.get_current_transport_info().get(
            "current_transport_state", "UNKNOWN"
        )
        print(
            f"  {i}. [{group_label(group)}] "
            f"(volume: {group.coordinator.volume}, status: {state})"
        )


def cmd_fade(args):
    groups = _load_groups_or_exit()

    group = None
    if args.group:
        group = find_group_by_name(groups, args.group)
        if group is None:
            print(f"No group matching '{args.group}'. Falling back to selection.")
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

    args.func(args)


if __name__ == "__main__":
    main()
