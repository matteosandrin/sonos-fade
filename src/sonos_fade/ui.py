from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

_STATUS_STYLES = {
    "PLAYING": "bold green",
    "PAUSED_PLAYBACK": "yellow",
    "TRANSITIONING": "yellow",
    "STOPPED": "dim",
    "UNKNOWN": "red",
}

_BAR_WIDTH = 10


def status_text(state: str) -> Text:
    return Text(state, style=_STATUS_STYLES.get(state, "magenta"))


def volume_bar(volume: int, width: int = _BAR_WIDTH) -> Text:
    filled = round((volume / 100) * width)
    filled = max(0, min(width, filled))
    if volume >= 70:
        color = "red"
    elif volume >= 40:
        color = "yellow"
    else:
        color = "green"
    bar = Text()
    bar.append("█" * filled, style=color)
    bar.append("░" * (width - filled), style="grey37")
    bar.append(f" {volume:>3}", style="bold")
    return bar


def groups_table(groups, label_for) -> Table:
    table = Table(
        title="Sonos speakers / groups",
        title_style="bold cyan",
        header_style="bold magenta",
        border_style="grey42",
        show_lines=False,
        expand=False,
    )
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Group", style="bold white")
    table.add_column("Volume", no_wrap=True)
    table.add_column("Status", no_wrap=True)

    for i, group in enumerate(groups, 1):
        state = group.coordinator.get_current_transport_info().get(
            "current_transport_state", "UNKNOWN"
        )
        table.add_row(
            str(i),
            label_for(group),
            volume_bar(int(group.coordinator.volume)),
            status_text(state),
        )
    return table
