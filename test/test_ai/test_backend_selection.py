"""Tests for choosing the AI backend by name, from the environment, the executor and the CLI."""
from __future__ import annotations

import json

import pytest

from je_api_testka.ai import backend as backend_module
from je_api_testka.ai.anthropic_backend import AnthropicAIBackend
from je_api_testka.ai.backend import (
    NoOpAIBackend,
    StaticAIBackend,
    ai_backend,
    build_ai_backend,
    select_ai_backend,
    set_ai_backend,
)
from je_api_testka.ai.failure_classifier import classify_failures
from je_api_testka.ai.fake_data_generator import generate_fake_payload
from je_api_testka.ai.reply import parse_json_reply
from je_api_testka.cli.cli_main import main
from je_api_testka.utils.exception.exceptions import APIAIBackendException
from je_api_testka.utils.executor.action_executor import execute_action


@pytest.fixture(autouse=True)
def _reset_backend():
    yield
    set_ai_backend(NoOpAIBackend())


def test_build_by_name():
    assert isinstance(build_ai_backend("noop"), NoOpAIBackend)
    backend = build_ai_backend("anthropic", model="claude-sonnet-5-5", effort="low")
    assert (backend.model, backend.effort) == ("claude-sonnet-5-5", "low")
    assert build_ai_backend("anthropic").model == "claude-opus-5-5"


def test_build_rejects_unknown_name_and_noop_options():
    with pytest.raises(APIAIBackendException):
        build_ai_backend("gpt")
    with pytest.raises(APIAIBackendException):
        build_ai_backend("noop", model="x")


def test_environment_selects_backend_on_first_use(monkeypatch):
    monkeypatch.setattr(backend_module, "_selection", {})
    monkeypatch.setenv("APITESTKA_AI_BACKEND", "Anthropic")
    monkeypatch.setenv("APITESTKA_AI_MODEL", "claude-haiku-4-5")
    monkeypatch.setenv("APITESTKA_AI_EFFORT", "")
    selected = ai_backend()
    assert isinstance(selected, AnthropicAIBackend)
    assert (selected.model, selected.effort) == ("claude-haiku-4-5", "medium")
    assert ai_backend() is selected


def test_environment_defaults_to_noop(monkeypatch):
    monkeypatch.setattr(backend_module, "_selection", {})
    monkeypatch.delenv("APITESTKA_AI_BACKEND", raising=False)
    assert isinstance(ai_backend(), NoOpAIBackend)


def test_select_through_the_executor():
    record = execute_action([["AT_select_ai_backend", {"name": "anthropic", "effort": "high"}]])
    assert list(record.values()) == ["AnthropicAIBackend"]
    assert ai_backend().effort == "high"
    assert select_ai_backend() == "NoOpAIBackend"


def test_failure_classifier_asks_the_backend_about_unmatched_errors():
    set_ai_backend(StaticAIBackend(response='```json\n["network", "server"]\n```'))
    counts = classify_failures([[{}, "401 Unauthorized"], [{}, "socket reset by peer"], [{}, "upstream said no"]])
    assert counts == {"auth": 1, "network": 1, "server": 1}


@pytest.mark.parametrize("reply", ["", "nope", '["network"]', '["network", "cosmic"]'])
def test_failure_classifier_keeps_other_on_unusable_labels(reply):
    set_ai_backend(StaticAIBackend(response=reply))
    assert classify_failures([[{}, "a"], [{}, "b"]]) == {"other": 2}


def test_fake_payload_accepts_fenced_json():
    set_ai_backend(StaticAIBackend(response='```\n{"id": 7}\n```'))
    assert generate_fake_payload({"type": "object"}) == {"id": 7}


def test_parse_json_reply():
    assert parse_json_reply('  [1, 2] ') == [1, 2]
    assert parse_json_reply('```json\n{"a": 1}\n```') == {"a": 1}
    with pytest.raises(json.JSONDecodeError):
        parse_json_reply("```\nnot json\n```")


def _spec(tmp_path):
    path = tmp_path / "openapi.json"
    path.write_text(json.dumps({"servers": [{"url": "https://api.invalid"}],
                                "paths": {"/items": {"get": {"responses": {"200": {}}}}}}), encoding="utf-8")
    return str(path)


def test_cli_generate_tests_deterministic(tmp_path):
    out = tmp_path / "actions.json"
    assert main(["generate-tests", _spec(tmp_path), "-o", str(out), "--ai", "noop"]) == 0
    assert json.loads(out.read_text(encoding="utf-8"))[0][1]["test_url"] == "https://api.invalid/items"


def test_cli_generate_tests_with_anthropic(tmp_path, monkeypatch, capsys):
    actions = [["AT_test_api_method", {"http_method": "get", "test_url": "https://api.invalid/items?page=1"}]]
    seen = {}

    def _fake_complete(self, prompt, *, context=None):
        seen.update(model=self.model, effort=self.effort)
        return json.dumps(actions)

    monkeypatch.setattr(AnthropicAIBackend, "complete", _fake_complete)
    assert main(["generate-tests", _spec(tmp_path), "--ai", "anthropic", "--effort", "high"]) == 0
    assert json.loads(capsys.readouterr().out) == actions
    assert seen == {"model": "claude-opus-5-5", "effort": "high"}


def test_cli_generate_tests_usage_errors(tmp_path):
    assert main(["generate-tests", str(tmp_path / "missing.json")]) == 2
    assert main(["generate-tests", _spec(tmp_path), "--ai", "noop", "--model", "x"]) == 2
