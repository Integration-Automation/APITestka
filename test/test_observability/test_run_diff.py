"""Tests for diff_runs."""
from __future__ import annotations

import json

from je_api_testka.utils.generate_report.run_diff import diff_runs


def _write_failures(path, urls):
    payload = {f"Failure_Test{index}": {"test_url": url} for index, url in enumerate(urls, start=1)}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_new_failures_and_recoveries(tmp_path):
    prev = tmp_path / "prev_failure.json"
    curr = tmp_path / "curr_failure.json"
    _write_failures(prev, ["https://a.invalid", "https://b.invalid"])
    _write_failures(curr, ["https://b.invalid", "https://c.invalid"])
    diff = diff_runs(str(prev), str(curr))
    assert diff.new_failures == ["https://c.invalid"]
    assert diff.new_passes == ["https://a.invalid"]
    assert diff.still_failing == ["https://b.invalid"]
