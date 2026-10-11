"""
Actions produced by the converters must run through ``execute_action`` as they are.

Regression: OpenAPI/Postman import, cURL and HAR import, AI test generation,
``scaffold`` and the ``apitestka_test_api`` MCP tool emitted
``AT_test_api_method_requests`` (never registered) and, except scaffold and
MCP, the dict shape ``{"AT_...": {...}}`` the executor cannot run.
"""
from __future__ import annotations

import json

from je_api_testka.ai.backend import NoOpAIBackend, set_ai_backend
from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.cli.import_specs import convert_openapi, convert_postman
from je_api_testka.cli.scaffold_test import scaffold_action_list
from je_api_testka.integrations.curl_import import curl_to_action
from je_api_testka.integrations.har_import import convert_har
from je_api_testka.mcp_server.tool_definitions import dispatch_tool
from je_api_testka.utils.executor.action_executor import execute_action, executor
from je_api_testka.utils.executor.request_action import REQUEST_COMMAND, build_request_action
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def _run_cleanly(actions: list) -> None:
    record = execute_action(actions)
    errors = [value for value in record.values() if isinstance(value, str) and "Error(" in value]
    assert errors == []
    assert test_record_instance.error_record_list == []
    assert len(test_record_instance.test_record_list) == sum(1 for a in actions if a[0] == REQUEST_COMMAND)


def test_request_command_is_registered():
    assert REQUEST_COMMAND in executor.event_dict


def test_build_request_action_body_kinds():
    assert build_request_action("GET", "u") == [REQUEST_COMMAND, {"http_method": "get", "test_url": "u"}]
    assert build_request_action("POST", "u", body={"a": 1})[1]["json"] == {"a": 1}
    assert build_request_action("POST", "u", body="a=1")[1]["data"] == "a=1"
    action = build_request_action("GET", "u", headers={"X": "1"}, timeout=3)
    assert action[1]["headers"] == {"X": "1"} and action[1]["timeout"] == 3


def test_openapi_import_runs(mock_url):
    spec = {"servers": [{"url": mock_url}], "paths": {"/get": {"get": {"responses": {}}}}}
    _run_cleanly(convert_openapi(spec))


def test_postman_import_runs_and_sends_text_as_data(mock_url):
    collection = {"item": [{"request": {
        "method": "POST", "url": {"raw": f"{mock_url}/post"}, "body": {"mode": "raw", "raw": "a=1"},
    }}]}
    actions = convert_postman(collection)
    assert actions[0][1]["data"] == "a=1"
    _run_cleanly(actions)


def test_curl_import_runs(mock_url):
    _run_cleanly([curl_to_action(f"curl {mock_url}/get -H 'Accept: application/json'")])


def test_har_import_runs(mock_url, tmp_path):
    har = {"log": {"entries": [{"request": {
        "method": "POST", "url": f"{mock_url}/post", "headers": [], "postData": {"text": '{"a": 1}'},
    }}]}}
    path = tmp_path / "t.har"
    path.write_text(json.dumps(har), encoding="utf-8")
    _run_cleanly(convert_har(str(path)))


def test_ai_fallback_actions_run(mock_url):
    set_ai_backend(NoOpAIBackend())
    spec = {"servers": [{"url": mock_url}], "paths": {"/get": {"get": {"responses": {}}}}}
    _run_cleanly(generate_tests_from_openapi(spec))


def test_scaffold_runs_including_tags_and_sla(mock_url):
    # The request carries runner tags; the executor strips them before calling requests.
    _run_cleanly(scaffold_action_list(f"{mock_url}/get"))


def test_runner_metadata_is_stripped_before_the_call(mock_url):
    _run_cleanly([build_request_action("GET", f"{mock_url}/get", id="a", depends_on=[], tags=["smoke"])])


def test_mcp_test_api_tool_sends_the_request(mock_url):
    dispatch_tool("apitestka_test_api", {"url": f"{mock_url}/get", "timeout": 30})
    assert len(test_record_instance.test_record_list) == 1
