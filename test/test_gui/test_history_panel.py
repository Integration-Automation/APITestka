"""Tests for the history panel model."""
from __future__ import annotations

from je_api_testka.gui.history_panel import HistoryEntry, HistoryPanelModel


def test_push_and_latest():
    model = HistoryPanelModel()
    model.push(HistoryEntry(method="GET", url="http://x.invalid", status=200))
    assert model.latest().status == 200
    assert len(model.all()) == 1


def test_buffer_respects_limit():
    model = HistoryPanelModel(limit=2)
    for index in range(5):
        model.push(HistoryEntry(method="GET", url=f"http://x.invalid/{index}"))
    assert len(model.all()) == 2


def test_clear_empties_buffer():
    model = HistoryPanelModel()
    model.push(HistoryEntry(method="GET", url="http://x.invalid"))
    model.clear()
    assert model.all() == []
    assert model.latest() is None
