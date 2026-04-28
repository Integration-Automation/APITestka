"""
Structural diff between two JSON-like payloads.

Returns three buckets:
* ``added``      - keys present in the right side only.
* ``removed``    - keys present in the left side only.
* ``changed``    - keys present in both with different values; value is
                   ``(left_value, right_value)``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Tuple


@dataclass
class DiffResult:
    """Bucketed differences between two payloads."""

    added: Dict[str, Any] = field(default_factory=dict)
    removed: Dict[str, Any] = field(default_factory=dict)
    changed: Dict[str, Tuple[Any, Any]] = field(default_factory=dict)

    @property
    def is_empty(self) -> bool:
        return not (self.added or self.removed or self.changed)


def _child_prefix(prefix: str, suffix: str) -> str:
    return f"{prefix}.{suffix}" if prefix else suffix


def _walk_dicts(left: dict, right: dict, prefix: str,
                ignore: Iterable[str], result: DiffResult) -> None:
    for key in left.keys() | right.keys():
        child = _child_prefix(prefix, key)
        if key not in right:
            result.removed[child] = left[key]
        elif key not in left:
            result.added[child] = right[key]
        else:
            _walk(left[key], right[key], child, ignore, result)


def _walk_lists(left: list, right: list, prefix: str,
                ignore: Iterable[str], result: DiffResult) -> None:
    for index in range(max(len(left), len(right))):
        child = f"{prefix}[{index}]"
        if index >= len(right):
            result.removed[child] = left[index]
        elif index >= len(left):
            result.added[child] = right[index]
        else:
            _walk(left[index], right[index], child, ignore, result)


def _walk(left: Any, right: Any, prefix: str, ignore: Iterable[str], result: DiffResult) -> None:
    if prefix in ignore:
        return
    if isinstance(left, dict) and isinstance(right, dict):
        _walk_dicts(left, right, prefix, ignore, result)
        return
    if isinstance(left, list) and isinstance(right, list):
        _walk_lists(left, right, prefix, ignore, result)
        return
    if left != right:
        result.changed[prefix or "<root>"] = (left, right)


def diff_payloads(left: Any, right: Any, ignore_paths: Iterable[str] = ()) -> DiffResult:
    """Return a :class:`DiffResult` describing structural changes from ``left`` to ``right``."""
    result = DiffResult()
    _walk(left, right, prefix="", ignore=set(ignore_paths), result=result)
    return result
