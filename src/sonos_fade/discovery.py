import soco


def discover_speakers():
    # Some speakers do not reply to SSDP. If SSDP finds none, scan the subnet on port 1400.
    speakers = soco.discover(timeout=5, allow_network_scan=True)
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
