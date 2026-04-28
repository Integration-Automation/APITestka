"""Tests for CSV / JSON data iterators."""
from __future__ import annotations

import json

import pytest

from je_api_testka.data.iter_data_rows import collect_rows, iter_csv_rows, iter_json_rows


def test_iter_csv_rows(tmp_path):
    csv_path = tmp_path / "data.csv"
    csv_path.write_text("name,age\nalice,30\nbob,25\n", encoding="utf-8")
    rows = collect_rows(iter_csv_rows(str(csv_path)))
    assert rows == [{"name": "alice", "age": "30"}, {"name": "bob", "age": "25"}]


def test_iter_json_rows_list(tmp_path):
    target = tmp_path / "data.json"
    target.write_text(json.dumps([{"a": 1}, {"a": 2}]), encoding="utf-8")
    rows = collect_rows(iter_json_rows(str(target)))
    assert rows == [{"a": 1}, {"a": 2}]


def test_iter_json_rows_object(tmp_path):
    target = tmp_path / "data.json"
    target.write_text(json.dumps({"a": 1}), encoding="utf-8")
    rows = collect_rows(iter_json_rows(str(target)))
    assert rows == [{"a": 1}]


def test_iter_json_rows_unsupported_type(tmp_path):
    target = tmp_path / "data.json"
    target.write_text(json.dumps(42), encoding="utf-8")
    with pytest.raises(TypeError):
        collect_rows(iter_json_rows(str(target)))
