import time

DEFAULT_SECONDS_PER_STEP = 10


def group_label(group):
    return ", ".join(m.player_name for m in group.members)


def choose_group(groups):
    print("\nAvailable speakers/groups:\n")
    labels = [group_label(group) for group in groups]
    for i, group in enumerate(groups, 1):
        state = group.coordinator.get_current_transport_info().get(
            "current_transport_state", "UNKNOWN"
        )
        print(
            f"  {i}. [{labels[i-1]}] "
            f"(volume: {group.coordinator.volume}, status: {state})"
        )

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


def find_group_by_name(groups, name):
    needle = name.strip().lower()
    for group in groups:
        if group_label(group).lower() == needle:
            return group
        if group.coordinator.player_name.lower() == needle:
            return group
    return None


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


def fade_volume(group, target, seconds_per_step=DEFAULT_SECONDS_PER_STEP):
    current = group.coordinator.volume
    diff = target - current

    if diff == 0:
        print("Already at target volume.")
        return

    step = 1 if diff > 0 else -1
    steps = abs(diff)
    total_time = steps * seconds_per_step

    print(
        f"\nFading from {current} to {target} "
        f"({steps} steps, ~{total_time:.0f}s)"
    )

    for i in range(1, steps + 1):
        new_volume = current + (step * i)
        for member in group.members:
            member.volume = new_volume
        print(f"\r  Volume: {new_volume} (step {i} of {steps})", end="", flush=True)
        if i < steps:
            time.sleep(seconds_per_step)

    print(f"\n\nDone. Volume set to {target}.")
