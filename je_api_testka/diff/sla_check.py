"""
Response-time SLA assertions.

These do not load-test the endpoint - they only assert that a single response
record meets a target. Multiple records can be batched via :func:`assert_sla`.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_TIMEOUT_MS: float = 5000.0
SECONDS_TO_MS: int = 1000


@dataclass
class ResponseSLA:
    """Per-endpoint timing target."""

    max_ms: float = DEFAULT_TIMEOUT_MS
    p95_ms: float = DEFAULT_TIMEOUT_MS


def _record_ms(record: dict) -> float:
    elapsed = record.get("elapsed")
    if isinstance(elapsed, (int, float)):
        return float(elapsed) * SECONDS_TO_MS if elapsed < 1000 else float(elapsed)
    seconds = record.get("request_time_sec")
    if isinstance(seconds, (int, float)):
        return float(seconds) * SECONDS_TO_MS
    return 0.0


def _percentile(values: Sequence[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(int(round(percentile / 100 * len(ordered))) - 1, 0)
    return ordered[min(rank, len(ordered) - 1)]


def assert_sla(records: Iterable[dict], sla: ResponseSLA) -> None:
    """Raise :class:`APIAssertException` if records breach ``sla``."""
    apitestka_logger.info(f"sla_check assert_sla sla: {sla}")
    timings = [_record_ms(record) for record in records]
    if not timings:
        return
    worst = max(timings)
    p95 = _percentile(timings, percentile=95)
    if worst > sla.max_ms:
        raise APIAssertException(f"max latency {worst:.1f}ms exceeded SLA {sla.max_ms}ms")
    if p95 > sla.p95_ms:
        raise APIAssertException(f"p95 latency {p95:.1f}ms exceeded SLA {sla.p95_ms}ms")
