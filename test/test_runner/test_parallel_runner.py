"""Tests for the parallel runner."""
from __future__ import annotations

import threading
import time

from je_api_testka.runner.parallel_runner import run_actions_parallel


def test_runs_in_parallel_with_custom_runner():
    barrier = threading.Barrier(3, timeout=2)
    captured = []

    def _runner(action_list):
        barrier.wait()
        captured.append(action_list[0][1]["index"])
        return {"ok": True}

    actions = [["AT_x", {"index": index}] for index in range(3)]
    results = run_actions_parallel(actions, max_workers=3, runner=_runner)
    assert len(results) == 3
    assert sorted(captured) == [0, 1, 2]


def test_failed_action_returns_repr():
    def _runner(_action_list):
        raise RuntimeError("boom")

    results = run_actions_parallel([["AT_x", {}]], max_workers=1, runner=_runner)
    assert "boom" in results[0]


def test_runner_strips_metadata_before_call():
    captured = []

    def _runner(action_list):
        captured.append(action_list[0][1])
        return {}

    run_actions_parallel(
        [["AT_x", {"id": "a", "tags": ["smoke"], "depends_on": ["b"], "real": 1}]],
        runner=_runner,
    )
    assert captured == [{"real": 1}]


def test_metadata_strip_ignores_when_no_kwargs():
    def _runner(action_list):
        return {"echo": action_list}

    results = run_actions_parallel([["AT_x"]], runner=_runner)
    assert results[0]["echo"] == [["AT_x"]]


def test_executor_command_does_not_block_with_metadata():
    """End-to-end: an action carrying tags should not crash the executor."""
    from je_api_testka.runner.metadata import strip_runner_metadata
    from je_api_testka.utils.executor.action_executor import execute_action

    cleaned = strip_runner_metadata(["AT_fake_uuid", {"tags": ["smoke"]}])
    record = execute_action([cleaned])
    value = next(iter(record.values()))
    assert isinstance(value, str)
    # also wait a hair so threads can settle in the parallel path
    time.sleep(0)
