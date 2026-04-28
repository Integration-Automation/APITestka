"""
Lightweight failure classifier.

We keep this rule-based by default so it works without an LLM. Categories:

* ``network``: ``ConnectError`` / ``Timeout`` / DNS issues.
* ``auth``: 401 / 403 / "unauthorized" / "forbidden" in the message.
* ``validation``: 400 / 422 / "invalid" / schema mismatches.
* ``server``: 5xx.
* ``other``: anything that did not match.
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable, List

CATEGORY_NETWORK: str = "network"
CATEGORY_AUTH: str = "auth"
CATEGORY_VALIDATION: str = "validation"
CATEGORY_SERVER: str = "server"
CATEGORY_OTHER: str = "other"


def _classify_one(error_text: str) -> str:
    haystack = error_text.lower()
    if any(token in haystack for token in ("connecterror", "timeout", "dns", "name resolution")):
        return CATEGORY_NETWORK
    if "401" in haystack or "unauthorized" in haystack or "forbidden" in haystack or "403" in haystack:
        return CATEGORY_AUTH
    if "400" in haystack or "422" in haystack or "invalid" in haystack or "schema" in haystack:
        return CATEGORY_VALIDATION
    if any(code in haystack for code in ("500", "502", "503", "504")) or "internal server" in haystack:
        return CATEGORY_SERVER
    return CATEGORY_OTHER


def classify_failures(error_records: Iterable[list]) -> Counter:
    """Bucket each error record into one of the categories above; return a counter."""
    counter: Counter = Counter()
    for entry in error_records:
        message = entry[1] if len(entry) > 1 else ""
        counter[_classify_one(str(message))] += 1
    return counter
