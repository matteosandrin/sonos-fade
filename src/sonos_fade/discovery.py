import soco


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
