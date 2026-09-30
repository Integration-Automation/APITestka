"""Tests for the optional gRPC stub server."""
from __future__ import annotations

import base64
import builtins
import json

import pytest

from je_api_testka.utils.exception.exceptions import APITesterException, MockServerException
from je_api_testka.utils.mock_server import grpc_stub
from je_api_testka.utils.mock_server.grpc_stub import GrpcStubServer, configure_grpc_method, encode_payload


def test_is_grpc_available_reflects_import(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "grpc":
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    assert grpc_stub.is_grpc_available() is False


def test_grpc_stub_server_raises_when_dep_missing(monkeypatch):
    monkeypatch.setattr(grpc_stub, "is_grpc_available", lambda: False)
    with pytest.raises(APITesterException):
        grpc_stub.GrpcStubServer()


@pytest.mark.parametrize(("value", "wire"), [
    (b"\x01\x02", b"\x01\x02"), ("héllo", "héllo".encode("utf-8")), ({"a": 1}, b'{"a":1}'), ([1, 2], b"[1,2]"),
    (3, b"3"), (True, b"true"), (None, b"null"),
])
def test_encode_payload(value, wire):
    assert encode_payload(value) == wire


def test_encode_payload_rejects_other_types():
    with pytest.raises(MockServerException):
        encode_payload(object())


@pytest.fixture
def grpc_module():
    return pytest.importorskip("grpc")


@pytest.fixture
def server(grpc_module):
    stub = GrpcStubServer(port=0)
    with stub:
        yield stub


def _unary(grpc_module, server, method, request=b""):
    with grpc_module.insecure_channel(server.address) as channel:
        return channel.unary_unary(method)(request, timeout=5)


def test_unary_json_response_and_request_capture(grpc_module, server):
    server.add_unary_response("/shop.Catalog/Get", {"id": 1})
    assert json.loads(_unary(grpc_module, server, "/shop.Catalog/Get", b'{"sku":"a"}')) == {"id": 1}
    assert server.received("/shop.Catalog/Get") == [b'{"sku":"a"}']


def test_callable_handler_sees_request(grpc_module, server):
    server.register("/echo.Echo/Say", lambda request: request.upper())
    assert _unary(grpc_module, server, "/echo.Echo/Say", b"hi") == b"HI"


def test_server_stream(grpc_module, server):
    server.add_stream_responses("/shop.Catalog/List", [{"id": 1}, "two", b"3"])
    with grpc_module.insecure_channel(server.address) as channel:
        replies = list(channel.unary_stream("/shop.Catalog/List")(b"", timeout=5))
    assert replies == [b'{"id":1}', b"two", b"3"]


def test_error_status(grpc_module, server):
    server.add_error("/shop.Catalog/Get", "not_found", "no such item")
    with pytest.raises(grpc_module.RpcError) as caught:
        _unary(grpc_module, server, "/shop.Catalog/Get")
    assert caught.value.code() == grpc_module.StatusCode.NOT_FOUND
    assert caught.value.details() == "no such item"


def test_unknown_method_is_unimplemented(grpc_module, server):
    with pytest.raises(grpc_module.RpcError) as caught:
        _unary(grpc_module, server, "/nope.Nope/Nope")
    assert caught.value.code() == grpc_module.StatusCode.UNIMPLEMENTED


def test_unknown_status_code_raises(server):
    with pytest.raises(MockServerException):
        server.add_error("/a.B/C", "NOT_A_CODE")


def test_second_start_raises(server):
    with pytest.raises(MockServerException):
        server.start()


def test_configure_from_json_forms(grpc_module, server):
    configure_grpc_method(server, "/a.S/Json", {"response": {"ok": True}})
    configure_grpc_method(server, "/a.S/Raw", {"response_base64": base64.b64encode(b"\x08\x01").decode()})
    configure_grpc_method(server, "/a.S/Err", {"error": {"code": "UNAVAILABLE"}})
    configure_grpc_method(server, "/a.S/List", {"stream": [1, 2]})
    with grpc_module.insecure_channel(server.address) as channel:
        assert list(channel.unary_stream("/a.S/List")(b"", timeout=5)) == [b"1", b"2"]
    assert _unary(grpc_module, server, "/a.S/Json") == b'{"ok":true}'
    assert _unary(grpc_module, server, "/a.S/Raw") == b"\x08\x01"
    with pytest.raises(grpc_module.RpcError):
        _unary(grpc_module, server, "/a.S/Err")


@pytest.mark.parametrize("config", [
    {}, {"response": 1, "stream": []}, {"response": 1, "extra": 2}, {"stream": "x"},
    {"error": "NOT_FOUND"}, {"response_base64": "***"},
])
def test_configure_rejects_bad_forms(server, config):
    with pytest.raises(MockServerException):
        configure_grpc_method(server, "/a.S/M", config)
