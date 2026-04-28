"""Tests for the security header scanner."""
from __future__ import annotations

from je_api_testka.security.header_scan import (
    SEVERITY_HIGH,
    SEVERITY_LOW,
    SEVERITY_MEDIUM,
    scan_security_headers,
)


def test_empty_headers_yield_findings_for_each_required_header():
    findings = scan_security_headers({})
    headers = {finding.header for finding in findings}
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers
    severities = {finding.severity for finding in findings}
    assert severities <= {SEVERITY_HIGH, SEVERITY_MEDIUM, SEVERITY_LOW}


def test_full_hardening_yields_no_findings():
    headers = {
        "Strict-Transport-Security": "max-age=31536000",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "geolocation=()",
    }
    assert scan_security_headers(headers) == []


def test_misconfigured_nosniff_flagged():
    headers = {
        "Strict-Transport-Security": "max-age=1",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "garbage",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "geolocation=()",
    }
    findings = scan_security_headers(headers)
    assert any("nosniff" in finding.message for finding in findings)


def test_server_banner_with_version_flagged():
    headers = {
        "Strict-Transport-Security": "max-age=1",
        "Content-Security-Policy": "default-src 'self'",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "no-referrer",
        "Permissions-Policy": "geolocation=()",
        "Server": "nginx/1.25.3",
    }
    findings = scan_security_headers(headers)
    assert any(finding.header == "Server" for finding in findings)
