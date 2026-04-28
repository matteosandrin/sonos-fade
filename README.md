# sonos-fade

Gradually fade the volume of a Sonos group on your LAN.

Discovers Sonos speakers via SSDP, lets you pick a group, and ramps the volume
to a target level one step at a time — handy for nudging music down at the end
of an evening without a jarring cut.

## Install

```bash
pip install sonos-fade
```

## Usage

Interactive (prompts for group and target volume):

```bash
sonos-fade
```

List discovered groups:

```bash
sonos-fade list
```

Non-interactive fade:

```bash
sonos-fade fade --group "Living Room" --target 5 --seconds-per-step 2
```

### Options

- `--group` — group label or coordinator name. Prompts if omitted or no match.
- `--target` — target volume (0–100). Prompts if omitted.
- `--seconds-per-step` — seconds between each 1-unit volume change.

## Requirements

- Python 3.10+
- Sonos speakers reachable on the local network

## License

MIT — see [LICENSE](LICENSE).
