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
