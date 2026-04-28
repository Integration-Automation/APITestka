"""Tests for the GraphQL helper - we focus on the payload builder."""
from __future__ import annotations

from je_api_testka.graphql_wrapper.graphql_method import _build_payload


def test_build_payload_minimal():
    payload = _build_payload("{ user { id } }", None, None)
    assert payload == {"query": "{ user { id } }"}


def test_build_payload_with_variables_and_operation():
    payload = _build_payload(
        "query Get($id: ID!) { user(id: $id) { id } }",
        {"id": "42"},
        "Get",
    )
    assert payload["variables"] == {"id": "42"}
    assert payload["operationName"] == "Get"
