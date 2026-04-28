"""
Tool catalogue exposed by the APITestka MCP server.

Each entry has:
* ``name``         - tool name visible to the MCP client.
* ``description``  - short help string.
* ``input_schema`` - JSON Schema for the arguments object.
* ``handler``      - callable taking ``(arguments: dict)`` and returning a
                     JSON-serialisable result.

Defining the catalogue here (decoupled from the network layer) lets unit
tests dispatch tools without spinning up the actual MCP transport.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from je_api_testka.integrations.curl_import import curl_to_action
from je_api_testka.integrations.har_import import convert_har
from je_api_testka.spec.records_to_openapi import records_to_openapi
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.generate_report.markdown_report import render_markdown
from je_api_testka.utils.test_record.test_record_class import test_record_instance


@dataclass
class MCPToolSpec:
    """One MCP tool exposed to the client."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable[[Dict[str, Any]], Any]


def _handle_run_action(arguments: Dict[str, Any]) -> Any:
    actions = arguments.get("actions") or []
    if not isinstance(actions, list) or not actions:
        raise APITesterException("'actions' must be a non-empty list")
    record = execute_action(actions)
    return {key: _jsonable(value) for key, value in record.items()}


def _handle_test_api(arguments: Dict[str, Any]) -> Any:
    method = arguments.get("method", "GET")
    url = arguments["url"]
    timeout = arguments.get("timeout", 30)
    body = arguments.get("body")
    headers = arguments.get("headers")
    payload: dict = {"http_method": method.lower(), "test_url": url, "timeout": timeout}
    if headers:
        payload["headers"] = headers
    if body is not None:
        payload["json"] = body
    record = execute_action([["AT_test_api_method_requests", payload]])
    return {key: _jsonable(value) for key, value in record.items()}


def _handle_curl_to_action(arguments: Dict[str, Any]) -> Any:
    return curl_to_action(arguments["curl_command"])


def _handle_har_import(arguments: Dict[str, Any]) -> Any:
    return convert_har(arguments["file_path"])


def _handle_render_markdown(_arguments: Dict[str, Any]) -> str:
    return render_markdown()


def _handle_records_to_openapi(arguments: Dict[str, Any]) -> Any:
    return records_to_openapi(
        title=arguments.get("title", "APITestka Inferred"),
        version=arguments.get("version", "0.1.0"),
    )


def _handle_clear_records(_arguments: Dict[str, Any]) -> dict:
    test_record_instance.clean_record()
    return {"cleared": True}


def _handle_get_records(_arguments: Dict[str, Any]) -> dict:
    return {
        "successes": [_jsonable(record) for record in test_record_instance.test_record_list],
        "failures": [_jsonable(record) for record in test_record_instance.error_record_list],
    }


def _jsonable(value: Any) -> Any:
    """Coerce nested values into JSON-serialisable form for the MCP transport."""
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        if isinstance(value, dict):
            return {str(k): _jsonable(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_jsonable(v) for v in value]
        if hasattr(value, "__dict__"):
            return _jsonable(value.__dict__)
        return repr(value)


APITESTKA_TOOLS: List[MCPToolSpec] = [
    MCPToolSpec(
        name="apitestka_run_action",
        description="Execute an APITestka action list (executor JSON).",
        input_schema={
            "type": "object",
            "properties": {
                "actions": {
                    "type": "array",
                    "description": "List of [command, kwargs] pairs as understood by execute_action.",
                    "items": {"type": "array"},
                }
            },
            "required": ["actions"],
        },
        handler=_handle_run_action,
    ),
    MCPToolSpec(
        name="apitestka_test_api",
        description="Issue a single HTTP request via the requests backend.",
        input_schema={
            "type": "object",
            "properties": {
                "method": {"type": "string", "default": "GET"},
                "url": {"type": "string"},
                "headers": {"type": "object"},
                "body": {},
                "timeout": {"type": "integer", "default": 30},
            },
            "required": ["url"],
        },
        handler=_handle_test_api,
    ),
    MCPToolSpec(
        name="apitestka_curl_to_action",
        description="Convert a curl command line into an APITestka action dict.",
        input_schema={
            "type": "object",
            "properties": {"curl_command": {"type": "string"}},
            "required": ["curl_command"],
        },
        handler=_handle_curl_to_action,
    ),
    MCPToolSpec(
        name="apitestka_har_import",
        description="Convert a HAR file into a list of APITestka actions.",
        input_schema={
            "type": "object",
            "properties": {"file_path": {"type": "string"}},
            "required": ["file_path"],
        },
        handler=_handle_har_import,
    ),
    MCPToolSpec(
        name="apitestka_render_markdown",
        description="Render the current test record as a Markdown report.",
        input_schema={"type": "object", "properties": {}},
        handler=_handle_render_markdown,
    ),
    MCPToolSpec(
        name="apitestka_records_to_openapi",
        description="Reconstruct an OpenAPI 3.x document from the current test record.",
        input_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "version": {"type": "string"},
            },
        },
        handler=_handle_records_to_openapi,
    ),
    MCPToolSpec(
        name="apitestka_clear_records",
        description="Clear the in-memory success and failure records.",
        input_schema={"type": "object", "properties": {}},
        handler=_handle_clear_records,
    ),
    MCPToolSpec(
        name="apitestka_get_records",
        description="Return the current success and failure records.",
        input_schema={"type": "object", "properties": {}},
        handler=_handle_get_records,
    ),
]


def dispatch_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Look up a tool by name and invoke its handler."""
    for tool in APITESTKA_TOOLS:
        if tool.name == name:
            return tool.handler(arguments or {})
    raise APITesterException(f"unknown MCP tool {name}")
