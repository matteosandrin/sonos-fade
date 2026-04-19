import time

from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from sonos_fade.ui import ask_int, console, groups_table, volume_bar

DEFAULT_SECONDS_PER_STEP = 10


def group_label(group):
    return ", ".join(m.player_name for m in group.members)


def choose_group(groups):
    console.print()
    console.print(groups_table(groups, group_label))

    if len(groups) == 1:
        console.print(
            f"\n[dim]Only one speaker/group found. Using[/dim] "
            f"[bold cyan][{group_label(groups[0])}][/bold cyan]."
        )
        return groups[0]

    console.print()
    choice = ask_int(
        "[bold]Choose a speaker/group[/bold]", minimum=1, maximum=len(groups)
    )
    return groups[choice - 1]


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
    console.print()
    console.print("[bold]Current volume[/bold] ", volume_bar(int(current)))

    return ask_int("[bold]Target volume (0-100)[/bold]", minimum=0, maximum=100)


def fade_volume(group, target, seconds_per_step=DEFAULT_SECONDS_PER_STEP):
    current = group.coordinator.volume
    diff = target - current

    if diff == 0:
        console.print("[dim]Already at target volume.[/dim]")
        return

    step = 1 if diff > 0 else -1
    steps = abs(diff)
    total_time = steps * seconds_per_step

    console.print()
    console.print(
        f"[bold]Fading[/bold] [cyan]{current}[/cyan] → [cyan]{target}[/cyan] "
        f"[dim]({steps} steps, ~{total_time:.0f}s)[/dim]"
    )

    progress = Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold]{task.description}"),
        BarColumn(bar_width=None, complete_style="cyan", finished_style="green"),
        TextColumn("vol [bold]{task.fields[volume]:>3}[/bold]"),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )

    last_applied = current
    try:
        with progress:
            task_id = progress.add_task(
                f"{current} → {target}", total=steps, volume=current
            )
            fps = 60
            for i in range(1, steps + 1):
                sub_ticks = max(1, int(seconds_per_step * fps))
                tick = seconds_per_step / sub_ticks
                for k in range(1, sub_ticks + 1):
                    time.sleep(tick)
                    progress.update(task_id, completed=(i - 1) + k / sub_ticks)
                new_volume = current + (step * i)
                for member in group.members:
                    member.volume = new_volume
                last_applied = new_volume
                progress.update(task_id, completed=i, volume=new_volume)
    except KeyboardInterrupt:
        console.print(
            Panel(
                f"[bold yellow]✗[/bold yellow] Cancelled. "
                f"Volume left at [bold]{last_applied}[/bold].",
                border_style="yellow",
                expand=False,
            )
        )
        raise

    console.print(
        Panel(
            f"[bold green]✓[/bold green] Done. Volume set to [bold]{target}[/bold].",
            border_style="green",
            expand=False,
        )
    )
