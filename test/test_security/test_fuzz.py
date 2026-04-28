"""Tests for fuzz helpers."""
from __future__ import annotations

from je_api_testka.security.fuzz import fuzz_string_inputs, fuzz_value_pool


def test_fuzz_string_inputs_returns_independent_copy():
    a = fuzz_string_inputs(limit=3)
    b = fuzz_string_inputs(limit=3)
    a.append("mutated")
    assert "mutated" not in b


def test_fuzz_string_inputs_respects_limit():
    assert len(fuzz_string_inputs(limit=2)) == 2
    assert fuzz_string_inputs(limit=0) == []


def test_fuzz_value_pool_iterates_over_fields():
    template = {"name": "alice", "age": 30}
    pool = list(fuzz_value_pool(template, ["name"]))
    assert pool, "expected at least one mutation"
    assert all("age" in entry for entry in pool)
    assert any(entry["name"] == "" for entry in pool)
