"""A small provider app on a free port for contract verification tests."""
from __future__ import annotations

import socket
import threading

import pytest
from flask import Flask, jsonify, request
from werkzeug.serving import make_server


def _provider_app(states: list) -> Flask:
    # Test-only provider on loopback; no form auth surface, CSRF not applicable.
    app = Flask(__name__)  # NOSONAR S4502

    @app.get("/items/<int:item_id>")
    def get_item(item_id: int):
        return jsonify({"id": item_id, "name": f"item {item_id}", "tags": ["a", "b"]})

    @app.post("/items")
    def create_item():
        return jsonify({"id": 99, **(request.get_json(silent=True) or {})}), 201

    @app.get("/ping")
    def ping():
        return "pong", 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.post("/_states")
    def set_state():
        states.append(request.get_json())
        return "", 204

    return app


@pytest.fixture
def provider():
    """Yield ``(base_url, states)``; ``states`` collects provider-state setup calls."""
    states: list = []
    original_getfqdn = socket.getfqdn
    socket.getfqdn = lambda name="": name or "127.0.0.1"  # avoid reverse DNS on some CI runners
    try:
        server = make_server("127.0.0.1", 0, _provider_app(states), threaded=True)
    finally:
        socket.getfqdn = original_getfqdn
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    # Local in-process provider on loopback; HTTPS not applicable.
    yield f"http://127.0.0.1:{server.server_port}", states  # NOSONAR S5332
    server.shutdown()
    thread.join(5)
