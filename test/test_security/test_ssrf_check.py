"""Tests for the SSRF probe."""
from __future__ import annotations

import httpx

from je_api_testka.security.ssrf_check import probe_ssrf


def test_records_probes_with_2xx_response():
    captured = []

    def _handler(request):
        captured.append(request)
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(_handler)
    findings = probe_ssrf("http://app.invalid/fetch", transport=transport,
                          probes=["http://127.0.0.1"])
    assert len(findings) == 1
    assert findings[0].probe == "http://127.0.0.1"


def test_skips_probes_that_return_4xx():
    transport = httpx.MockTransport(lambda _r: httpx.Response(400))
    findings = probe_ssrf("http://app.invalid/fetch", transport=transport,
                          probes=["http://127.0.0.1"])
    assert findings == []


def test_default_probe_list_used_when_none_supplied():
    transport = httpx.MockTransport(lambda _r: httpx.Response(403))
    findings = probe_ssrf("http://app.invalid/fetch", transport=transport)
    # All 403 -> no findings, but the function should not raise
    assert findings == []
