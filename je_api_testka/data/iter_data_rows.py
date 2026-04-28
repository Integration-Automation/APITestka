"""
Generators that yield row dictionaries from CSV or JSON files for
data-driven test loops.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterator, List


def iter_csv_rows(file_path: str, delimiter: str = ",") -> Iterator[dict]:
    """Yield rows from a CSV file as dictionaries keyed by header."""
    target = Path(file_path)
    with target.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        for row in reader:
            yield row


def iter_json_rows(file_path: str) -> Iterator[dict]:
    """Yield rows from a JSON file. Accepts either a list-of-dicts or a single dict."""
    target = Path(file_path)
    with target.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if isinstance(data, list):
        for row in data:
            yield row
    elif isinstance(data, dict):
        yield data
    else:
        raise TypeError(f"unsupported JSON root type: {type(data).__name__}")


def collect_rows(rows: Iterator[dict]) -> List[dict]:
    """Materialise an iterator into a list (helper for tests)."""
    return list(rows)
