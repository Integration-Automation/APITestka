"""Tests for the optional gRPC stub server."""
from __future__ import annotations

import builtins

import pytest

from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.mock_server import grpc_stub


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
