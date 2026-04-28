"""Tests for the webhook receiver."""
from __future__ import annotations

from flask import Flask

from je_api_testka.utils.mock_server.webhook_receiver import WebhookReceiver


def _client_with_receiver():
    app = Flask(__name__)
    receiver = WebhookReceiver()
    receiver.attach(app, route="/hook")
    return app.test_client(), receiver


def test_webhook_captures_post_payload():
    client, receiver = _client_with_receiver()
    rsp = client.post("/hook", json={"event": "ping"})
    assert rsp.status_code == 200
    latest = receiver.pop_latest()
    assert latest["json"] == {"event": "ping"}
    assert latest["method"] == "POST"


def test_buffer_keeps_only_recent():
    app = Flask(__name__)
    receiver = WebhookReceiver(buffer_size=2)
    receiver.attach(app, route="/hook")
    client = app.test_client()
    for index in range(5):
        client.post("/hook", json={"index": index})
    assert len(receiver.all()) == 2


def test_clear_drops_buffer():
    client, receiver = _client_with_receiver()
    client.post("/hook", json={"event": "x"})
    receiver.clear()
    assert receiver.all() == []
