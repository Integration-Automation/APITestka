"""Tests for the structural payload diff."""
from __future__ import annotations

from je_api_testka.diff.response_diff import diff_payloads


def test_identical_payloads_yield_empty_diff():
    result = diff_payloads({"a": 1}, {"a": 1})
    assert result.is_empty


def test_added_and_removed_keys():
    result = diff_payloads({"a": 1, "b": 2}, {"a": 1, "c": 3})
    assert "c" in result.added
    assert "b" in result.removed


def test_changed_value():
    result = diff_payloads({"a": 1}, {"a": 2})
    assert result.changed == {"a": (1, 2)}


def test_nested_diff_uses_dotted_paths():
    result = diff_payloads(
        {"user": {"name": "alice", "age": 30}},
        {"user": {"name": "alice", "age": 31}},
    )
    assert result.changed == {"user.age": (30, 31)}


def test_list_diff_uses_index_notation():
    result = diff_payloads([1, 2, 3], [1, 2])
    assert "[2]" in result.removed


def test_ignore_paths_skip_subtree():
    result = diff_payloads(
        {"ts": "2026-01-01", "id": 1},
        {"ts": "2026-12-31", "id": 1},
        ignore_paths=["ts"],
    )
    assert result.is_empty
