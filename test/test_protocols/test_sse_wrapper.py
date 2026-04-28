"""Tests for the SSE helper.

We don't spin up a real SSE server; we exercise ``iter_sse_events`` against a
fake stream object that mimics the small surface area used (``iter_lines``,
``raise_for_status``, context manager protocol).
"""
from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

from je_api_testka.sse_wrapper import sse_method


class _FakeStreamResponse:
    def __init__(self, lines: Iterable[str]) -> None:
        self._lines = list(lines)

    def raise_for_status(self) -> None:
        return None

    def iter_lines(self):
        yield from self._lines


@contextmanager
def _fake_stream(_method, _url, **_kwargs):
    yield _FakeStreamResponse([
        "event: ping",
        "data: hello",
        "",
        "data: second",
        "",
    ])


def test_iter_sse_events_parses_basic_stream(monkeypatch):
    monkeypatch.setattr(sse_method.httpx, "stream", _fake_stream)
    events = list(sse_method.iter_sse_events("http://example.invalid", max_events=2))
    assert events == [
        {"event": "ping", "data": "hello"},
        {"data": "second"},
    ]


def test_iter_sse_events_respects_max(monkeypatch):
    @contextmanager
    def _three_events(_method, _url, **_kwargs):
        yield _FakeStreamResponse([
            "data: a", "",
            "data: b", "",
            "data: c", "",
        ])

    monkeypatch.setattr(sse_method.httpx, "stream", _three_events)
    events = list(sse_method.iter_sse_events("http://example.invalid", max_events=2))
    assert len(events) == 2


def test_test_api_method_sse_records(monkeypatch):
    from je_api_testka.utils.test_record.test_record_class import test_record_instance

    monkeypatch.setattr(sse_method.httpx, "stream", _fake_stream)
    test_record_instance.clean_record()
    record = sse_method.test_api_method_sse("http://example.invalid", max_events=2)
    assert record["events"]
    assert test_record_instance.test_record_list, "record was not stored"
