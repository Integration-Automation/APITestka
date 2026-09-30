"""Read JSON out of a model's text reply."""
from __future__ import annotations

import json
import re
from typing import Any

_FENCE = re.compile(r"^```[A-Za-z0-9_-]*\s*\n(.*?)\n?```$", re.DOTALL)


def parse_json_reply(reply: str) -> Any:
    """
    Parse ``reply`` as JSON, ignoring surrounding whitespace and one Markdown code fence.

    :raises json.JSONDecodeError: when the reply is not JSON.
    """
    text = reply.strip()
    fenced = _FENCE.match(text)
    if fenced:
        text = fenced.group(1).strip()
    return json.loads(text)
