"""Tests for the declarative mock config and ``apitestka mock --config``."""
from __future__ import annotations

import json

import pytest

from je_api_testka.cli.cli_main import main
from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.mock_server import protocol_mocks
from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer
from je_api_testka.utils.mock_server.mock_config import apply_mock_config, read_mock_config, stop_protocol_mocks


@pytest.fixture(autouse=True)
def _stop_mocks():
    yield
    stop_protocol_mocks()


def _server() -> FlaskMockServer:
    return FlaskMockServer("127.0.0.1", 0)


def test_http_routes_and_relative_openapi(tmp_path):
    spec = {"paths": {"/items": {"get": {"responses": {"200": {
        "content": {"application/json": {"example": [1, 2]}}}}}}}}
    (tmp_path / "spec.json").write_text(json.dumps(spec), encoding="utf-8")
    server = _server()
    endpoints = apply_mock_config({"http": {
        "routes": [{"rule": "/health", "body": {"ok": True}, "status": 201, "methods": ["GET"]}],
        "openapi": "spec.json",
    }}, server, base_dir=str(tmp_path))
    client = server.app.test_client()
    health = client.get("/health")
    assert endpoints == {}
    assert (health.status_code, health.get_json()) == (201, {"ok": True})
    assert client.get("/items").get_json() == [1, 2]


def test_websocket_and_grpc_sections_start_mocks():
    pytest.importorskip("websockets")
    pytest.importorskip("grpc")
    endpoints = apply_mock_config({
        "websocket": {"port": 0, "routes": {"/chat": {}}},
        "grpc": {"port": 0, "methods": {"/a.S/M": {"response": "ok"}}},
    }, _server())
    assert endpoints["websocket"].startswith("ws://")
    assert endpoints["grpc"].startswith("127.0.0.1:")
    stop_protocol_mocks()
    with pytest.raises(MockServerException):
        protocol_mocks.websocket_mock_received("/chat")


def test_failed_grpc_section_stops_the_websocket_it_started():
    pytest.importorskip("websockets")
    pytest.importorskip("grpc")
    with pytest.raises(MockServerException):
        apply_mock_config({
            "websocket": {"port": 0},
            "grpc": {"port": 0, "methods": {"/a.S/M": {"bogus": 1}}},
        }, _server())
    with pytest.raises(MockServerException):
        protocol_mocks.websocket_mock_received("/")


@pytest.mark.parametrize("config", [
    {"ftp": {}},
    {"http": []},
    {"http": {"routes": {}}},
    {"http": {"routes": [{"body": "no rule"}]}},
    {"http": {"routes": [{"rule": "/x", "colour": "red"}]}},
    {"http": {"openapi": "missing.json"}},
])
def test_rejects_malformed_config(config, tmp_path):
    with pytest.raises(MockServerException):
        apply_mock_config(config, _server(), base_dir=str(tmp_path))


def test_read_mock_config_errors(tmp_path):
    (tmp_path / "list.json").write_text("[]", encoding="utf-8")
    (tmp_path / "bad.json").write_text("{", encoding="utf-8")
    for name in ("list.json", "bad.json", "missing.json"):
        with pytest.raises(MockServerException):
            read_mock_config(str(tmp_path / name))


def test_cli_mock_config_starts_and_then_stops_protocol_mocks(tmp_path, monkeypatch):
    pytest.importorskip("websockets")
    config = tmp_path / "mock.json"
    config.write_text(json.dumps({"websocket": {"port": 0}}), encoding="utf-8")
    seen = {}

    def _fake_run(self):
        seen["received"] = protocol_mocks.websocket_mock_received("/")

    monkeypatch.setattr(FlaskMockServer, "start_mock_server", _fake_run)
    assert main(["mock", "--port", "0", "--config", str(config)]) == 0
    assert seen == {"received": []}
    with pytest.raises(MockServerException):
        protocol_mocks.websocket_mock_received("/")
