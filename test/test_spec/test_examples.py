"""Tests for deterministic example values from an OpenAPI document."""
from __future__ import annotations

import pytest

from je_api_testka.ai.backend import NoOpAIBackend, set_ai_backend
from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.spec.examples import (
    example_value,
    fill_path,
    parameter_example,
    request_body_example,
    success_status,
)

SPEC = {"components": {"schemas": {
    "Item": {"type": "object", "properties": {"id": {"type": "integer"}, "tag": {"$ref": "#/components/schemas/Tag"}}},
    "Tag": {"type": "string", "enum": ["new", "old"]},
    "Node": {"type": "object", "properties": {"child": {"$ref": "#/components/schemas/Node"}}},
}}}


@pytest.mark.parametrize(("schema", "value"), [
    ({"type": "integer"}, 1),
    ({"type": "number"}, 1.0),
    ({"type": "boolean"}, True),
    ({"type": "string"}, "string"),
    ({"type": "string", "format": "uuid"}, "00000000-0000-4000-8000-000000000000"),
    ({"type": "string", "format": "email"}, "user@example.com"),
    ({"type": ["null", "integer"]}, 1),
    ({"type": "string", "example": "abc"}, "abc"),
    ({"type": "integer", "default": 7}, 7),
    ({"examples": ["first", "second"]}, "first"),
    ({"type": "array", "items": {"type": "integer"}}, [1]),
    ({"$ref": "#/components/schemas/Item"}, {"id": 1, "tag": "new"}),
    ({"allOf": [{"properties": {"a": {"type": "integer"}}}, {"properties": {"b": {"type": "boolean"}}}]},
     {"a": 1, "b": True}),
    ({"oneOf": [{"type": "string"}, {"type": "integer"}]}, "string"),
    ({}, "string"),
])
def test_example_value(schema, value):
    assert example_value(schema, SPEC) == value


def test_recursive_schema_stops():
    value = example_value({"$ref": "#/components/schemas/Node"}, SPEC)
    depth = 0
    while value:
        value = value["child"]
        depth += 1
    assert depth < 20


def test_parameter_examples_and_path_filling():
    assert parameter_example({"name": "id", "in": "path", "example": 42}, SPEC) == 42
    assert parameter_example({"name": "id", "in": "path", "examples": {"a": {"value": "x/y"}}}, SPEC) == "x/y"
    assert parameter_example({"name": "id", "in": "path", "schema": {"type": "integer"}}, SPEC) == 1
    assert fill_path("/items/{id}/tags/{tag}", {"id": "x/y"}) == "/items/x%2Fy/tags/1"


def test_success_status_and_request_body():
    assert success_status({"responses": {"404": {}, "201": {}, "204": {}}}) == 201
    assert success_status({"responses": {"2XX": {}}}) == 200
    operation = {"requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Item"}}}}}
    assert request_body_example(operation, SPEC) == {"id": 1, "tag": "new"}
    assert request_body_example({"requestBody": {"content": {"application/json": {"example": {"a": 1}}}}}, SPEC) == {"a": 1}
    assert request_body_example({"requestBody": {"content": {"text/plain": {}}}}, SPEC) is None


def test_deterministic_generation_fills_parameters_status_and_body():
    set_ai_backend(NoOpAIBackend())
    spec = {
        "servers": [{"url": "https://api.invalid/v1"}],
        "paths": {
            "/items/{id}": {"parameters": [{"name": "id", "in": "path", "example": 7}],
                            "get": {"parameters": [{"name": "full", "in": "query", "required": True,
                                                    "schema": {"type": "boolean"}}],
                                    "responses": {"200": {}}}},
            "/items": {"post": {"requestBody": {"content": {"application/json": {"example": {"name": "n"}}}},
                                "responses": {"201": {}}}},
        },
    }
    assert generate_tests_from_openapi(spec) == [
        ["AT_test_api_method", {"http_method": "get", "test_url": "https://api.invalid/v1/items/7",
                                "result_check_dict": {"status_code": 200}, "params": {"full": True}}],
        ["AT_test_api_method", {"http_method": "post", "test_url": "https://api.invalid/v1/items",
                                "json": {"name": "n"}, "result_check_dict": {"status_code": 201}}],
    ]
