"""Tests for the SQLite trend store."""
from __future__ import annotations

from je_api_testka.utils.generate_report.trend_store import (
    list_trend_rows,
    record_current_run,
)
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_record_then_list(tmp_path):
    db_path = str(tmp_path / "trend.sqlite")
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({
        "request_url": "https://x.invalid", "request_time_sec": 0.5,
    })
    record_current_run(db_path)
    record_current_run(db_path)
    rows = list_trend_rows(db_path)
    assert len(rows) == 2
    assert rows[0].success_count == 1
    test_record_instance.clean_record()


def test_list_empty_when_db_missing(tmp_path):
    db_path = str(tmp_path / "missing.sqlite")
    assert list_trend_rows(db_path) == []
