"""Tests for the record-replay proxy."""
from __future__ import annotations

from flask import Flask

from je_api_testka.connection.cassette import Cassette, CassetteRecord
from je_api_testka.utils.mock_server.proxy_recorder import attach_proxy


def test_proxy_replays_cached_response(tmp_path):
    cassette_path = tmp_path / "tape.json"
    cassette = Cassette(str(cassette_path))
    cassette.put(CassetteRecord(
        method="GET",
        url="http://upstream.invalid/v1/users",
        request_body="",
        response_status=200,
        response_body='{"users":[]}',
        response_headers={"Content-Type": "application/json"},
    ))
    app = Flask(__name__)
    attach_proxy(app, "http://upstream.invalid", str(cassette_path), replay_only=True)
    client = app.test_client()
    rsp = client.get("/proxy/v1/users")
    assert rsp.status_code == 200
    assert rsp.get_json() == {"users": []}


def test_proxy_replay_only_returns_404_when_missing(tmp_path):
    app = Flask(__name__)
    attach_proxy(app, "http://upstream.invalid", str(tmp_path / "tape.json"),
                 replay_only=True)
    client = app.test_client()
    rsp = client.get("/proxy/anything")
    assert rsp.status_code == 404
