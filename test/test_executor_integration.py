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
    # Integrations
    "AT_notify_via_webhook", "AT_post_pr_comment",
    "AT_curl_to_action", "AT_convert_har",
    # Security
    "AT_cors_preflight", "AT_probe_rate_limit", "AT_probe_ssrf",
    # Spec
    "AT_infer_schema", "AT_records_to_openapi", "AT_openapi_changelog",
    # AI
    "AT_classify_failures", "AT_generate_fake_payload",
    "AT_generate_tests_from_openapi",
)


@pytest.mark.parametrize("command", EXPECTED_NEW_COMMANDS)
def test_command_registered(command):
    assert command in executor.event_dict, f"{command} not registered in executor"


def test_chain_env_variable_template_diff(tmp_path):
    """Multi-step chain that uses several modules together."""
    variable_store.clear()
    profile = tmp_path / "dev.json"
    profile.write_text(json.dumps({"base": "http://example.invalid"}), encoding="utf-8")

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
    assert any(value == "http://example.invalid/users/7" for value in rendered)
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
