"""
SSRF probe.

Submits a list of suspicious URLs (loopback, link-local, cloud metadata) to a
target endpoint and reports which ones produced a non-error response. The
caller chooses the parameter name and HTTP method.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import httpx

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_SSRF_TIMEOUT_SECONDS: float = 5.0

# These URLs are SSRF *probe targets*: we send them at a victim endpoint to
# detect whether it follows them. Loopback / link-local / cloud-metadata IPs
# are the canonical probe set, so http and the hardcoded 169.254.169.254
# (AWS IMDS) address are intentional. Sonar S5332/S1313 are suppressed below.
SSRF_PROBES = (
    "http://127.0.0.1",  # NOSONAR S5332 - loopback probe
    "http://localhost",  # NOSONAR S5332 - loopback probe
    "http://0.0.0.0",  # NOSONAR S5332 - loopback probe
    "http://169.254.169.254/latest/meta-data/",  # NOSONAR S1313 S5332 - AWS IMDS probe
    "http://metadata.google.internal/",  # NOSONAR S5332 - GCP metadata probe
    "file:///etc/passwd",
)


@dataclass
class SSRFFinding:
    """Single suspicious URL that produced a non-error response."""

    probe: str
    status: int


def probe_ssrf(
    target: str,
    parameter: str = "url",
    method: str = "POST",
    timeout: float = DEFAULT_SSRF_TIMEOUT_SECONDS,
    transport: object = None,
    probes: Optional[List[str]] = None,
) -> List[SSRFFinding]:
    """Submit each probe URL into ``parameter`` and report responses below 400."""
    apitestka_logger.info(f"ssrf_check probe_ssrf target: {target} parameter: {parameter}")
    findings: List[SSRFFinding] = []
    pool = list(probes or SSRF_PROBES)
    client_kwargs = {"timeout": timeout}
    if transport is not None:
        client_kwargs["transport"] = transport
    with httpx.Client(**client_kwargs) as client:
        for probe in pool:
            payload = {parameter: probe}
            response = client.request(method.upper(), target, json=payload)
            if response.status_code < 400:
                findings.append(SSRFFinding(probe=probe, status=response.status_code))
    return findings
