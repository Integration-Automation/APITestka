"""Tests for the rule-based failure classifier."""
from __future__ import annotations

from je_api_testka.ai.failure_classifier import (
    CATEGORY_AUTH,
    CATEGORY_NETWORK,
    CATEGORY_OTHER,
    CATEGORY_SERVER,
    CATEGORY_VALIDATION,
    classify_failures,
)


def test_classifies_each_category():
    records = [
        [{"test_url": "x"}, "ConnectError on attempt"],
        [{"test_url": "x"}, "401 Unauthorized"],
        [{"test_url": "x"}, "422 Unprocessable Entity: invalid field"],
        [{"test_url": "x"}, "500 Internal Server Error"],
        [{"test_url": "x"}, "weird boom"],
    ]
    counts = classify_failures(records)
    assert counts[CATEGORY_NETWORK] == 1
    assert counts[CATEGORY_AUTH] == 1
    assert counts[CATEGORY_VALIDATION] == 1
    assert counts[CATEGORY_SERVER] == 1
    assert counts[CATEGORY_OTHER] == 1


def test_empty_input_yields_empty_counter():
    assert classify_failures([]) == {}
