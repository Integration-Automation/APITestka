"""
Persist per-run summary stats into a SQLite database for trend analysis.
"""
from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_TREND_DB: str = "apitestka_trend.sqlite"
SCHEMA_SQL: str = """
CREATE TABLE IF NOT EXISTS trend_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    captured_at TEXT NOT NULL,
    success_count INTEGER NOT NULL,
    failure_count INTEGER NOT NULL,
    avg_elapsed REAL NOT NULL
);
"""


@dataclass
class TrendRow:
    """One previously-captured run summary."""

    captured_at: str
    success_count: int
    failure_count: int
    avg_elapsed: float


def _avg_elapsed() -> float:
    timings = []
    for record in test_record_instance.test_record_list:
        elapsed = record.get("request_time_sec")
        if isinstance(elapsed, (int, float)):
            timings.append(float(elapsed))
    if not timings:
        return 0.0
    return sum(timings) / len(timings)


def record_current_run(db_path: str = DEFAULT_TREND_DB) -> Path:
    """Append the current global test record's summary into the trend DB."""
    target = Path(db_path)
    # closing() releases the file; the inner "with connection" only commits.
    with closing(sqlite3.connect(target)) as connection, connection:
        connection.execute(SCHEMA_SQL)
        connection.execute(
            "INSERT INTO trend_runs (captured_at, success_count, failure_count, avg_elapsed)"
            " VALUES (?, ?, ?, ?)",
            (
                datetime.now(timezone.utc).isoformat(),
                len(test_record_instance.test_record_list),
                len(test_record_instance.error_record_list),
                _avg_elapsed(),
            ),
        )
    return target


def list_trend_rows(db_path: str = DEFAULT_TREND_DB, limit: int = 50) -> List[TrendRow]:
    """Return the latest ``limit`` run summaries, newest first (empty when the database does not exist)."""
    target = Path(db_path)
    if not target.exists():
        return []
    with closing(sqlite3.connect(target)) as connection:
        connection.execute(SCHEMA_SQL)
        cursor = connection.execute(
            "SELECT captured_at, success_count, failure_count, avg_elapsed"
            " FROM trend_runs ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        return [TrendRow(*row) for row in cursor.fetchall()]
