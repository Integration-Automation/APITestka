"""Tests for the FaultInjector."""
from __future__ import annotations

import time

import pytest
from flask import Response

from je_api_testka.utils.mock_server.fault_injection import FaultInjector


def _make_view(label: str = "ok"):
    def _view():
        return Response(label, status=200)

    return _view


def test_invalid_probability_rejected():
    with pytest.raises(ValueError):
        FaultInjector(failure_probability=1.5)


def test_no_faults_passes_through():
    injector = FaultInjector()
    wrapped = injector.wrap(_make_view("hi"))
    response = wrapped()
    assert response.status_code == 200
    assert response.data == b"hi"


def test_certain_failure_returns_configured_status():
    injector = FaultInjector(failure_probability=1.0, failure_status=503, failure_body="nope")
    wrapped = injector.wrap(_make_view())
    response = wrapped()
    assert response.status_code == 503
    assert response.data == b"nope"


def test_latency_is_applied():
    injector = FaultInjector(latency_seconds=0.05)
    wrapped = injector.wrap(_make_view())
    start = time.monotonic()
    wrapped()
    assert time.monotonic() - start >= 0.04


def test_configure_clamps_negative_latency():
    injector = FaultInjector()
    injector.configure(latency_seconds=-1)
    assert injector.latency_seconds == pytest.approx(0.0)
