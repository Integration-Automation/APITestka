"""Tests for authentication helpers."""
from __future__ import annotations

import base64
import builtins

import pytest

from je_api_testka.security import auth_helpers
from je_api_testka.utils.exception.exceptions import APITesterException


def test_basic_auth_header_encodes_credentials():
    header = auth_helpers.basic_auth_header("alice", "s3cret")
    decoded = base64.b64decode(header["Authorization"].split(" ", 1)[1]).decode()
    assert decoded == "alice:s3cret"


def test_basic_auth_header_rejects_non_strings():
    with pytest.raises(APITesterException):
        auth_helpers.basic_auth_header(None, "x")


def test_bearer_token_header():
    header = auth_helpers.bearer_token_header("abc.def.ghi")
    assert header["Authorization"] == "Bearer abc.def.ghi"


def test_bearer_token_header_rejects_empty():
    with pytest.raises(APITesterException):
        auth_helpers.bearer_token_header("")


def test_build_jwt_dependency_missing(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "jwt":
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APITesterException) as excinfo:
        auth_helpers.build_jwt({"sub": "x"}, "secret")
    assert "PyJWT" in str(excinfo.value)


def test_aws_sigv4_dependency_missing(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name.startswith("botocore"):
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APITesterException) as excinfo:
        auth_helpers.aws_sigv4_headers(
            "GET", "https://example.invalid/", "us-east-1", "s3", "AK", "SK"
        )
    assert "botocore" in str(excinfo.value)
