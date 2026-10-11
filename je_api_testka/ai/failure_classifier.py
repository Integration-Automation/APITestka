"""
Lightweight failure classifier.

Rules classify each failure first, so this works without an LLM. Categories:

* ``network``: ``ConnectError`` / ``Timeout`` / DNS issues.
* ``auth``: 401 / 403 / "unauthorized" / "forbidden" in the message.
* ``validation``: 400 / 422 / "invalid" / schema mismatches.
* ``server``: 5xx.
* ``other``: anything that did not match.

When an AI backend other than :class:`NoOpAIBackend` is active, the messages
the rules leave as ``other`` go to it in one request; a reply that is not a
JSON list of known categories, one per message, leaves them as ``other``.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Iterable, List

from je_api_testka.ai.backend import NoOpAIBackend, ai_backend
from je_api_testka.ai.reply import parse_json_reply
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

CATEGORY_NETWORK: str = "network"
CATEGORY_AUTH: str = "auth"
CATEGORY_VALIDATION: str = "validation"
CATEGORY_SERVER: str = "server"
CATEGORY_OTHER: str = "other"
CATEGORIES = (CATEGORY_NETWORK, CATEGORY_AUTH, CATEGORY_VALIDATION, CATEGORY_SERVER, CATEGORY_OTHER)

CLASSIFICATION_PROMPT: str = (
    "Each context entry is the error message of a failed API test request. Label each one with exactly one "
    f"of: {', '.join(CATEGORIES)} (network: connection, timeout or DNS; auth: authentication or permission; "
    "validation: the request was rejected as malformed or invalid; server: the server failed; other: none of "
    "these). Reply with a JSON array of labels in the same order as the messages."
)


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


def _ai_labels(messages: List[str]) -> List[str]:
    backend = ai_backend()
    if not messages or isinstance(backend, NoOpAIBackend):
        return [CATEGORY_OTHER] * len(messages)
    reply = backend.complete(CLASSIFICATION_PROMPT, context={"messages": messages})
    try:
        labels = parse_json_reply(reply) if reply else None
    except json.JSONDecodeError:
        labels = None
    if (isinstance(labels, list) and len(labels) == len(messages)
            and all(label in CATEGORIES for label in labels)):
        return labels
    if reply:
        apitestka_logger.error("AI backend returned unusable failure labels; keeping them as 'other'")
    return [CATEGORY_OTHER] * len(messages)


def classify_failures(error_records: Iterable[list]) -> Counter:
    """Bucket each error record into one of the categories above; return a counter."""
    counter: Counter = Counter()
    unmatched: List[str] = []
    for entry in error_records:
        message = str(entry[1] if len(entry) > 1 else "")
        category = _classify_one(message)
        if category == CATEGORY_OTHER:
            unmatched.append(message)
        else:
            counter[category] += 1
    counter.update(_ai_labels(unmatched))
    return counter
