"""
Thread-safe variable store and JSONPath-style extraction from response payloads.

Used to chain requests in JSON action scripts: extract a value from the first
response, store under a name, then template into later requests via ``{{name}}``.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional


class VariableStore:
    """A globally accessible, thread-safe key/value mapping."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._values: Dict[str, Any] = {}

    def set(self, name: str, value: Any) -> None:
        with self._lock:
            self._values[name] = value

    def get(self, name: str, default: Any = None) -> Any:
        with self._lock:
            return self._values.get(name, default)

    def delete(self, name: str) -> None:
        with self._lock:
            self._values.pop(name, None)

    def clear(self) -> None:
        with self._lock:
            self._values.clear()

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._values)


variable_store = VariableStore()


_MISSING = object()


def _split_segment(raw: str) -> Optional[tuple]:
    """Split ``foo[3]`` into ``("foo", 3)``; return ``None`` for malformed input."""
    if "[" not in raw or not raw.endswith("]"):
        return raw, None
    segment, raw_index = raw[:-1].split("[", 1)
    try:
        return segment, int(raw_index)
    except ValueError:
        return None


def _step_dict(cursor: Any, segment: str) -> Any:
    if not segment:
        return cursor
    if not isinstance(cursor, dict) or segment not in cursor:
        return _MISSING
    return cursor[segment]


def _step_list(cursor: Any, index: Optional[int]) -> Any:
    if index is None:
        return cursor
    if not isinstance(cursor, list) or index >= len(cursor):
        return _MISSING
    return cursor[index]


def extract_from_payload(payload: Any, path: str) -> Optional[Any]:
    """
    Walk a dotted path into ``payload``. ``a.b[0].c`` -> ``payload['a']['b'][0]['c']``.

    Returns ``None`` if any segment is missing or malformed.
    """
    if not path:
        return payload
    cursor: Any = payload
    for raw in path.split("."):
        split = _split_segment(raw)
        if split is None:
            return None
        segment, index = split
        cursor = _step_dict(cursor, segment)
        if cursor is _MISSING:
            return None
        cursor = _step_list(cursor, index)
        if cursor is _MISSING:
            return None
    return cursor


def extract_and_store(response: dict, path: str, name: str) -> Any:
    """Extract from ``response`` and persist into the global :data:`variable_store`."""
    value = extract_from_payload(response, path)
    variable_store.set(name, value)
    return value
