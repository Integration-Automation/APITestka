"""Tests for the test_record -> OpenAPI inferer."""
from __future__ import annotations

from je_api_testka.spec.records_to_openapi import records_to_openapi


def test_groups_by_path_and_method():
    records = [
        {
            "request_url": "http://x.invalid/users",
            "request_method": "GET",
            "status_code": 200,
            "text": '{"id": 1}',
        },
        {
            "request_url": "http://x.invalid/users",
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
        "request_url": "http://x.invalid/health",
        "request_method": "GET",
        "status_code": 200,
        "text": "",
    }]
    spec = records_to_openapi(records=records)
    assert spec["paths"]["/health"]["get"]["responses"]["200"]
