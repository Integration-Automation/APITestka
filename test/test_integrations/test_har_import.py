"""Tests for the HAR import."""
from __future__ import annotations

import json

from je_api_testka.integrations.har_import import convert_har


def test_convert_har_basic(tmp_path):
    har = {
        "log": {
            "entries": [
                {
                    "request": {
                        "method": "GET",
                        "url": "https://api.invalid/users",
                        "headers": [{"name": "Accept", "value": "application/json"}],
                    }
                },
                {
                    "request": {
                        "method": "POST",
                        "url": "https://api.invalid/users",
                        "headers": [],
                        "postData": {"text": "{\"name\":\"alice\"}"},
                    }
                },
            ]
        }
    }
    path = tmp_path / "out.har"
    path.write_text(json.dumps(har), encoding="utf-8")
    actions = convert_har(str(path))
    assert len(actions) == 2
    first = actions[0]["AT_test_api_method_requests"]
    assert first["http_method"] == "get"
    assert first["headers"]["Accept"] == "application/json"
    second = actions[1]["AT_test_api_method_requests"]
    assert second["json"] == {"name": "alice"}


def test_convert_har_skips_entries_without_url(tmp_path):
    path = tmp_path / "out.har"
    path.write_text(json.dumps({"log": {"entries": [{"request": {"method": "GET"}}]}}),
                    encoding="utf-8")
    assert convert_har(str(path)) == []
