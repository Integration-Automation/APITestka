"""Read JSON out of a model's text reply."""
from __future__ import annotations

import json
import re
from typing import Any

_FENCE_LANGUAGE = re.compile(r"[A-Za-z0-9_-]*")


def parse_json_reply(reply: str) -> Any:
    """
    Parse ``reply`` as JSON, ignoring surrounding whitespace and one Markdown code fence.

    :raises json.JSONDecodeError: when the reply is not JSON.
    """
    text = reply.strip()
    if text.startswith("```") and text.endswith("```"):
        language, newline, body = text[3:-3].partition("\n")
        if newline and _FENCE_LANGUAGE.fullmatch(language.strip()):
            text = body.strip()
    return json.loads(text)
