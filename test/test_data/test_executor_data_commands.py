"""Integration tests: new data-layer AT_* commands work via the executor."""
from __future__ import annotations

from je_api_testka.data.variable_store import variable_store
from je_api_testka.utils.executor.action_executor import execute_action


def test_set_get_clear_variables_via_executor():
    variable_store.clear()
    execute_action([
        ["AT_set_variable", {"name": "token", "value": "abc"}],
    ])
    assert variable_store.get("token") == "abc"
    execute_action([["AT_clear_variables"]])
    assert variable_store.get("token") is None


def test_extract_and_render_via_executor():
    variable_store.clear()
    execute_action([
        ["AT_extract_and_store", {
            "response": {"data": {"id": 99}},
            "path": "data.id",
            "name": "user_id",
        }],
    ])
    assert variable_store.get("user_id") == 99
    record = execute_action([
        ["AT_render_template", {"payload": "user/{{user_id}}"}],
    ])
    rendered_value = next(iter(record.values()))
    assert rendered_value == "user/99"
    variable_store.clear()


def test_fake_uuid_via_executor():
    record = execute_action([["AT_fake_uuid"]])
    value = next(iter(record.values()))
    assert isinstance(value, str)
    assert len(value) == 36


def test_load_env_profile_via_executor(tmp_path):
    import json

    profile_path = tmp_path / "dev.json"
    profile_path.write_text(json.dumps({"base": "https://x.invalid"}), encoding="utf-8")
    variable_store.clear()
    execute_action([
        ["AT_load_env_profile", {"file_path": str(profile_path)}],
    ])
    assert variable_store.get("base") == "https://x.invalid"
    variable_store.clear()
