"""Tests for response-time SLA assertions."""
from __future__ import annotations

import pytest

from je_api_testka.diff.sla_check import ResponseSLA, assert_sla
from je_api_testka.utils.exception.exceptions import APIAssertException
from je_api_testka.utils.executor.action_executor import execute_action
from je_api_testka.utils.test_record.test_record_class import test_record_instance


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


def test_assert_sla_accepts_json_mapping():
    # Regression: JSON actions can only pass a dict, which used to fail on sla.max_ms.
    with pytest.raises(APIAssertException):
        assert_sla([{"request_time_sec": 1.0}], {"max_ms": 500, "p95_ms": 2000})


def test_assert_sla_defaults_to_the_shared_record():
    test_record_instance.test_record_list.append({"request_time_sec": 1.0})
    with pytest.raises(APIAssertException):
        assert_sla(sla={"max_ms": 500})


def test_assert_sla_via_executor_checks_recorded_run():
    test_record_instance.test_record_list.append({"request_time_sec": 1.0})
    record = execute_action([["AT_assert_sla", {"sla": {"max_ms": 500}}]])
    assert "APIAssertException" in next(iter(record.values()))
