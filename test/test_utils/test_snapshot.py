"""Tests for the snapshot helper."""
from __future__ import annotations

import pytest

from je_api_testka.utils.assert_result.snapshot import _strip_keys, assert_snapshot
from je_api_testka.utils.exception.exceptions import APIAssertException


def test_first_call_writes_snapshot(tmp_path):
    payload = {"name": "alice", "age": 30}
    assert_snapshot("user", payload, snapshot_dir=str(tmp_path))
    assert (tmp_path / "user.json").exists()


def test_matching_payload_passes(tmp_path):
    payload = {"name": "alice"}
    assert_snapshot("user", payload, snapshot_dir=str(tmp_path))
    assert_snapshot("user", payload, snapshot_dir=str(tmp_path))


def test_mismatch_raises(tmp_path):
    assert_snapshot("user", {"name": "alice"}, snapshot_dir=str(tmp_path))
    with pytest.raises(APIAssertException):
        assert_snapshot("user", {"name": "bob"}, snapshot_dir=str(tmp_path))


def test_ignore_keys(tmp_path):
    assert_snapshot(
        "rec", {"id": 1, "ts": "2026-01-01"}, snapshot_dir=str(tmp_path), ignore_keys=["ts"]
    )
    assert_snapshot(
        "rec", {"id": 1, "ts": "2026-12-31"}, snapshot_dir=str(tmp_path), ignore_keys=["ts"]
    )


def test_strip_keys_recursive():
    payload = {"a": 1, "b": {"a": 2, "c": 3}, "list": [{"a": 4}]}
    assert _strip_keys(payload, ["a"]) == {"b": {"c": 3}, "list": [{}]}
