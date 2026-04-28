"""Tests for dependency-aware ordering."""
from __future__ import annotations

import pytest

from je_api_testka.runner.dependency_runner import order_actions
from je_api_testka.utils.exception.exceptions import APITesterExecuteException


def test_order_respects_dependencies():
    actions = [
        ["AT_b", {"id": "b", "depends_on": ["a"]}],
        ["AT_a", {"id": "a"}],
    ]
    ordered = order_actions(actions)
    assert ordered[0][1]["id"] == "a"
    assert ordered[1][1]["id"] == "b"


def test_order_handles_missing_deps_gracefully():
    actions = [
        ["AT_a", {"id": "a", "depends_on": ["ghost"]}],
    ]
    ordered = order_actions(actions)
    assert ordered == actions


def test_cycle_raises():
    actions = [
        ["AT_a", {"id": "a", "depends_on": ["b"]}],
        ["AT_b", {"id": "b", "depends_on": ["a"]}],
    ]
    with pytest.raises(APITesterExecuteException):
        order_actions(actions)
