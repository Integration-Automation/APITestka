"""Tests for the optional WebSocket wrapper."""
from __future__ import annotations

import builtins

import pytest

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.websocket_wrapper import websocket_method


def test_websockets_missing_raises(monkeypatch):
    """When the websockets package is absent we get a friendly APITesterException."""
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "websockets":
            raise ImportError("simulated missing dep")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APITesterException) as excinfo:
        websocket_method._import_websockets()
    assert "websockets" in str(excinfo.value)


def test_test_api_method_websocket_records_failure(monkeypatch):
    """A connection error must be recorded into the global error list."""
    from je_api_testka.utils.test_record.test_record_class import test_record_instance

    def _explode(*_args, **_kwargs):
        raise ConnectionError("boom")

    monkeypatch.setattr(websocket_method, "_async_send_recv", _explode)
    test_record_instance.clean_record()
    with pytest.raises(ConnectionError):
        websocket_method.test_api_method_websocket(
            url="ws://invalid.invalid", messages=["hi"], expected_replies=1
        )
    assert test_record_instance.error_record_list, "failure was not recorded"
