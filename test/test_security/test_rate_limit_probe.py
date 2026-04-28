"""Tests for the rate-limit probe."""
from __future__ import annotations

import httpx

from je_api_testka.security.rate_limit_probe import probe_rate_limit


def test_triggers_when_server_returns_429():
    counter = {"calls": 0}

    def _handler(_request):
        counter["calls"] += 1
        if counter["calls"] >= 3:
            return httpx.Response(429, headers={"Retry-After": "30"})
        return httpx.Response(200)

    transport = httpx.MockTransport(_handler)
    result = probe_rate_limit("https://x.invalid", burst=10, transport=transport)
    assert result.triggered is True
    assert result.triggered_at_attempt == 3
    assert result.retry_after == "30"


def test_no_trigger_returns_false():
    transport = httpx.MockTransport(lambda _r: httpx.Response(200))
    result = probe_rate_limit("https://x.invalid", burst=3, transport=transport)
    assert result.triggered is False
    assert result.triggered_at_attempt is None


def test_zero_burst_short_circuits():
    result = probe_rate_limit("https://x.invalid", burst=0)
    assert result.triggered is False
