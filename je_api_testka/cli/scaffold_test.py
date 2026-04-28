"""
Scaffold a starter action JSON for a given URL.

Useful for "I have a curl-friendly endpoint, give me a test skeleton". Emits an
action list with a smoke check, a result_check_dict, and SLA placeholders.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List


def scaffold_action_list(url: str, method: str = "GET") -> List[list]:
    """Return a starter action list."""
    return [
        ["AT_test_api_method_requests", {
            "http_method": method.lower(),
            "test_url": url,
            "result_check_dict": {"status_code": 200},
            "tags": ["smoke"],
        }],
        ["AT_assert_sla", {"records": [], "sla": {"max_ms": 2000, "p95_ms": 1500}}],
    ]


def write_scaffold(file_path: str, url: str, method: str = "GET") -> Path:
    """Write the scaffold to ``file_path`` and return the path."""
    target = Path(file_path)
    target.write_text(
        json.dumps(scaffold_action_list(url, method), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return target
