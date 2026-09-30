"""Tests for the apitestka CLI parser."""
from __future__ import annotations

import json

import pytest

from je_api_testka.cli.cli_main import build_parser, main


def test_parser_run_subcommand(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["run", str(tmp_path / "missing.json")])
    assert args.command == "run"
    assert args.path.endswith("missing.json")


def test_parser_import_defaults(tmp_path):
    parser = build_parser()
    args = parser.parse_args(["import", "in.json", "out.json"])
    assert args.format == "openapi"


def test_main_invokes_import(tmp_path):
    spec = {
        "paths": {"/x": {"get": {"responses": {"200": {"description": "ok"}}}}},
        "servers": [{"url": "https://example.invalid"}],
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec), encoding="utf-8")
    out_path = tmp_path / "out.json"

    rc = main(["import", str(spec_path), str(out_path), "--format", "openapi"])
    assert rc == 0
    assert json.loads(out_path.read_text(encoding="utf-8"))


def test_main_run_with_missing_path_returns_2(tmp_path):
    rc = main(["run", str(tmp_path / "does_not_exist.json")])
    assert rc == 2


def _write_report(path, url="https://x.invalid/users"):
    path.write_text(json.dumps({"Success_Test1": {
        "request_url": url, "request_method": "GET", "status_code": "200", "text": '{"id": 1}',
    }}), encoding="utf-8")
    return str(path)


def test_openapi_from_report_writes_file(tmp_path):
    report = _write_report(tmp_path / "run_success.json")
    out_path = tmp_path / "spec.json"
    rc = main(["openapi", "--report", report, "-o", str(out_path), "--title", "Shop", "--api-version", "2.0"])
    spec = json.loads(out_path.read_text(encoding="utf-8"))
    assert rc == 0
    assert spec["info"] == {"title": "Shop", "version": "2.0"}
    assert "/users" in spec["paths"]


def test_openapi_runs_actions_then_prints(tmp_path, mock_url, capsys):
    actions = tmp_path / "actions.json"
    actions.write_text(json.dumps([["AT_test_api_method", {
        "http_method": "get", "test_url": f"{mock_url}/get", "timeout": 30,
    }]]), encoding="utf-8")
    rc = main(["openapi", "--run", str(actions)])
    assert rc == 0
    assert "/get" in json.loads(capsys.readouterr().out)["paths"]


def test_openapi_needs_a_source():
    assert main(["openapi"]) == 2


def test_openapi_with_missing_run_path_returns_2(tmp_path):
    assert main(["openapi", "--run", str(tmp_path / "missing.json")]) == 2


def test_openapi_without_records_returns_1(tmp_path):
    empty = tmp_path / "empty_success.json"
    empty.write_text("{}", encoding="utf-8")
    assert main(["openapi", "--report", str(empty), "-o", str(tmp_path / "spec.json")]) == 1
    assert not (tmp_path / "spec.json").exists()
