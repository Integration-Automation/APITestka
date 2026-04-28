"""
Tag-based action filtering.

An action can carry an optional ``"tags"`` list inside its kwargs dict; the
filter keeps only actions whose tags intersect the requested set. Untagged
actions can be optionally included via ``include_untagged=True``.
"""
from __future__ import annotations

from typing import Iterable, List


def _action_tags(action: list) -> List[str]:
    if len(action) < 2 or not isinstance(action[1], dict):
        return []
    raw = action[1].get("tags")
    if isinstance(raw, list):
        return [str(tag) for tag in raw]
    return []


def filter_actions_by_tag(actions: List[list], wanted_tags: Iterable[str],
                          include_untagged: bool = False) -> List[list]:
    """Return only actions whose tags overlap ``wanted_tags``."""
    wanted = set(wanted_tags)
    if not wanted:
        return list(actions)
    filtered: List[list] = []
    for action in actions:
        tags = _action_tags(action)
        if not tags:
            if include_untagged:
                filtered.append(action)
            continue
        if wanted.intersection(tags):
            filtered.append(action)
    return filtered
