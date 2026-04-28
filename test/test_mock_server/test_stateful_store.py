"""Tests for StatefulStore."""
from __future__ import annotations

import threading

from je_api_testka.utils.mock_server.stateful_store import StatefulStore


def test_basic_get_set_delete():
    store = StatefulStore()
    store.set("k", 1)
    assert store.get("k") == 1
    assert "k" in store
    store.delete("k")
    assert store.get("k") is None


def test_clear_and_snapshot():
    store = StatefulStore()
    store.set("a", 1)
    store.set("b", 2)
    snap = store.snapshot()
    assert snap == {"a": 1, "b": 2}
    store.clear()
    assert store.snapshot() == {}


def test_concurrent_writes_keep_state_consistent():
    store = StatefulStore()

    def _writer(prefix: str):
        for index in range(50):
            store.set(f"{prefix}-{index}", index)

    threads = [threading.Thread(target=_writer, args=(name,)) for name in "abc"]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(store.snapshot()) == 150
