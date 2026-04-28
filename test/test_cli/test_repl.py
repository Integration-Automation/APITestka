"""Tests for the JSON REPL."""
from __future__ import annotations

import io

from je_api_testka.cli.repl import repl_loop


def test_repl_executes_action():
    inp = io.StringIO('[["AT_fake_uuid"]]\nexit\n')
    out = io.StringIO()
    processed = repl_loop(input_stream=inp, output_stream=out, show_prompt=False)
    assert processed == 1
    rendered = out.getvalue()
    assert "AT_fake_uuid" in rendered or "execute" in rendered


def test_repl_invalid_json_does_not_crash():
    inp = io.StringIO("not json\nexit\n")
    out = io.StringIO()
    processed = repl_loop(input_stream=inp, output_stream=out, show_prompt=False)
    assert processed == 0
    assert "invalid JSON" in out.getvalue()


def test_repl_handles_eof():
    inp = io.StringIO('[["AT_fake_uuid"]]')
    out = io.StringIO()
    processed = repl_loop(input_stream=inp, output_stream=out, show_prompt=False)
    assert processed == 1
