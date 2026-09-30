"""Tests for the test-as-spec loop."""
from __future__ import annotations

import json

import pytest

from je_api_testka.ai.backend import NoOpAIBackend, set_ai_backend
from je_api_testka.cli.cli_main import main
from je_api_testka.spec.spec_loop import (
    check_records_against_spec,
    check_spec_against_tests,
    documented_operations,
    infer_spec_from_tests,
    missing_test_actions,
    uncovered_spec,
)
from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.test_record.test_record_class import test_record_instance

ITEM = {"type": "object", "required": ["id", "name"],
        "properties": {"id": {"type": "integer"}, "name": {"type": "string"}}}


def _spec(base_url: str = "https://api.invalid/v1") -> dict:
    return {
        "openapi": "3.0.3",
        "info": {"title": "Shop", "version": "2.0"},
        "servers": [{"url": base_url}],
        "components": {"schemas": {"Item": ITEM}},
        "paths": {
            "/items/{id}": {
                "parameters": [{"name": "id", "in": "path", "required": True, "example": 3}],
                "get": {"responses": {"200": {"content": {"application/json": {
                    "schema": {"$ref": "#/components/schemas/Item"}}}}}},
                "delete": {"responses": {"204": {}}},
            },
            "/items": {"post": {"requestBody": {"content": {"application/json": {"example": {"name": "n"}}}},
                                "responses": {"201": {"content": {"application/json": {
                                    "schema": {"$ref": "#/components/schemas/Item"}}}}}}},
        },
    }


def _record(path, method="GET", status=200, text='{"id": 1, "name": "a"}', body=None):
    return {"request_url": f"https://api.invalid/v1{path}", "request_method": method, "status_code": status,
            "text": text, "request_body": body}


def test_documented_operations():
    assert documented_operations(_spec()) == ["GET /items/{id}", "DELETE /items/{id}", "POST /items"]


def test_coverage_undocumented_and_drift():
    report = check_records_against_spec([
        _record("/items/1"), _record("/items/2"),
        _record("/items/3", text='{"id": "3", "name": "a"}'),
        _record("/orders/9"), _record("/orders/10"),
        _record("/items", method="POST", status=202, body=b'{"name": "n"}'),
        {"status_code": 200},
    ], _spec())
    assert report.covered == ["GET /items/{id}", "POST /items"]
    assert report.uncovered == ["DELETE /items/{id}"]
    assert report.undocumented == ["GET /orders/{id}"]
    assert report.problems == [
        ("GET /v1/items/3 -> 200", "response body $.body.id: expected type integer, got string"),
        ("POST /v1/items -> 202", "status 202 is not declared"),
    ]
    assert report.coverage == pytest.approx(2 / 3)
    failures = report.failures(min_coverage=0.9)
    assert failures[0] == "undocumented operation GET /orders/{id}" and failures[-1] == "coverage 67% is below 90%"
    assert "[UNTESTED] DELETE /items/{id}" in report.render_text()
    assert report.to_dict()["ok"] is False


def test_clean_run_passes():
    report = check_records_against_spec([_record("/items/1")], _spec())
    assert report.failures() == []
    assert report.to_dict(min_coverage=0.5)["failures"] == ["coverage 33% is below 50%"]


def test_uncovered_spec_keeps_only_untested_operations():
    trimmed = uncovered_spec(_spec(), ["DELETE /items/{id}"])
    assert list(trimmed["paths"]) == ["/items/{id}"]
    assert set(trimmed["paths"]["/items/{id}"]) == {"parameters", "delete"}
    assert trimmed["components"] == _spec()["components"]


def test_missing_test_actions_use_examples():
    set_ai_backend(NoOpAIBackend())
    report = check_records_against_spec([_record("/items/1")], _spec())
    assert missing_test_actions(_spec(), report) == [
        ["AT_test_api_method", {"http_method": "delete", "test_url": "https://api.invalid/v1/items/3",
                                "result_check_dict": {"status_code": 204}}],
        ["AT_test_api_method", {"http_method": "post", "test_url": "https://api.invalid/v1/items",
                                "json": {"name": "n"}, "result_check_dict": {"status_code": 201}}],
    ]
    assert missing_test_actions(_spec(), check_records_against_spec([], {"paths": {}})) == []


def test_inferred_spec_groups_under_committed_templates():
    inferred = infer_spec_from_tests([_record("/items/1"), _record("/items/2"), _record("/orders/5")], _spec())
    assert set(inferred["paths"]) == {"/items/{id}", "/orders/{id}"}
    assert inferred["paths"]["/items/{id}"]["get"]["parameters"] == [
        {"name": "id", "in": "path", "required": True, "schema": {"type": "string"}}]
    assert inferred["info"] == {"title": "Shop", "version": "2.0"}
    assert inferred["servers"] == _spec()["servers"]


def _provider_spec(base_url: str) -> dict:
    spec = _spec(base_url)
    spec["paths"]["/items/{id}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"] = {
        "type": "object", "required": ["id", "name"],
        "properties": {"id": {"type": "integer"}, "name": {"type": "string"},
                       "tags": {"type": "array", "items": {"type": "string"}}}}
    del spec["paths"]["/items/{id}"]["delete"]
    return spec


def test_loop_end_to_end_generated_tests_close_the_gap(provider, tmp_path):
    base_url, _states = provider
    set_ai_backend(NoOpAIBackend())
    spec_path = tmp_path / "openapi.json"
    spec_path.write_text(json.dumps(_provider_spec(base_url)), encoding="utf-8")
    execute_action([["AT_test_api_method", {"http_method": "get", "test_url": f"{base_url}/items/5",
                                            "timeout": 5}]])
    missing = tmp_path / "missing.json"
    with pytest.raises(APIAssertException, match="coverage 50% is below 100%"):
        check_spec_against_tests(str(spec_path), min_coverage=1.0, missing_actions_path=str(missing))

    # The generated actions exercise the untested operation, and then the loop passes.
    execute_action(json.loads(missing.read_text(encoding="utf-8")))
    assert test_record_instance.error_record_list == []
    result = check_spec_against_tests(str(spec_path), min_coverage=1.0,
                                      inferred_spec_path=str(tmp_path / "inferred.json"))
    assert result["ok"] is True and result["coverage"] == 1.0
    assert "/items/{id}" in json.loads((tmp_path / "inferred.json").read_text(encoding="utf-8"))["paths"]


def test_executor_command(provider, tmp_path):
    base_url, _states = provider
    spec_path = tmp_path / "openapi.json"
    spec_path.write_text(json.dumps(_provider_spec(base_url)), encoding="utf-8")
    record = execute_action([
        ["AT_test_api_method", {"http_method": "get", "test_url": f"{base_url}/items/5", "timeout": 5}],
        ["AT_check_spec_against_tests", {"spec_path": str(spec_path)}],
    ])
    assert list(record.values())[1]["covered"] == ["GET /items/{id}"]


def test_cli_spec_check(provider, tmp_path, capsys):
    base_url, _states = provider
    set_ai_backend(NoOpAIBackend())
    spec_path = tmp_path / "openapi.json"
    spec_path.write_text(json.dumps(_provider_spec(base_url)), encoding="utf-8")
    actions = tmp_path / "tests.json"
    actions.write_text(json.dumps([["AT_test_api_method", {"http_method": "get", "test_url": f"{base_url}/items/5",
                                                          "timeout": 5}]]), encoding="utf-8")
    assert main(["spec", "check", str(spec_path), "--run", str(actions), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["uncovered"] == ["POST /items"]
    assert main(["spec", "check", str(spec_path), "--run", str(actions), "--min-coverage", "1",
                 "--missing-actions", str(tmp_path / "gen" / "missing.json")]) == 1
    assert "[UNTESTED] POST /items" in capsys.readouterr().out
    assert json.loads((tmp_path / "gen" / "missing.json").read_text(encoding="utf-8"))[0][1]["http_method"] == "post"


def test_cli_spec_check_usage_errors(tmp_path):
    assert main(["spec", "check", str(tmp_path / "openapi.json")]) == 2
    assert main(["spec", "check", str(tmp_path / "missing.json"), "--report", "x.json"]) == 2
