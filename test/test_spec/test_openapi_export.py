"""Tests for building and writing OpenAPI documents from saved reports."""
from __future__ import annotations

import json

import pytest

from je_api_testka import execute_action, generate_json_report
from je_api_testka.spec.openapi_export import build_openapi, export_openapi, load_report_records
from je_api_testka.utils.exception.exceptions import APIJsonReportException
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def _write(path, document):
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


def test_round_trip_through_generate_json_report(mock_url, tmp_path):
    execute_action([["AT_test_api_method", {
        "http_method": "post", "test_url": f"{mock_url}/post?page=1", "json": {"name": "a"}, "timeout": 30,
    }]])
    generate_json_report(str(tmp_path / "run"))
    test_record_instance.clean_record()

    records = load_report_records(str(tmp_path / "run_success.json"))

    assert len(records) == 1
    assert records[0]["request_body"] == b'{"name": "a"}'
    spec = build_openapi([str(tmp_path / "run_success.json")])
    operation = spec["paths"]["/post"]["post"]
    assert operation["parameters"][0]["name"] == "page"
    assert "application/json" in operation["requestBody"]["content"]
    assert "application/json" in operation["responses"]["200"]["content"]


def test_report_none_strings_become_none(tmp_path):
    path = _write(tmp_path / "r.json", {"Success_Test1": {
        "request_url": "https://x.invalid/a", "request_method": "GET", "status_code": "200",
        "text": "", "request_body": "None",
    }})
    assert load_report_records(path)[0]["request_body"] is None


def test_accepts_mcp_get_records_shape(tmp_path):
    path = _write(tmp_path / "r.json", {"successes": [{"request_url": "https://x.invalid/a"}], "failures": []})
    assert load_report_records(path) == [{"request_url": "https://x.invalid/a"}]


def test_accepts_plain_record_list(tmp_path):
    path = _write(tmp_path / "r.json", [{"request_url": "https://x.invalid/a"}])
    assert len(load_report_records(path)) == 1


@pytest.mark.parametrize("document", [[1], {"Success_Test1": {"text": "no url"}}, "text"])
def test_rejects_entries_that_are_not_records(tmp_path, document):
    with pytest.raises(APIJsonReportException):
        load_report_records(_write(tmp_path / "r.json", document))


def test_rejects_unreadable_file(tmp_path):
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(APIJsonReportException):
        load_report_records(str(tmp_path / "bad.json"))
    with pytest.raises(APIJsonReportException):
        load_report_records(str(tmp_path / "missing.json"))


def test_build_combines_current_record_and_reports(tmp_path):
    test_record_instance.test_record_list.append({"request_url": "https://x.invalid/live", "status_code": 200})
    path = _write(tmp_path / "r.json", [{"request_url": "https://x.invalid/saved"}])
    spec = build_openapi([path], title="T", version="9")
    assert set(spec["paths"]) == {"/live", "/saved"}
    assert spec["info"] == {"title": "T", "version": "9"}


def test_export_writes_utf8_json(tmp_path):
    path = _write(tmp_path / "r.json", [{"request_url": "https://x.invalid/a", "text": '{"name": "測試"}'}])
    written = export_openapi(str(tmp_path / "spec.json"), [path])
    spec = json.loads((tmp_path / "spec.json").read_text(encoding="utf-8"))
    assert written == str(tmp_path / "spec.json")
    assert "/a" in spec["paths"]


def test_export_through_executor(tmp_path):
    test_record_instance.test_record_list.append({"request_url": "https://x.invalid/a", "status_code": 200})
    execute_action([["AT_export_openapi", {"output_path": str(tmp_path / "spec.json")}]])
    assert "/a" in json.loads((tmp_path / "spec.json").read_text(encoding="utf-8"))["paths"]
