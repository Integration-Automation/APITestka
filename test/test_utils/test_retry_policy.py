"""Tests for the retry helper."""
from __future__ import annotations

import pytest

from je_api_testka.utils.retry import RetryPolicy, retry_call


def test_retry_call_succeeds_eventually():
    counter = {"calls": 0}

    def _flaky():
        counter["calls"] += 1
        if counter["calls"] < 3:
            raise RuntimeError("not yet")
        return "ok"

    policy = RetryPolicy(max_attempts=5, initial_delay_seconds=0, jitter=False)
    assert retry_call(_flaky, policy=policy) == "ok"
    assert counter["calls"] == 3


def test_retry_call_raises_after_exhaustion():
    def _always_fail():
        raise ValueError("boom")

    policy = RetryPolicy(max_attempts=2, initial_delay_seconds=0, jitter=False)
    with pytest.raises(ValueError):
        retry_call(_always_fail, policy=policy)


def test_retry_call_does_not_swallow_unrelated_exception():
    def _typeerror():
        raise TypeError("wrong type")

    policy = RetryPolicy(
        max_attempts=3, initial_delay_seconds=0, jitter=False, retry_on=(ValueError,)
    )
    with pytest.raises(TypeError):
        retry_call(_typeerror, policy=policy)


def test_compute_delay_caps_at_max():
    policy = RetryPolicy(
        initial_delay_seconds=10,
        backoff_factor=10,
        max_delay_seconds=5,
        jitter=False,
    )
    assert policy.compute_delay(5) == 5
