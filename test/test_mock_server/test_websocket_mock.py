"""Tests for the WebSocket mock endpoints."""
from __future__ import annotations

import builtins

import pytest

from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.mock_server.websocket_mock import (
    WebSocketMockServer,
    WebSocketRoute,
    route_from_config,
)
from je_api_testka.websocket_wrapper.websocket_method import test_api_method_websocket as ws_round_trip


def test_default_route_echoes():
    assert WebSocketRoute().answer("hello") == ["hello"]


def test_replies_take_precedence_and_expand_message():
    route = WebSocketRoute(replies={"ping": "pong", "hi": ["a", "you said {{message}}"]})
    assert route.answer("ping") == ["pong"]
    assert route.answer("hi") == ["a", "you said hi"]
    assert route.answer("other") == ["other"]


def test_none_fallback_stays_silent():
    assert WebSocketRoute(fallback=None).answer("x") == []


def test_handler_overrides_replies():
    route = WebSocketRoute(replies={"x": "no"}, handler=lambda message: message.upper())
    assert route.answer("x") == ["X"]


def test_route_from_config():
    route = route_from_config({"greeting": "hi", "replies": {"a": "b"}, "fallback": None})
    assert (route.greeting, route.replies, route.fallback) == ("hi", {"a": "b"}, None)


@pytest.mark.parametrize("config", [
    {"unknown": 1}, {"replies": []}, {"fallback": 3}, {"greeting": ["x"]},
])
def test_route_from_config_rejects_bad_values(config):
    with pytest.raises(MockServerException):
        route_from_config(config)


def test_route_path_must_be_absolute():
    with pytest.raises(MockServerException):
        WebSocketMockServer(port=0).add_route("chat")


def test_missing_websockets_raises(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name.startswith("websockets"):
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(MockServerException):
        WebSocketMockServer(port=0).start()


def test_stop_without_start_is_a_no_op():
    WebSocketMockServer(port=0).stop()


@pytest.fixture
def chat_server():
    pytest.importorskip("websockets")
    server = WebSocketMockServer(port=0)
    server.add_route("/chat", WebSocketRoute(greeting="welcome", replies={"ping": "pong"}))
    with server:
        yield server


def test_round_trip_with_greeting_replies_and_echo(chat_server):
    from websockets.sync.client import connect

    with connect(f"{chat_server.url}/chat?room=1", open_timeout=5) as connection:
        assert connection.recv(timeout=5) == "welcome"
        connection.send("ping")
        assert connection.recv(timeout=5) == "pong"
        connection.send("hello")
        assert connection.recv(timeout=5) == "hello"
    assert chat_server.received("/chat") == ["ping", "hello"]


def test_apitestka_websocket_backend_against_the_mock(chat_server):
    record = ws_round_trip(f"{chat_server.url}/chat", messages=["ping"], expected_replies=2, timeout=5)
    assert record["messages_received"] == ["welcome", "pong"]


def test_unknown_path_is_refused(chat_server):
    from websockets.exceptions import InvalidStatus
    from websockets.sync.client import connect

    with pytest.raises(InvalidStatus) as caught:
        connect(f"{chat_server.url}/missing", open_timeout=5)
    assert caught.value.response.status_code == 404


def test_second_start_raises(chat_server):
    with pytest.raises(MockServerException):
        chat_server.start()
