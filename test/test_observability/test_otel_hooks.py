"""Tests for the OpenTelemetry hook."""
from __future__ import annotations

from je_api_testka.utils.observability import otel_hooks


def test_instrument_request_no_op_when_otel_missing(monkeypatch):
    monkeypatch.setattr(otel_hooks, "_try_import_tracer", lambda: None)
    with otel_hooks.instrument_request("GET", "https://example.invalid"):
        executed = True
    assert executed
    assert otel_hooks.is_otel_available() is False


def test_instrument_request_uses_tracer_when_available(monkeypatch):
    captured = {}

    class _Span:
        def set_attribute(self, key, value):
            captured[key] = value

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    class _Tracer:
        def start_as_current_span(self, name):
            captured["span_name"] = name
            return _Span()

    monkeypatch.setattr(otel_hooks, "_try_import_tracer", lambda: _Tracer())
    with otel_hooks.instrument_request("post", "https://example.invalid/x", attributes={"k": "v"}):
        # the span attributes are recorded inside __enter__, so the body of
        # the with block deliberately performs no further work.
        assert "span_name" in captured
    assert captured["span_name"] == "POST https://example.invalid/x"
    assert captured["http.method"] == "POST"
    assert captured["k"] == "v"
