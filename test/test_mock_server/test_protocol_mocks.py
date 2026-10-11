"""Tests for driving the WebSocket and gRPC mocks from JSON actions."""
from __future__ import annotations

import pytest

from je_api_testka.utils.exception.exceptions import MockServerException
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.mock_server.protocol_mocks import (
    grpc_mock_received,
    start_grpc_mock,
    start_websocket_mock,
    stop_grpc_mock,
    stop_websocket_mock,
    websocket_mock_received,
)
from je_api_testka.websocket_wrapper.websocket_method import test_api_method_websocket as ws_round_trip


@pytest.fixture(autouse=True)
def _stop_mocks():
    yield
    stop_websocket_mock()
    stop_grpc_mock()


def _values(record: dict) -> list:
    return list(record.values())


def test_websocket_mock_through_json_actions():
    pytest.importorskip("websockets")
    url = _values(execute_action([["AT_mock_start_websocket_server", {
        "port": 0, "routes": {"/chat": {"replies": {"ping": "pong"}}},
    }]]))[0]
    assert url.startswith("ws://127.0.0.1:")
    assert ws_round_trip(f"{url}/chat", messages=["ping"], timeout=5)["messages_received"] == ["pong"]
    received = _values(execute_action([
        ["AT_mock_websocket_received", {"path": "/chat"}],
        ["AT_mock_stop_websocket_server"],
    ]))
    assert received[0] == ["ping"]


def test_websocket_mock_defaults_to_echo_on_root():
    pytest.importorskip("websockets")
    url = start_websocket_mock(port=0)
    assert ws_round_trip(f"{url}/", messages=["x"], timeout=5)["messages_received"] == ["x"]


def test_grpc_mock_through_json_actions():
    grpc = pytest.importorskip("grpc")
    address = _values(execute_action([["AT_mock_start_grpc_server", {
        "port": 0, "methods": {"/shop.Catalog/Get": {"response": {"id": 1}}},
    }]]))[0]
    with grpc.insecure_channel(address) as channel:
        assert channel.unary_unary("/shop.Catalog/Get")(b'{"sku":"a"}', timeout=5) == b'{"id":1}'
    assert grpc_mock_received("/shop.Catalog/Get") == ['{"sku":"a"}']


def test_second_start_raises_and_keeps_the_first():
    pytest.importorskip("websockets")
    url = start_websocket_mock(port=0)
    with pytest.raises(MockServerException):
        start_websocket_mock(port=0)
    assert ws_round_trip(f"{url}/", messages=["still up"], timeout=5)["messages_received"] == ["still up"]


def test_received_without_a_running_mock_raises():
    with pytest.raises(MockServerException):
        websocket_mock_received("/chat")
    with pytest.raises(MockServerException):
        grpc_mock_received("/a.B/C")


def test_grpc_mock_needs_methods():
    with pytest.raises(MockServerException):
        start_grpc_mock({})


def test_stop_when_nothing_runs_is_a_no_op():
    stop_websocket_mock()
    stop_grpc_mock()
