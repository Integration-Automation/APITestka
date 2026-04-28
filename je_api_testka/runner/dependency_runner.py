"""
Topological-sort an action list by declared dependencies.

Each action may include ``"id"`` and ``"depends_on": [<id>, ...]`` keys inside
its kwargs dict. ``order_actions`` returns a new list ordered so every action
runs after all of its dependencies.
"""
from __future__ import annotations

from typing import Dict, List

from je_api_testka.utils.exception.exceptions import APITesterExecuteException


def _id_of(action: list) -> str:
    if len(action) >= 2 and isinstance(action[1], dict):
        candidate = action[1].get("id")
        if isinstance(candidate, str):
            return candidate
    return ""


def _deps_of(action: list) -> List[str]:
    if len(action) < 2 or not isinstance(action[1], dict):
        return []
    raw = action[1].get("depends_on") or []
    return [str(dep) for dep in raw]


def order_actions(actions: List[list]) -> List[list]:
    """Return ``actions`` topologically sorted by declared dependencies."""
    by_id: Dict[str, list] = {}
    for action in actions:
        identifier = _id_of(action)
        if identifier:
            by_id[identifier] = action

    visiting: set = set()
    visited: set = set()
    ordered: List[list] = []

    def _visit(action: list) -> None:
        identifier = _id_of(action)
        marker = identifier or id(action)
        if marker in visited:
            return
        if marker in visiting:
            raise APITesterExecuteException(f"dependency cycle detected at {identifier}")
        visiting.add(marker)
        for dep in _deps_of(action):
            if dep in by_id:
                _visit(by_id[dep])
        visiting.discard(marker)
        visited.add(marker)
        ordered.append(action)

    for action in actions:
        _visit(action)
    return ordered
