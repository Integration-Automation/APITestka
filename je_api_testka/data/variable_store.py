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


def extract_from_payload(payload: Any, path: str) -> Optional[Any]:
    """
    Walk a dotted path into ``payload``. ``a.b[0].c`` -> ``payload['a']['b'][0]['c']``.

    Returns ``None`` if any segment is missing.
    """
    if not path:
        return payload
    cursor: Any = payload
    for raw in path.split("."):
        segment = raw
        index: Optional[int] = None
        if "[" in segment and segment.endswith("]"):
            segment, raw_index = segment[:-1].split("[", 1)
            try:
                index = int(raw_index)
            except ValueError:
                return None
        if segment:
            if not isinstance(cursor, dict) or segment not in cursor:
                return None
            cursor = cursor[segment]
        if index is not None:
            if not isinstance(cursor, list) or index >= len(cursor):
                return None
            cursor = cursor[index]
    return cursor


def extract_and_store(response: dict, path: str, name: str) -> Any:
    """Extract from ``response`` and persist into the global :data:`variable_store`."""
    value = extract_from_payload(response, path)
    variable_store.set(name, value)
    return value
