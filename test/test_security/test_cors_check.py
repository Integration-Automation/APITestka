"""Tests for CORS preflight checks."""
from __future__ import annotations

import httpx

from je_api_testka.security.cors_check import cors_preflight


def _transport(headers: dict):
    def _handler(_request):
        return httpx.Response(204, headers=headers)
    return httpx.MockTransport(_handler)


def test_missing_allow_origin_flagged():
    findings = cors_preflight("https://x.invalid", origin="https://app.invalid",
                              transport=_transport({}))
    assert any(f.header == "Access-Control-Allow-Origin" for f in findings)


def test_wildcard_with_credentials_flagged():
    findings = cors_preflight(
        "https://x.invalid", origin="https://app.invalid",
        transport=_transport({
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET",
        }),
    )
    assert any("wildcard" in f.message.lower() for f in findings)


def test_method_not_advertised_flagged():
    findings = cors_preflight(
        "https://x.invalid", origin="https://app.invalid", method="DELETE",
        transport=_transport({
            "Access-Control-Allow-Origin": "https://app.invalid",
            "Access-Control-Allow-Methods": "GET, POST",
        }),
    )
    assert any(f.header == "Access-Control-Allow-Methods" for f in findings)


def test_well_configured_returns_no_findings():
    findings = cors_preflight(
        "https://x.invalid", origin="https://app.invalid", method="GET",
        transport=_transport({
            "Access-Control-Allow-Origin": "https://app.invalid",
            "Access-Control-Allow-Methods": "GET, POST",
        }),
    )
    assert findings == []
