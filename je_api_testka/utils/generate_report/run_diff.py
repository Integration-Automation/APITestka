"""
Compare two saved JSON report files (success/failure dicts) and report which
test went from green to red, or vice versa, between runs.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class RunDiffResult:
    """Differences between two prior runs."""

    new_failures: List[str] = field(default_factory=list)
    new_passes: List[str] = field(default_factory=list)
    still_failing: List[str] = field(default_factory=list)
    still_passing: List[str] = field(default_factory=list)


def _load(file_path: str) -> dict:
    return json.loads(Path(file_path).read_text(encoding="utf-8"))


def diff_runs(previous_failure_json: str, current_failure_json: str) -> RunDiffResult:
    """Compare two ``*_failure.json`` files produced by ``generate_json_report``."""
    previous = _load(previous_failure_json)
    current = _load(current_failure_json)
    prev_keys = {entry.get("test_url", name) for name, entry in previous.items()}
    curr_keys = {entry.get("test_url", name) for name, entry in current.items()}
    new_failures = sorted(curr_keys - prev_keys)
    new_passes = sorted(prev_keys - curr_keys)
    still_failing = sorted(prev_keys & curr_keys)
    return RunDiffResult(
        new_failures=new_failures,
        new_passes=new_passes,
        still_failing=still_failing,
    )
