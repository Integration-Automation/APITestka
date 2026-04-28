"""
Thread-safe in-memory key/value store used by stateful mock endpoints.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Iterator


class StatefulStore:
    """A thread-safe dict wrapper used to mock session state."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value

    def delete(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._data)

    def __contains__(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def __iter__(self) -> Iterator[str]:
        with self._lock:
            return iter(list(self._data))
