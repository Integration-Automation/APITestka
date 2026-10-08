"""Helpers shared by the ``apitestka`` subcommands."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from threading import Lock
from types import TracebackType
from typing import Any

from je_action_core import ExecutionReporter

from je_api_testka.utils.executor.action_executor import execute_action, execute_files, executor
from je_api_testka.utils.file_process.get_dir_file_list import get_dir_files_as_list
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

EXIT_OK: int = 0
EXIT_FAILED: int = 1
EXIT_USAGE: int = 2


class _CountingReporter(ExecutionReporter):
    """The executor's reporter for one CLI run: passes every event on and counts the actions that raised."""

    def __init__(self, delegate: ExecutionReporter) -> None:
        self._delegate = delegate
        self._lock = Lock()
        self.raised = 0

    def on_start(self, action_list: Any) -> None:
        self._delegate.on_start(action_list)

    def on_event(self, action: Any) -> None:
        self._delegate.on_event(action)

    def on_success(self, action: Any) -> None:
        self._delegate.on_success(action)

    def on_failure(self, action: Any, error: Exception) -> None:
        # AT_run_actions_parallel runs actions on several threads.
        with self._lock:
            self.raised += 1
        self._delegate.on_failure(action, error)

    def on_empty(self, action_list: Any) -> None:
        self._delegate.on_empty(action_list)

    def on_records(self, records: Mapping[str, Any]) -> None:
        self._delegate.on_records(records)


class FailureCount:
    """
    Counts what fails while its ``with`` block runs.

    The executor records a failed action and goes on, and a request that fails is kept in the
    test record without raising, so a run that failed returns like one that passed. ``failed``
    adds the two up: the actions that raised, and the requests added to the failure record.
    """

    def __init__(self) -> None:
        self._settings = executor.settings
        self._reporter = _CountingReporter(self._settings.reporter)
        self._recorded_before = 0

    def __enter__(self) -> FailureCount:
        self._settings = executor.settings
        self._reporter = _CountingReporter(self._settings.reporter)
        self._recorded_before = len(test_record_instance.error_record_list)
        executor.settings = replace(self._settings, reporter=self._reporter)
        return self

    def __exit__(self, kind: type[BaseException] | None, error: BaseException | None,
                 trace: TracebackType | None) -> None:
        executor.settings = self._settings

    @property
    def failed(self) -> int:
        """How many actions raised or requests were recorded as failed since the block was entered."""
        recorded = len(test_record_instance.error_record_list) - self._recorded_before
        return self._reporter.raised + max(recorded, 0)


def run_action_path(target: Path) -> int:
    """Execute an action JSON file, or every JSON file in a directory; return 2 when ``target`` is missing."""
    if target.is_dir():
        execute_files(get_dir_files_as_list(str(target)))
    elif target.is_file():
        execute_action(read_action_json(str(target)))
    else:
        apitestka_logger.error(f"cli: path not found: {target}")
        return EXIT_USAGE
    return EXIT_OK
