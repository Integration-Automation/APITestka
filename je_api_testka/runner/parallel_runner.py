"""
Parallel runner for action lists. Each action runs in its own thread; results
come back keyed by original index.

This is for cutting suite duration by overlapping IO-bound HTTP calls. It is
NOT for load testing (no scheduling, no ramp-up, no sustained throughput).
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List

from je_api_testka.runner.metadata import strip_runner_metadata
from je_api_testka.utils.executor.action_executor import executor
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

DEFAULT_MAX_WORKERS: int = 8


def run_actions_parallel(actions: List[list], max_workers: int = DEFAULT_MAX_WORKERS,
                         runner: Callable[[list], Any] = None) -> Dict[int, Any]:
    """Execute each action concurrently and return a dict keyed by index."""
    apitestka_logger.info(
        f"parallel_runner run_actions_parallel actions: {len(actions)} max_workers: {max_workers}"
    )
    runner = runner or executor.execute_action
    cleaned = [strip_runner_metadata(action) for action in actions]
    results: Dict[int, Any] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(runner, [action]): index for index, action in enumerate(cleaned)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as error:
                results[index] = repr(error)
    return results
