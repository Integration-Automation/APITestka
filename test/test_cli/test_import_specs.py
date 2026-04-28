"""Tests for OpenAPI / Postman importers."""
from __future__ import annotations

import json

import pytest

from je_api_testka.cli.import_specs import (
    convert_openapi,
    convert_postman,
    convert_spec_file,
)
from je_api_testka.utils.exception.exceptions import APITesterException


def test_convert_openapi_extracts_path_methods():
    spec = {
        "servers": [{"url": "https://api.example.invalid"}],
        "paths": {
            "/users": {
                "get": {"responses": {"200": {"description": "ok"}}},
                "post": {"responses": {"201": {"description": "created"}}},
            },
            "/users/{id}": {"delete": {"responses": {"204": {"description": "gone"}}}},
        },
    }
    actions = convert_openapi(spec)
    methods = sorted(a["AT_test_api_method_requests"]["http_method"] for a in actions)
    assert methods == ["delete", "get", "post"]
    urls = {a["AT_test_api_method_requests"]["test_url"] for a in actions}
    assert "https://api.example.invalid/users" in urls


def test_convert_postman_handles_nested_folders():
    collection = {
        "item": [
            {
                "name": "folder",
                "item": [
                    {
                        "name": "ping",
                        "request": {
                            "method": "GET",
                            "url": {"raw": "https://api.example.invalid/ping"},
                            "header": [{"key": "X-Test", "value": "1"}],
                        },
                    }
                ],
            }
        ]
    }
    actions = convert_postman(collection)
    assert len(actions) == 1
    body = actions[0]["AT_test_api_method_requests"]
    assert body["http_method"] == "get"
    assert body["headers"] == {"X-Test": "1"}


def test_convert_spec_file_unsupported_format(tmp_path):
    target = tmp_path / "spec.json"
    target.write_text(json.dumps({}), encoding="utf-8")
    with pytest.raises(APITesterException):
        convert_spec_file(str(target), spec_format="raml")
