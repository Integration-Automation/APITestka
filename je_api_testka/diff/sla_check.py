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


def _number(value: object) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except ValueError:
        return None


def record_latency_ms(record: Mapping[str, object]) -> Optional[float]:
    """
    Return a record's response time in milliseconds, or ``None`` when it has none.

    A numeric ``elapsed`` is read as seconds below 1000 and as milliseconds from there;
    otherwise ``request_time_sec`` is used. Numbers stored as text (saved JSON reports) count.
    """
    elapsed = _number(record.get("elapsed"))
    if elapsed is not None:
        return elapsed * SECONDS_TO_MS if elapsed < ELAPSED_SECONDS_LIMIT else elapsed
    seconds = _number(record.get("request_time_sec"))
    return None if seconds is None else seconds * SECONDS_TO_MS


def _record_ms(record: dict) -> float:
    latency = record_latency_ms(record)
    return 0.0 if latency is None else latency


def percentile(values: Sequence[float], pct: float) -> float:
    """Return the nearest-rank ``pct`` percentile (0-100) of ``values``; 0.0 for no values."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(int(round(pct / 100 * len(ordered))) - 1, 0)
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
    p95 = percentile(timings, 95)
    if worst > sla.max_ms:
        raise APIAssertException(f"max latency {worst:.1f}ms exceeded SLA {sla.max_ms}ms")
    if p95 > sla.p95_ms:
        raise APIAssertException(f"p95 latency {p95:.1f}ms exceeded SLA {sla.p95_ms}ms")
