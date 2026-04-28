"""Tests for the curl-to-action converter."""
from __future__ import annotations

import pytest

from je_api_testka.integrations.curl_import import curl_to_action
from je_api_testka.utils.exception.exceptions import APITesterException


def test_simple_get():
    action = curl_to_action("curl https://api.invalid/x")
    body = action["AT_test_api_method_requests"]
    assert body["http_method"] == "get"
    assert body["test_url"] == "https://api.invalid/x"


def test_post_with_json_body():
    action = curl_to_action(
        "curl -X POST https://api.invalid/x -H 'Content-Type: application/json' "
        "-d '{\"a\":1}'"
    )
    body = action["AT_test_api_method_requests"]
    assert body["http_method"] == "post"
    assert body["json"] == {"a": 1}
    assert body["headers"]["Content-Type"] == "application/json"


def test_post_with_text_body_falls_back_to_data():
    action = curl_to_action("curl -X POST https://api.invalid/x -d 'plain text'")
    body = action["AT_test_api_method_requests"]
    assert body["data"] == "plain text"


def test_implicit_post_when_data_present():
    action = curl_to_action("curl https://api.invalid/x -d '{\"a\":1}'")
    assert action["AT_test_api_method_requests"]["http_method"] == "post"


def test_non_curl_input_raises():
    with pytest.raises(APITesterException):
        curl_to_action("wget https://api.invalid/x")


def test_no_url_raises():
    with pytest.raises(APITesterException):
        curl_to_action("curl -X GET")
