"""Tests for the Anthropic reference backend (a fake client stands in for the API)."""
from __future__ import annotations

import builtins
import json
from types import SimpleNamespace

import pytest

from je_api_testka.ai import anthropic_backend
from je_api_testka.ai.anthropic_backend import FALLBACK_BETA, SYSTEM_PROMPT, AnthropicAIBackend
from je_api_testka.ai.backend import NoOpAIBackend, set_ai_backend
from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.utils.exception.exceptions import APIAIBackendException


class _FakeMessages:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response


def _response(text="ok", stop_reason="end_turn", category=None):
    content = [SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(content=content, stop_reason=stop_reason, model="claude-opus-5-5",
                           stop_details=SimpleNamespace(category=category), _request_id="req_1")


def _backend(response=None, error=None, **options):
    messages = _FakeMessages(response, error)
    return AnthropicAIBackend(client=SimpleNamespace(beta=SimpleNamespace(messages=messages)), **options), messages


@pytest.fixture(autouse=True)
def _reset_backend():
    yield
    set_ai_backend(NoOpAIBackend())


def test_default_request_uses_opus_medium_effort_and_fallbacks():
    options = AnthropicAIBackend().request_options("Do it.", {"b": 1, "a": "é"})
    assert options["model"] == "claude-opus-5-5"
    assert options["max_tokens"] == 16000
    assert options["system"] == SYSTEM_PROMPT
    assert options["output_config"] == {"effort": "medium"}
    assert options["fallbacks"] == "default"
    assert options["betas"] == [FALLBACK_BETA]
    assert "thinking" not in options  # thinking is always on for this model
    assert options["messages"] == [{"role": "user", "content": 'Do it.\n\n<context>\n{"a": "é", "b": 1}\n</context>'}]


def test_options_can_turn_off_fallbacks_and_effort():
    options = AnthropicAIBackend(model="claude-sonnet-5-5", effort=None, fallbacks=None).request_options("p")
    assert options["model"] == "claude-sonnet-5-5"
    assert options["messages"][0]["content"] == "p"
    assert not {"output_config", "fallbacks", "betas"} & set(options)


def test_complete_returns_text_blocks_only():
    pytest.importorskip("anthropic")
    backend, messages = _backend(_response("hello"))
    assert backend.complete("p", context={"x": 1}) == "hello"
    assert messages.calls[0]["fallbacks"] == "default"


@pytest.mark.parametrize("stop_reason", ["refusal", "max_tokens"])
def test_unusable_replies_become_empty(stop_reason):
    pytest.importorskip("anthropic")
    backend, _messages = _backend(_response("partial", stop_reason=stop_reason, category="cyber"))
    assert backend.complete("p") == ""


def _status_error(anthropic, error_class, status):
    httpx2 = pytest.importorskip("httpx2")
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return error_class("boom", response=httpx2.Response(status, request=request), body=None)


def test_transient_errors_become_empty():
    anthropic = pytest.importorskip("anthropic")
    httpx2 = pytest.importorskip("httpx2")
    request = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    for error in (_status_error(anthropic, anthropic.RateLimitError, 429),
                  _status_error(anthropic, anthropic.InternalServerError, 529),
                  anthropic.APIConnectionError(request=request),
                  anthropic.APITimeoutError(request=request)):
        backend, _messages = _backend(error=error)
        assert backend.complete("p") == ""


def test_rejected_requests_raise():
    anthropic = pytest.importorskip("anthropic")
    for error_class, status in ((anthropic.AuthenticationError, 401), (anthropic.BadRequestError, 400),
                                (anthropic.NotFoundError, 404)):
        backend, _messages = _backend(error=_status_error(anthropic, error_class, status))
        with pytest.raises(APIAIBackendException, match=str(status)):
            backend.complete("p")


def test_client_is_built_lazily_with_timeout(monkeypatch):
    anthropic = pytest.importorskip("anthropic")
    built = []
    monkeypatch.setattr(anthropic, "Anthropic", lambda **kwargs: built.append(kwargs) or "client")
    backend = AnthropicAIBackend(timeout=30.0)
    assert built == []
    assert backend._client() == "client" and backend._client() == "client"
    assert built == [{"timeout": 30.0}]


def test_missing_sdk_raises(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name == "anthropic":
            raise ImportError("nope")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APIAIBackendException, match="je_api_testka\\[ai\\]"):
        anthropic_backend._import_anthropic()


SPEC = {"servers": [{"url": "https://api.invalid"}], "paths": {"/items": {"get": {"responses": {"200": {}}}}}}


def test_test_generation_uses_a_valid_fenced_reply():
    pytest.importorskip("anthropic")
    actions = [["AT_test_api_method", {"http_method": "get", "test_url": "https://api.invalid/items"}]]
    backend, messages = _backend(_response("```json\n" + json.dumps(actions) + "\n```"))
    set_ai_backend(backend)
    assert generate_tests_from_openapi(SPEC) == actions
    assert '"openapi"' in messages.calls[0]["messages"][0]["content"]


@pytest.mark.parametrize("reply", ["[]", '[{"AT_test_api_method": {}}]', '[["print", {}]]', '[["AT_x", 1]]', "nope"])
def test_test_generation_falls_back_on_unusable_replies(reply):
    pytest.importorskip("anthropic")
    backend, _messages = _backend(_response(reply))
    set_ai_backend(backend)
    assert generate_tests_from_openapi(SPEC)[0][1]["result_check_dict"] == {"status_code": 200}
