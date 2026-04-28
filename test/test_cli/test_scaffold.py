"""Tests for the action-list scaffold helper."""
from __future__ import annotations

import json

from je_api_testka.cli.scaffold_test import scaffold_action_list, write_scaffold


def test_scaffold_action_list_includes_smoke_check():
    actions = scaffold_action_list("https://x.invalid", method="POST")
    assert actions[0][0] == "AT_test_api_method_requests"
    assert actions[0][1]["http_method"] == "post"
    assert actions[0][1]["tags"] == ["smoke"]


def test_write_scaffold_persists_json(tmp_path):
    target = tmp_path / "starter.json"
    write_scaffold(str(target), "https://x.invalid")
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert isinstance(payload, list) and payload
