"""
Headless-friendly history panel state.

We deliberately keep the data model separate from the Qt widget so the same
logic is testable without an X server / display. The actual ``QListWidget``
hookup lives in ``main_widget.py`` and consumes ``HistoryPanelModel``.
"""
from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional

DEFAULT_HISTORY_LIMIT: int = 100


@dataclass
class HistoryEntry:
    """One captured request from the API Request tab."""

    method: str
    url: str
    status: Optional[int] = None
    summary: str = ""


class HistoryPanelModel:
    """Thread-safe ring buffer of HistoryEntry."""

    def __init__(self, limit: int = DEFAULT_HISTORY_LIMIT) -> None:
        self._lock = threading.RLock()
        self._buffer: Deque[HistoryEntry] = deque(maxlen=limit)

    def push(self, entry: HistoryEntry) -> None:
        with self._lock:
            self._buffer.append(entry)

    def all(self) -> List[HistoryEntry]:
        with self._lock:
            return list(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()

    def latest(self) -> Optional[HistoryEntry]:
        with self._lock:
            return self._buffer[-1] if self._buffer else None
