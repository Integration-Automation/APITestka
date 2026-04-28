"""
Passive security-header scan over a response.

Returns a list of findings (severity + message) describing missing or weak
hardening headers. Inspired by OWASP Secure Headers Project recommendations.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

SEVERITY_HIGH: str = "high"
SEVERITY_MEDIUM: str = "medium"
SEVERITY_LOW: str = "low"


@dataclass
class HeaderFinding:
    """One actionable result from :func:`scan_security_headers`."""

    header: str
    severity: str
    message: str


REQUIRED_HEADERS = {
    "Strict-Transport-Security": SEVERITY_HIGH,
    "Content-Security-Policy": SEVERITY_HIGH,
    "X-Content-Type-Options": SEVERITY_MEDIUM,
    "X-Frame-Options": SEVERITY_MEDIUM,
    "Referrer-Policy": SEVERITY_LOW,
    "Permissions-Policy": SEVERITY_LOW,
}


def _normalize(headers: Mapping[str, str]) -> dict:
    return {key.lower(): value for key, value in headers.items()}


def scan_security_headers(headers: Mapping[str, str]) -> List[HeaderFinding]:
    """Return a list of :class:`HeaderFinding` describing problems with ``headers``."""
    apitestka_logger.info("header_scan scan_security_headers")
    findings: List[HeaderFinding] = []
    normalised = _normalize(headers)

    for header, severity in REQUIRED_HEADERS.items():
        if header.lower() not in normalised:
            findings.append(HeaderFinding(
                header=header,
                severity=severity,
                message=f"missing recommended header {header}",
            ))

    nosniff = normalised.get("x-content-type-options", "").lower()
    if nosniff and nosniff != "nosniff":
        findings.append(HeaderFinding(
            header="X-Content-Type-Options",
            severity=SEVERITY_MEDIUM,
            message=f"X-Content-Type-Options should be 'nosniff', got '{nosniff}'",
        ))

    server_banner = normalised.get("server")
    if server_banner and any(char.isdigit() for char in server_banner):
        findings.append(HeaderFinding(
            header="Server",
            severity=SEVERITY_LOW,
            message=f"Server header leaks version info: '{server_banner}'",
        ))
    return findings
