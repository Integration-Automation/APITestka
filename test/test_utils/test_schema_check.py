"""Tests for the optional JSON schema and JSONPath assertions."""
from __future__ import annotations

import builtins

import pytest

from je_api_testka.utils.assert_result import schema_check
from je_api_testka.utils.exception.exceptions import APIAssertException, APITesterException


def test_check_json_schema_passes_when_dep_available():
    pytest.importorskip("jsonschema")
    schema_check.check_json_schema({"name": "abc"}, {"type": "object", "required": ["name"]})


def test_check_json_schema_fails_on_invalid_payload():
    pytest.importorskip("jsonschema")
    with pytest.raises(APIAssertException):
        schema_check.check_json_schema({}, {"type": "object", "required": ["name"]})


def test_check_jsonpath_passes_when_dep_available():
    pytest.importorskip("jsonpath_ng")
    matches = schema_check.check_jsonpath({"a": {"b": 1}}, "$.a.b", expected=1)
    assert matches == [1]


def test_check_jsonpath_no_matches_raises():
    pytest.importorskip("jsonpath_ng")
    with pytest.raises(APIAssertException):
        schema_check.check_jsonpath({"a": 1}, "$.missing")


def test_jsonschema_missing_dep_message(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "jsonschema":
            raise ImportError("simulated")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APITesterException) as excinfo:
        schema_check._import_jsonschema()
    assert "jsonschema" in str(excinfo.value)
