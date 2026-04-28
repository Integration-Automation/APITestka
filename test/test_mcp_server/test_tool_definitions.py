"""Tests for the APITestka MCP tool catalogue."""
from __future__ import annotations

import json

import pytest

from je_api_testka.mcp_server.tool_definitions import APITESTKA_TOOLS, dispatch_tool
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_each_tool_has_required_fields():
    for spec in APITESTKA_TOOLS:
        assert spec.name.startswith("apitestka_")
        assert spec.description
        assert isinstance(spec.input_schema, dict)
        assert spec.input_schema.get("type") == "object"
        assert callable(spec.handler)


def test_dispatch_unknown_tool_raises():
    with pytest.raises(APITesterException):
        dispatch_tool("apitestka_does_not_exist", {})


def test_clear_records_tool():
    test_record_instance.test_record_list.append({"x": 1})
    result = dispatch_tool("apitestka_clear_records", {})
    assert result == {"cleared": True}
    assert test_record_instance.test_record_list == []


def test_get_records_tool_returns_lists():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({"x": 1})
    result = dispatch_tool("apitestka_get_records", {})
    assert "successes" in result
    assert "failures" in result
    test_record_instance.clean_record()


def test_curl_to_action_tool():
    result = dispatch_tool("apitestka_curl_to_action", {"curl_command": "curl https://x.invalid"})
    assert "AT_test_api_method_requests" in result


def test_render_markdown_tool_returns_string():
    test_record_instance.clean_record()
    result = dispatch_tool("apitestka_render_markdown", {})
    assert isinstance(result, str)
    assert "APITestka Report" in result


def test_records_to_openapi_tool():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({
        "request_url": "https://x.invalid/health",
        "request_method": "GET",
        "status_code": 200,
        "text": "",
    })
    result = dispatch_tool("apitestka_records_to_openapi", {"title": "Test"})
    assert result["info"]["title"] == "Test"
    assert "/health" in result["paths"]
    test_record_instance.clean_record()


def test_run_action_tool_dispatches():
    test_record_instance.clean_record()
    result = dispatch_tool("apitestka_run_action", {"actions": [["AT_fake_uuid"]]})
    assert isinstance(result, dict) and result
    payload_value = next(iter(result.values()))
    assert isinstance(payload_value, str)


def test_run_action_tool_validates_input():
    with pytest.raises(APITesterException):
        dispatch_tool("apitestka_run_action", {"actions": []})


def test_har_import_tool(tmp_path):
    har_path = tmp_path / "out.har"
    har_path.write_text(json.dumps({"log": {"entries": []}}), encoding="utf-8")
    result = dispatch_tool("apitestka_har_import", {"file_path": str(har_path)})
    assert result == []
