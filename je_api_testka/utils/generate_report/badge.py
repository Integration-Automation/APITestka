"""
Generate a shields.io-compatible JSON badge from the global test record.

Drop the resulting file into a public bucket / Pages site and reference via
``https://img.shields.io/endpoint?url=...`` in your README.
"""
from __future__ import annotations

import json
from pathlib import Path

from je_api_testka.utils.test_record.test_record_class import test_record_instance

DEFAULT_BADGE_FILENAME: str = "apitestka_badge.json"
COLOR_GREEN: str = "brightgreen"
COLOR_YELLOW: str = "yellow"
COLOR_RED: str = "red"
SCHEMA_VERSION: int = 1


def render_badge(label: str = "tests") -> dict:
    """Return a shields.io endpoint dict describing the latest run."""
    success = len(test_record_instance.test_record_list)
    failure = len(test_record_instance.error_record_list)
    total = success + failure
    if total == 0:
        message = "no data"
        color = COLOR_YELLOW
    elif failure == 0:
        message = f"{success} passing"
        color = COLOR_GREEN
    else:
        message = f"{success}/{total} passing"
        color = COLOR_RED
    return {
        "schemaVersion": SCHEMA_VERSION,
        "label": label,
        "message": message,
        "color": color,
    }


def generate_badge(file_name: str = DEFAULT_BADGE_FILENAME, label: str = "tests") -> Path:
    target = Path(file_name)
    target.write_text(json.dumps(render_badge(label), indent=2), encoding="utf-8")
    return target
