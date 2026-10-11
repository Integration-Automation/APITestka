"""Markdown fence parsing stays bounded for malformed model replies."""
import json

import pytest

from je_api_testka.ai.reply import parse_json_reply


@pytest.mark.parametrize("reply", ['{"a": 1}', '```json\n{"a": 1}\n```', '```\r\n{"a": 1}\n```'])
def test_plain_and_fenced_json(reply):
    assert parse_json_reply(reply) == {"a": 1}


def test_long_unterminated_fence_is_rejected():
    reply = "```json\n" + " " * 100_000 + "invalid"
    with pytest.raises(json.JSONDecodeError):
        parse_json_reply(reply)
