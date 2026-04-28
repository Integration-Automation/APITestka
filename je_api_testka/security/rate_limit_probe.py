"""
Rate-limit probe.

Sends a small, bounded burst of requests (default 20) at a low concurrency and
reports the first attempt at which the server responds with HTTP 429 plus any
``Retry-After`` value. This is *not* a load test - it is a rate-limit detector.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import httpx

from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_PROBE_BURST: int = 20
DEFAULT_PROBE_TIMEOUT_SECONDS: float = 10.0
HTTP_TOO_MANY_REQUESTS: int = 429


@dataclass
class RateLimitProbe:
    """Outcome of :func:`probe_rate_limit`."""

    triggered: bool
    triggered_at_attempt: Optional[int]
    retry_after: Optional[str]


def probe_rate_limit(
    url: str,
    method: str = "GET",
    burst: int = DEFAULT_PROBE_BURST,
    timeout: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
    transport: object = None,
) -> RateLimitProbe:
    """Send up to ``burst`` requests sequentially; return as soon as a 429 is seen."""
    apitestka_logger.info(f"rate_limit_probe probe_rate_limit url: {url} burst: {burst}")
    if burst < 1:
        return RateLimitProbe(triggered=False, triggered_at_attempt=None, retry_after=None)
    client_kwargs = {"timeout": timeout}
    if transport is not None:
        client_kwargs["transport"] = transport
    with httpx.Client(**client_kwargs) as client:
        for attempt in range(1, burst + 1):
            response = client.request(method.upper(), url)
            if response.status_code == HTTP_TOO_MANY_REQUESTS:
                return RateLimitProbe(
                    triggered=True,
                    triggered_at_attempt=attempt,
                    retry_after=response.headers.get("retry-after"),
                )
    return RateLimitProbe(triggered=False, triggered_at_attempt=None, retry_after=None)
