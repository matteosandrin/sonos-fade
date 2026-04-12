import sys
import time

import soco

SECONDS_PER_UNIT = 10


def discover_speakers():
    speakers = soco.discover(timeout=5)
    if not speakers:
        return []
    return list(speakers)


def get_groups(speakers):
    seen = set()
    groups = []
    for speaker in speakers:
        for group in speaker.all_groups:
            uid = group.uid
            if uid not in seen:
                seen.add(uid)
                groups.append(group)
    return groups


def choose_group(groups):
    print("\nAvailable speakers/groups:\n")
    labels = [
        ", ".join(m.player_name for m in group.members) for group in groups
    ]
    for i, group in enumerate(groups, 1):
        state = group.coordinator.get_current_transport_info().get("current_transport_state", "UNKNOWN")
        print(f"  {i}. [{labels[i-1]}] (volume: {group.coordinator.volume}, status: {state})")

    if len(groups) == 1:
        print(f"\nOnly one speaker/group found. Using [{labels[0]}].")
        return groups[0]

    while True:
        try:
            choice = int(input("\nChoose a speaker/group: "))
            if 1 <= choice <= len(groups):
                return groups[choice - 1]
            print(f"Please enter a number between 1 and {len(groups)}.")
        except ValueError:
            print("Please enter a valid number.")


def choose_target_volume(group):
    current = group.coordinator.volume
    print(f"\nCurrent volume: {current}")

    while True:
        try:
            target = int(input("Target volume (0-100): "))
            if 0 <= target <= 100:
                return target
            print("Please enter a number between 0 and 100.")
        except ValueError:
            print("Please enter a valid number.")


def fade_volume(group, target):
    current = group.coordinator.volume
    diff = target - current

    if diff == 0:
        print("Already at target volume.")
        return

    step = 1 if diff > 0 else -1
    steps = abs(diff)
    total_time = steps * SECONDS_PER_UNIT

    print(f"\nFading from {current} to {target} "
          f"({steps} steps, ~{total_time:.0f}s)")

    for i in range(1, steps + 1):
        new_volume = current + (step * i)
        for member in group.members:
            member.volume = new_volume
        print(f"\r  Volume: {new_volume} (step {i} of {steps})", end="", flush=True)
        if i < steps:
            time.sleep(SECONDS_PER_UNIT)

    print(f"\n\nDone. Volume set to {target}.")


def main():
    print("Discovering Sonos speakers...")
    speakers = discover_speakers()
    if not speakers:
        print("No Sonos speakers found on the network.")
        sys.exit(1)

    groups = get_groups(speakers)
    if not groups:
        print("No speaker groups found.")
        sys.exit(1)

    group = choose_group(groups)
    target = choose_target_volume(group)
    fade_volume(group, target)


if __name__ == "__main__":
    main()
