"""Tests for the file-level contract steps, their CLI and the executor commands."""
from __future__ import annotations

import json

import pytest

from je_api_testka.cli.cli_main import main
from je_api_testka.contract.commands import (
    check_contract_against_openapi,
    read_openapi,
    verify_contract,
    write_contract,
)
from je_api_testka.contract.pact import read_pact
from je_api_testka.spec.openapi_export import export_openapi
from je_api_testka.utils.exception.exceptions import APIContractException
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def _call_provider(base_url: str) -> None:
    execute_action([
        ["AT_test_api_method", {"http_method": "get", "test_url": f"{base_url}/items/3", "timeout": 5}],
        ["AT_test_api_method", {"http_method": "post", "test_url": f"{base_url}/items",
                                "json": {"name": "n"}, "timeout": 5}],
    ])


def test_bidirectional_flow_end_to_end(provider, tmp_path):
    base_url, _states = provider
    # Consumer side: its tests talk to the provider (or a mock) and the run becomes the contract.
    _call_provider(base_url)
    contract = write_contract(str(tmp_path / "web-shop.json"), "web", "shop")
    # Provider side: its own test run becomes the OpenAPI document it publishes.
    openapi = export_openapi(str(tmp_path / "openapi.json"))
    test_record_instance.clean_record()

    assert [i["description"] for i in read_pact(contract)["interactions"]] == [
        "GET /items/3 -> 200", "POST /items -> 201"]
    assert check_contract_against_openapi(contract, openapi)["ok"] is True
    assert verify_contract(contract, base_url, timeout=5)["ok"] is True


def test_write_contract_needs_records(tmp_path):
    with pytest.raises(APIContractException):
        write_contract(str(tmp_path / "c.json"), "web", "shop")


def test_verify_contract_raises_with_the_report(provider, tmp_path):
    base_url, _states = provider
    test_record_instance.test_record_list.append({
        "request_url": f"{base_url}/items/1", "request_method": "GET", "status_code": 200, "text": '{"id": "x"}'})
    contract = write_contract(str(tmp_path / "c.json"), "web", "shop")
    with pytest.raises(APIContractException, match="expected a string"):
        verify_contract(contract, base_url, timeout=5)


def test_read_openapi_errors(tmp_path):
    (tmp_path / "list.json").write_text("[]", encoding="utf-8")
    for name in ("list.json", "missing.json"):
        with pytest.raises(APIContractException):
            read_openapi(str(tmp_path / name))


def test_executor_commands(provider, tmp_path):
    base_url, _states = provider
    _call_provider(base_url)
    contract = str(tmp_path / "c.json")
    openapi = str(tmp_path / "o.json")
    record = execute_action([
        ["AT_write_contract", {"output_path": contract, "consumer": "web", "provider": "shop"}],
        ["AT_export_openapi", {"output_path": openapi}],
        ["AT_check_contract_against_openapi", {"contract_path": contract, "openapi_path": openapi}],
        ["AT_verify_contract", {"contract_path": contract, "base_url": base_url, "timeout": 5}],
    ])
    values = list(record.values())
    assert values[2]["ok"] is True and values[3]["ok"] is True


def _report(tmp_path, base_url: str) -> str:
    path = tmp_path / "run_success.json"
    path.write_text(json.dumps({"Success_Test1": {
        "request_url": f"{base_url}/items/1", "request_method": "GET", "status_code": "200",
        "text": '{"id": 1, "name": "a"}', "request_body": "None",
    }}), encoding="utf-8")
    return str(path)


def test_cli_record_verify_compare(provider, tmp_path, capsys):
    base_url, _states = provider
    contract = str(tmp_path / "pacts" / "web-shop.json")
    assert main(["contract", "record", "--report", _report(tmp_path, base_url),
                 "--consumer", "web", "--provider", "shop", "-o", contract]) == 0
    assert main(["contract", "verify", contract, "--base-url", base_url, "--json"]) == 0
    assert json.loads(capsys.readouterr().out.split("\n", 1)[1])["ok"] is True

    spec = tmp_path / "openapi.json"
    spec.write_text(json.dumps({"paths": {"/items/{id}": {"get": {"responses": {"200": {}}}}}}), encoding="utf-8")
    assert main(["contract", "compare", contract, str(spec)]) == 0
    spec.write_text(json.dumps({"paths": {}}), encoding="utf-8")
    assert main(["contract", "compare", contract, str(spec)]) == 1
    assert "no operation for GET /items/1" in capsys.readouterr().out


def test_cli_verify_failure_exit_code(provider, tmp_path):
    base_url, _states = provider
    contract = tmp_path / "c.json"
    contract.write_text(json.dumps({
        "consumer": {"name": "web"}, "provider": {"name": "shop"},
        "interactions": [{"description": "x", "request": {"method": "GET", "path": "/items/1"},
                          "response": {"status": 404}}]}), encoding="utf-8")
    assert main(["contract", "verify", str(contract), "--base-url", base_url]) == 1


def test_cli_usage_errors(tmp_path):
    assert main(["contract", "record", "--consumer", "a", "--provider", "b", "-o", str(tmp_path / "c.json")]) == 2
    empty = tmp_path / "empty.json"
    empty.write_text("{}", encoding="utf-8")
    assert main(["contract", "record", "--report", str(empty), "--consumer", "a", "--provider", "b",
                 "-o", str(tmp_path / "c.json")]) == 1
    assert main(["contract", "verify", str(tmp_path / "missing.json"), "--base-url", "http://127.0.0.1:9"]) == 2
    assert main(["contract", "compare", str(tmp_path / "missing.json"), str(empty)]) == 2
