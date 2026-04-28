"""
CORS preflight validation.

Sends an OPTIONS request with ``Origin`` and ``Access-Control-Request-Method``
headers and inspects the response for proper CORS headers. Returns a list of
:class:`HeaderFinding` describing problems.
"""
from __future__ import annotations

from typing import List

import httpx

from je_api_testka.security.header_scan import HeaderFinding, SEVERITY_HIGH, SEVERITY_MEDIUM
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_CORS_TIMEOUT_SECONDS: float = 10.0


def cors_preflight(
    url: str,
    origin: str,
    method: str = "GET",
    timeout: float = DEFAULT_CORS_TIMEOUT_SECONDS,
    transport: object = None,
) -> List[HeaderFinding]:
    """Issue a preflight OPTIONS request and return findings."""
    apitestka_logger.info(f"cors_check cors_preflight url: {url} origin: {origin}")
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": method.upper(),
    }
    client_kwargs = {"timeout": timeout}
    if transport is not None:
        client_kwargs["transport"] = transport
    with httpx.Client(**client_kwargs) as client:
        response = client.options(url, headers=headers)
    findings: List[HeaderFinding] = []
    allow_origin = response.headers.get("access-control-allow-origin")
    if allow_origin is None:
        findings.append(HeaderFinding(
            header="Access-Control-Allow-Origin",
            severity=SEVERITY_HIGH,
            message="missing Access-Control-Allow-Origin in preflight response",
        ))
    elif allow_origin == "*" and response.headers.get("access-control-allow-credentials", "").lower() == "true":
        findings.append(HeaderFinding(
            header="Access-Control-Allow-Origin",
            severity=SEVERITY_HIGH,
            message="wildcard origin combined with credentials is invalid",
        ))
    allow_methods = response.headers.get("access-control-allow-methods", "")
    if method.upper() not in [piece.strip().upper() for piece in allow_methods.split(",")]:
        findings.append(HeaderFinding(
            header="Access-Control-Allow-Methods",
            severity=SEVERITY_MEDIUM,
            message=f"method {method.upper()} not advertised in Allow-Methods",
        ))
    return findings
