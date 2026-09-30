"""Tests for the test_record -> OpenAPI inferer."""
from __future__ import annotations

from je_api_testka.spec.records_to_openapi import records_to_openapi


def test_groups_by_path_and_method():
    records = [
        {
            "request_url": "https://x.invalid/users",
            "request_method": "GET",
            "status_code": 200,
            "text": '{"id": 1}',
        },
        {
            "request_url": "https://x.invalid/users",
            "request_method": "POST",
            "status_code": 201,
            "text": "",
        },
    ]
    spec = records_to_openapi(records=records)
    assert "/users" in spec["paths"]
    assert "get" in spec["paths"]["/users"]
    assert "post" in spec["paths"]["/users"]


def test_skips_records_without_url():
    spec = records_to_openapi(records=[{"status_code": 200}])
    assert spec["paths"] == {}


def test_default_response_when_body_empty():
    records = [{
        "request_url": "https://x.invalid/health",
        "request_method": "GET",
        "status_code": 200,
        "text": "",
    }]
    spec = records_to_openapi(records=records)
    assert spec["paths"]["/health"]["get"]["responses"]["200"]


def _record(url="https://x.invalid/users", method="GET", status=200, text="", body=None):
    return {"request_url": url, "request_method": method, "status_code": status,
            "text": text, "request_body": body}


def test_body_less_response_has_no_content():
    # Regression: an empty body used to produce content {"application/json": {"text/plain": {}}}.
    spec = records_to_openapi(records=[_record(text="")])
    assert spec["paths"]["/users"]["get"]["responses"]["200"] == {"description": "inferred"}


def test_json_response_schema_under_application_json():
    spec = records_to_openapi(records=[_record(text='{"id": 1}')])
    content = spec["paths"]["/users"]["get"]["responses"]["200"]["content"]
    assert content == {"application/json": {"schema": {
        "type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"],
    }}}


def test_plain_text_response_under_text_plain():
    spec = records_to_openapi(records=[_record(text="pong")])
    content = spec["paths"]["/users"]["get"]["responses"]["200"]["content"]
    assert content == {"text/plain": {"schema": {"type": "string"}}}


def test_status_codes_of_one_operation_accumulate():
    # Regression: the last record used to replace the whole operation.
    spec = records_to_openapi(records=[_record(status=200), _record(status=404)])
    assert set(spec["paths"]["/users"]["get"]["responses"]) == {"200", "404"}


def test_query_parameter_names_accumulate_once():
    spec = records_to_openapi(records=[
        _record(url="https://x.invalid/users?page=1&size=5"),
        _record(url="https://x.invalid/users?page=2&sort=name"),
    ])
    parameters = spec["paths"]["/users"]["get"]["parameters"]
    assert [parameter["name"] for parameter in parameters] == ["page", "size", "sort"]
    assert all(parameter["in"] == "query" for parameter in parameters)


def test_operation_without_query_has_no_parameters_key():
    spec = records_to_openapi(records=[_record()])
    assert "parameters" not in spec["paths"]["/users"]["get"]


def test_json_request_body_bytes_become_request_body_schema():
    spec = records_to_openapi(records=[_record(method="POST", status=201, body=b'{"name": "a"}')])
    request_body = spec["paths"]["/users"]["post"]["requestBody"]
    assert request_body["content"]["application/json"]["schema"]["properties"] == {"name": {"type": "string"}}


def test_undecodable_request_body_is_skipped():
    spec = records_to_openapi(records=[_record(method="POST", body=b"\xff\xfe")])
    assert "requestBody" not in spec["paths"]["/users"]["post"]
