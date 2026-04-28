"""
Runner-only metadata keys that must be stripped from action kwargs before the
underlying executor function is invoked.
"""
from __future__ import annotations

from typing import List

RUNNER_METADATA_KEYS = ("id", "depends_on", "tags")


def strip_runner_metadata(action: list) -> list:
    """Return a copy of ``action`` with ``RUNNER_METADATA_KEYS`` removed from kwargs."""
    if len(action) < 2 or not isinstance(action[1], dict):
        return list(action)
    cleaned_kwargs = {key: value for key, value in action[1].items()
                      if key not in RUNNER_METADATA_KEYS}
    return [action[0], cleaned_kwargs] + list(action[2:])


def strip_many(actions: List[list]) -> List[list]:
    return [strip_runner_metadata(action) for action in actions]
