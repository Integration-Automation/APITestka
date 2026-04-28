"""Tests for OpenAPI contract drift."""
from __future__ import annotations

from je_api_testka.diff.contract_diff import diff_openapi_specs


def test_identical_specs_have_empty_diff():
    spec = {"paths": {"/x": {"get": {"responses": {"200": {}}}}}}
    diff = diff_openapi_specs(spec, spec)
    assert diff.is_empty


def test_added_and_removed_paths():
    left = {"paths": {"/a": {"get": {"responses": {"200": {}}}}}}
    right = {"paths": {"/b": {"get": {"responses": {"200": {}}}}}}
    diff = diff_openapi_specs(left, right)
    assert diff.removed_paths == {"/a"}
    assert diff.added_paths == {"/b"}


def test_added_operation_on_existing_path():
    left = {"paths": {"/x": {"get": {"responses": {"200": {}}}}}}
    right = {
        "paths": {"/x": {
            "get": {"responses": {"200": {}}},
            "post": {"responses": {"201": {}}},
        }}
    }
    diff = diff_openapi_specs(left, right)
    assert "POST /x" in diff.added_operations


def test_schema_change_detected():
    left = {"paths": {"/x": {"get": {"responses": {"200": {"description": "ok"}}}}}}
    right = {"paths": {"/x": {"get": {"responses": {"200": {"description": "OK"}}}}}}
    diff = diff_openapi_specs(left, right)
    assert "GET /x" in diff.schema_changes
