"""Tests for the variable store and JSONPath-style extractor."""
from __future__ import annotations

from je_api_testka.data.variable_store import (
    VariableStore,
    extract_and_store,
    extract_from_payload,
    variable_store,
)


def test_variable_store_basic_ops():
    store = VariableStore()
    store.set("k", "v")
    assert store.get("k") == "v"
    assert store.snapshot() == {"k": "v"}
    store.delete("k")
    assert store.get("k") is None
    store.set("a", 1)
    store.clear()
    assert store.snapshot() == {}


def test_extract_dotted_path():
    payload = {"a": {"b": {"c": 7}}}
    assert extract_from_payload(payload, "a.b.c") == 7


def test_extract_with_index():
    payload = {"items": [{"name": "x"}, {"name": "y"}]}
    assert extract_from_payload(payload, "items[1].name") == "y"


def test_extract_missing_returns_none():
    payload = {"a": 1}
    assert extract_from_payload(payload, "a.b.c") is None
    assert extract_from_payload(payload, "x") is None


def test_extract_and_store_writes_global():
    variable_store.clear()
    extract_and_store({"token": "abc"}, "token", "my_token")
    assert variable_store.get("my_token") == "abc"
    variable_store.clear()
