"""
End-to-end executor integration tests.

These verify that the executor's event_dict accepts every AT_* command we
registered across the new commits, and that a multi-step chain (env profile
+ variable + render template + diff + report) executes without crashing.
"""
from __future__ import annotations

import json

import pytest

from je_api_testka.data.variable_store import variable_store
from je_api_testka.utils.executor.action_executor import execute_action, executor


EXPECTED_NEW_COMMANDS = (
    # Data layer
    "AT_set_variable", "AT_get_variable", "AT_clear_variables",
    "AT_extract_and_store", "AT_render_template",
    "AT_fake_uuid", "AT_fake_email", "AT_fake_word",
    "AT_load_env_profile",
    # Diff / SLA
    "AT_diff_payloads", "AT_diff_openapi_specs", "AT_assert_sla",
    # Cassette
    "AT_cassette_lookup", "AT_cassette_record",
    # Reports
    "AT_render_markdown", "AT_generate_markdown_report",
    "AT_diff_runs", "AT_generate_badge",
    "AT_record_current_run", "AT_list_trend_rows",
    "AT_generate_junit_report", "AT_generate_allure_report",
    # Integrations
    "AT_notify_via_webhook", "AT_post_pr_comment",
    "AT_curl_to_action", "AT_convert_har",
    # Security
    "AT_cors_preflight", "AT_probe_rate_limit", "AT_probe_ssrf",
    "AT_scan_security_headers", "AT_fuzz_string_inputs",
    "AT_run_pip_audit",
    "AT_basic_auth_header", "AT_bearer_token_header",
    "AT_build_jwt", "AT_aws_sigv4_headers",
    # Spec
    "AT_infer_schema", "AT_records_to_openapi", "AT_openapi_changelog",
    # AI
    "AT_classify_failures", "AT_generate_fake_payload",
    "AT_generate_tests_from_openapi",
    # Extra protocols
    "AT_test_api_method_websocket",
    "AT_test_api_method_sse",
    "AT_test_api_method_graphql",
    # Schema / snapshot assertions
    "AT_check_json_schema", "AT_check_jsonpath", "AT_assert_snapshot",
    # Mock server advanced
    "AT_mock_add_dynamic_route", "AT_mock_add_template_route",
    "AT_mock_add_webhook", "AT_mock_add_proxy", "AT_mock_load_openapi",
    # Runner
    "AT_run_actions_parallel", "AT_filter_actions_by_tag", "AT_order_actions",
)


@pytest.mark.parametrize("command", EXPECTED_NEW_COMMANDS)
def test_command_registered(command):
    assert command in executor.event_dict, f"{command} not registered in executor"


def test_chain_env_variable_template_diff(tmp_path):
    """Multi-step chain that uses several modules together."""
    variable_store.clear()
    profile = tmp_path / "dev.json"
    profile.write_text(json.dumps({"base": "https://example.invalid"}), encoding="utf-8")

    record = execute_action([
        ["AT_load_env_profile", {"file_path": str(profile)}],
        ["AT_set_variable", {"name": "user_id", "value": 7}],
        ["AT_render_template", {"payload": "{{base}}/users/{{user_id}}"}],
        ["AT_diff_payloads", {
            "left": {"a": 1, "b": 2},
            "right": {"a": 1, "b": 3},
        }],
    ])
    rendered = list(record.values())
    assert any(value == "https://example.invalid/users/7" for value in rendered)
    diff = next(value for value in rendered if hasattr(value, "changed"))
    assert diff.changed == {"b": (2, 3)}
    variable_store.clear()


def test_curl_import_then_dispatch(tmp_path):
    record = execute_action([
        ["AT_curl_to_action", {"curl_command": "curl https://api.invalid/v1/health"}],
    ])
    action = next(iter(record.values()))
    body = action["AT_test_api_method_requests"]
    assert body["http_method"] == "get"
    assert body["test_url"] == "https://api.invalid/v1/health"


def test_har_import_then_count(tmp_path):
    har = {
        "log": {
            "entries": [
                {"request": {"method": "GET", "url": "https://api.invalid/x", "headers": []}},
                {"request": {"method": "POST", "url": "https://api.invalid/y", "headers": [],
                             "postData": {"text": "{\"a\":1}"}}},
            ]
        }
    }
    har_path = tmp_path / "out.har"
    har_path.write_text(json.dumps(har), encoding="utf-8")
    record = execute_action([["AT_convert_har", {"file_path": str(har_path)}]])
    actions = next(iter(record.values()))
    assert len(actions) == 2


def test_auth_helpers_via_executor():
    record = execute_action([
        ["AT_basic_auth_header", {"username": "alice", "password": "s3cret"}],
        ["AT_bearer_token_header", {"token": "abc"}],
    ])
    values = list(record.values())
    assert values[0]["Authorization"].startswith("Basic ")
    assert values[1]["Authorization"] == "Bearer abc"


def test_runner_helpers_via_executor():
    actions = [
        ["AT_fake_uuid", {"id": "u1", "tags": ["smoke"]}],
        ["AT_fake_uuid", {"id": "u2", "tags": ["regression"]}],
    ]
    record = execute_action([
        ["AT_filter_actions_by_tag", {"actions": actions, "wanted_tags": ["smoke"]}],
        ["AT_order_actions", {"actions": actions}],
    ])
    values = list(record.values())
    assert len(values[0]) == 1
    assert len(values[1]) == 2


def test_security_scan_via_executor():
    record = execute_action([
        ["AT_scan_security_headers", {"headers": {}}],
        ["AT_fuzz_string_inputs", {"limit": 3}],
    ])
    findings, fuzz = list(record.values())
    assert len(findings) > 0
    assert len(fuzz) == 3


def test_schema_assertions_via_executor():
    pytest.importorskip("jsonschema")
    record = execute_action([
        ["AT_check_json_schema", {
            "payload": {"name": "alice"},
            "schema": {"type": "object", "required": ["name"]},
        }],
    ])
    # The function returns None on success; the executor records None.
    assert next(iter(record.values())) is None


def test_mock_server_methods_via_executor():
    """The mock server bound methods should be reachable via AT_*."""
    spec = {"paths": {"/health": {
        "get": {"responses": {"200": {"content": {"text/plain": {"example": "ok"}}}}},
    }}}
    record = execute_action([
        ["AT_mock_load_openapi", {"spec": spec}],
    ])
    registered = next(iter(record.values()))
    assert "GET /health" in registered
