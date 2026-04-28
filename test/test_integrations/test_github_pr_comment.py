"""Tests for the GitHub PR comment poster."""
from __future__ import annotations

import json

import httpx
import pytest

from je_api_testka.integrations.github_pr_comment import (
    build_pr_comment_body,
    post_pr_comment,
)
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def test_build_pr_comment_body_includes_summary():
    test_record_instance.clean_record()
    test_record_instance.test_record_list.append({
        "request_method": "GET", "request_url": "http://x.invalid",
        "status_code": 200, "request_time_sec": 0.01,
    })
    body = build_pr_comment_body(title="run #42")
    assert "<details>" in body
    assert "run #42" in body
    test_record_instance.clean_record()


def test_post_pr_comment_invalid_repo_raises():
    with pytest.raises(APITesterException):
        post_pr_comment("not_a_slash", 1, "tok")


def test_post_pr_comment_uses_authorization_header():
    captured = {}

    def _handler(request):
        captured["auth"] = request.headers.get("authorization")
        captured["url"] = str(request.url)
        captured["body"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(201, text="ok")

    transport = httpx.MockTransport(_handler)
    status = post_pr_comment("acme/widget", 7, "tkn",
                             body="hello", transport=transport)
    assert status == 201
    assert captured["auth"] == "Bearer tkn"
    assert "/repos/acme/widget/issues/7/comments" in captured["url"]
    assert captured["body"] == {"body": "hello"}
