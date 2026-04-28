"""Tests for response-time SLA assertions."""
from __future__ import annotations

import pytest

from je_api_testka.diff.sla_check import ResponseSLA, assert_sla
from je_api_testka.utils.exception.exceptions import APIAssertException


def test_assert_sla_passes_under_thresholds():
    records = [{"request_time_sec": 0.05}, {"request_time_sec": 0.1}]
    assert_sla(records, ResponseSLA(max_ms=500, p95_ms=500))


def test_assert_sla_breaches_max():
    records = [{"request_time_sec": 0.05}, {"request_time_sec": 1.0}]
    with pytest.raises(APIAssertException):
        assert_sla(records, ResponseSLA(max_ms=500, p95_ms=2000))


def test_assert_sla_breaches_p95():
    records = [{"request_time_sec": 0.1}] * 9 + [{"request_time_sec": 0.6}]
    with pytest.raises(APIAssertException):
        assert_sla(records, ResponseSLA(max_ms=2000, p95_ms=200))


def test_assert_sla_no_records_no_op():
    assert_sla([], ResponseSLA())


def test_diff_payloads_via_executor():
    from je_api_testka.utils.executor.action_executor import execute_action

    record = execute_action([
        ["AT_diff_payloads", {"left": {"a": 1}, "right": {"a": 2}}],
    ])
    diff_value = next(iter(record.values()))
    assert diff_value.changed == {"a": (1, 2)}
