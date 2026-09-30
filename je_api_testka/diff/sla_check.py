"""
Response-time SLA assertions.

These do not load-test the endpoint - they only assert that a single response
record meets a target. Multiple records can be batched via :func:`assert_sla`,
which checks the shared test record when no records are given.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Sequence, Union

from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_TIMEOUT_MS: float = 5000.0
SECONDS_TO_MS: int = 1000
# A numeric ``elapsed`` below this is taken as seconds, otherwise as milliseconds.
ELAPSED_SECONDS_LIMIT: float = 1000.0


@dataclass
class ResponseSLA:
    """Per-endpoint timing target."""

    max_ms: float = DEFAULT_TIMEOUT_MS
    p95_ms: float = DEFAULT_TIMEOUT_MS


def _record_ms(record: dict) -> float:
    elapsed = record.get("elapsed")
    if isinstance(elapsed, (int, float)):
        return float(elapsed) * SECONDS_TO_MS if elapsed < ELAPSED_SECONDS_LIMIT else float(elapsed)
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


def assert_sla(records: Optional[Iterable[dict]] = None,
               sla: Union[ResponseSLA, Mapping[str, float], None] = None) -> None:
    """
    Raise :class:`APIAssertException` if records breach ``sla``.

    ``records`` defaults to the successes in the shared test record. ``sla`` may be a
    :class:`ResponseSLA` or a mapping with ``max_ms`` / ``p95_ms`` (the JSON action form);
    ``None`` uses the defaults.
    """
    apitestka_logger.info(f"sla_check assert_sla sla: {sla}")
    if not isinstance(sla, ResponseSLA):
        sla = ResponseSLA(**(sla or {}))
    if records is None:
        records = list(test_record_instance.test_record_list)
    timings = [_record_ms(record) for record in records]
    if not timings:
        return
    worst = max(timings)
    p95 = _percentile(timings, percentile=95)
    if worst > sla.max_ms:
        raise APIAssertException(f"max latency {worst:.1f}ms exceeded SLA {sla.max_ms}ms")
    if p95 > sla.p95_ms:
        raise APIAssertException(f"p95 latency {p95:.1f}ms exceeded SLA {sla.p95_ms}ms")
