"""Tests for JSON Schema inference."""
from __future__ import annotations

from je_api_testka.spec.schema_inference import infer_schema


def test_object_schema_lists_required_keys():
    schema = infer_schema({"name": "alice", "age": 30})
    assert schema["type"] == "object"
    assert sorted(schema["required"]) == ["age", "name"]
    assert schema["properties"]["age"]["type"] == "integer"


def test_array_schema_uses_first_element():
    schema = infer_schema(["a", "b"])
    assert schema == {"type": "array", "items": {"type": "string"}}


def test_empty_array_returns_open_items():
    assert infer_schema([])["items"] == {}


def test_scalars_classified_correctly():
    assert infer_schema(True)["type"] == "boolean"
    assert infer_schema(1.5)["type"] == "number"
    assert infer_schema(None)["type"] == "null"
