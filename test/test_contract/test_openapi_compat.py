"""Tests for the bidirectional check of a contract against an OpenAPI document."""
from __future__ import annotations

import pytest

from je_api_testka.contract.openapi_compat import (
    assert_pact_compatible,
    check_pact_against_openapi,
    interaction_problems,
)
from je_api_testka.contract.openapi_schema import schema_errors
from je_api_testka.contract.pact import add_interaction, new_pact
from je_api_testka.utils.exception.exceptions import APIContractException

SPEC = {
    "openapi": "3.0.3",
    "servers": [{"url": "https://shop.invalid/api/v1"}],
    "components": {
        "schemas": {"Item": {"type": "object", "required": ["id", "name"], "properties": {
            "id": {"type": "integer"}, "name": {"type": "string"}, "note": {"type": "string", "nullable": True}}}},
        "parameters": {"Full": {"name": "full", "in": "query", "schema": {"type": "string"}}},
    },
    "paths": {
        "/items/{id}": {
            "parameters": [{"$ref": "#/components/parameters/Full"}],
            "get": {"responses": {
                "200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Item"}}}},
                "4XX": {"description": "client error"}}},
        },
        "/items": {"post": {
            "parameters": [{"name": "dry", "in": "query", "required": True, "schema": {"type": "string"}}],
            "requestBody": {"required": True, "content": {"application/json": {"schema": {
                "type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}}}},
            "responses": {"default": {"description": "any"}}}},
    },
}


def _interaction(method="GET", path="/items/1", status=200, body=None, query=None, request_body=None):
    request = {"method": method, "path": path}
    if query:
        request["query"] = query
    if request_body is not None:
        request["body"] = request_body
    response = {"status": status}
    if body is not None:
        response["body"] = body
    return {"description": f"{method} {path}", "request": request, "response": response}


def test_compatible_interaction_through_refs_and_templates():
    interaction = _interaction(query="full=1", body={"id": 1, "name": "a", "note": None})
    assert interaction_problems(interaction, SPEC) == []


def test_server_base_path_is_ignored():
    assert interaction_problems(_interaction(path="/api/v1/items/1", body={"id": 1, "name": "a"}), SPEC) == []


@pytest.mark.parametrize(("interaction", "problem"), [
    (_interaction(path="/orders/1"), "no operation for GET /orders/1"),
    (_interaction(method="DELETE"), "no operation for DELETE /items/1"),
    (_interaction(status=500), "status 500 is not declared"),
    (_interaction(query="page=2"), "query parameter 'page' is not declared"),
    (_interaction(body={"id": "1", "name": "a"}), "response body $.body.id: expected type integer, got string"),
    (_interaction(body={"id": 1}), "response body $.body.name: required"),
    (_interaction(method="POST", path="/items", request_body={"name": "a"}),
     "required query parameter 'dry' is not sent"),
    (_interaction(method="POST", path="/items", query="dry=1"), "request body is required but not sent"),
    (_interaction(method="POST", path="/items", query="dry=1", request_body={"name": 3}),
     "request body $.body.name: expected type string, got number"),
    (_interaction(request_body={"x": 1}), "request body is sent but the operation declares none"),
])
def test_problems(interaction, problem):
    assert problem in interaction_problems(interaction, SPEC)


def test_status_ranges_and_default():
    assert interaction_problems(_interaction(status=404), SPEC) == []
    assert interaction_problems(_interaction(method="POST", path="/items", query="dry=1",
                                             request_body={"name": "a"}, status=418), SPEC) == []


def test_report_and_assert():
    pact = new_pact("web", "shop")
    add_interaction(pact, "ok", {"method": "GET", "path": "/items/1"}, {"status": 200, "body": {"id": 1, "name": "a"}})
    add_interaction(pact, "bad", {"method": "GET", "path": "/nope"}, {"status": 200})
    report = check_pact_against_openapi(pact, SPEC)
    assert not report.ok
    assert report.to_dict()["problems"] == [{"interaction": "bad", "problem": "no operation for GET /nope"}]
    assert "1/2 interactions compatible" in report.render_text()
    with pytest.raises(APIContractException):
        assert_pact_compatible(pact, SPEC)
    pact["interactions"].pop()
    assert assert_pact_compatible(pact, SPEC)["ok"] is True


def test_empty_contract_is_not_ok():
    assert not check_pact_against_openapi(new_pact("web", "shop"), SPEC).ok


@pytest.mark.parametrize(("value", "schema", "errors"), [
    (1, {"type": ["integer", "null"]}, 0),
    (None, {"type": ["integer", "null"]}, 0),
    (1.5, {"type": "integer"}, 1),
    (True, {"type": "integer"}, 1),
    ("b", {"enum": ["a"]}, 1),
    ({"a": 1, "b": 2}, {"type": "object", "properties": {"a": {}}, "additionalProperties": False}, 1),
    ([1, "x"], {"type": "array", "items": {"type": "integer"}}, 1),
    ({"a": 1}, {"allOf": [{"required": ["a"]}, {"required": ["b"]}]}, 1),
    ("x", {"anyOf": [{"type": "integer"}, {"type": "string"}]}, 0),
    ([], {"oneOf": [{"type": "integer"}, {"type": "string"}]}, 1),
    ({}, {"$ref": "#/components/schemas/Missing"}, 0),
])
def test_schema_errors(value, schema, errors):
    assert len(schema_errors(value, schema, SPEC)) == errors
