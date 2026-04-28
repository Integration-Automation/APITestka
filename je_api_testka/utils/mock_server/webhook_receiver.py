"""
Webhook receiver: a Flask blueprint-style helper that captures incoming POSTs
into an in-memory queue so tests can assert on what an external system tried
to send.
"""
from __future__ import annotations

import threading
from collections import deque
from typing import Any, Deque, Dict, Optional

from flask import Flask, jsonify, request

DEFAULT_BUFFER_SIZE: int = 100
DEFAULT_OK_STATUS: int = 200


class WebhookReceiver:
    """Captures inbound webhook payloads in a thread-safe ring buffer."""

    def __init__(self, buffer_size: int = DEFAULT_BUFFER_SIZE) -> None:
        self._lock = threading.RLock()
        self._buffer: Deque[Dict[str, Any]] = deque(maxlen=buffer_size)

    def attach(self, app: Flask, route: str = "/webhook") -> None:
        view_name = f"webhook_{route.strip('/').replace('/', '_') or 'root'}"

        def _view():
            payload = {
                "method": request.method,
                "path": request.path,
                "headers": dict(request.headers),
                "json": request.get_json(silent=True),
                "form": request.form.to_dict(flat=True),
                "data": request.get_data(as_text=True),
            }
            with self._lock:
                self._buffer.append(payload)
            return jsonify({"received": True}), DEFAULT_OK_STATUS

        _view.__name__ = view_name
        app.route(route, methods=["POST", "PUT"])(_view)

    def pop_latest(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._buffer[-1] if self._buffer else None

    def all(self) -> list:
        with self._lock:
            return list(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()
