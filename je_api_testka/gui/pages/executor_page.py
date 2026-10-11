"""Executor page: run action JSON typed in, from a file, or from every JSON file in a folder."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QHBoxLayout, QWidget

from je_api_testka.gui.widgets import (
    DIRECTORY,
    BasePage,
    FileField,
    code_editor,
    form_group,
    log,
    monospace_view,
    primary_button,
    tr,
)
from je_api_testka.utils.executor.action_executor import execute_action, execute_files
from je_api_testka.utils.file_process.get_dir_file_list import get_dir_files_as_list
from je_api_testka.utils.json.json_file.json_file import read_action_json

EXAMPLE_ACTIONS: str = '[["AT_test_api_method", {"http_method": "get", "test_url": "https://httpbin.org/get"}]]'


def format_results(results: dict) -> str:
    """Render ``execute_action`` results as one ``action => value`` block per action."""
    return "\n".join(f"{action}\n  => {value!r}" for action, value in results.items())


class ExecutorPage(BasePage):
    """Run executor actions without leaving the GUI."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_executor"), tr("executor_help"), parent)
        self.actions_editor = code_editor(EXAMPLE_ACTIONS)
        self.actions_editor.setMinimumHeight(160)
        self.body.addWidget(self.actions_editor)
        row = QHBoxLayout()
        row.addStretch(1)
        row.addWidget(primary_button(tr("run"), self.run_typed))
        self.body.addLayout(row)
        self.file_field = FileField()
        self.dir_field = FileField(DIRECTORY)
        self.body.addWidget(form_group(tr("run_from_disk"), [(tr("action_file"), self.file_field),
                                                             (tr("action_folder"), self.dir_field)],
                                       [primary_button(tr("run_file"), self.run_file),
                                        primary_button(tr("run_folder"), self.run_folder)]))
        self.results_view = monospace_view()
        self.results_view.setMinimumHeight(180)
        self.body.addWidget(self.results_view, stretch=1)

    def run_typed(self) -> None:
        """Run the actions in the editor."""
        try:
            actions = json.loads(self.actions_editor.toPlainText())
        except json.JSONDecodeError as error:
            log(f"{tr('error')}: {error}")
            return
        self.run_task(lambda: execute_action(actions), self._show)

    def run_file(self) -> None:
        """Run the chosen action file."""
        path = self.file_field.path()
        if path:
            self.run_task(lambda: execute_action(read_action_json(path)), self._show)

    def run_folder(self) -> None:
        """Run every JSON file in the chosen folder."""
        folder = self.dir_field.path()
        if not folder:
            return
        files = [name for name in get_dir_files_as_list(folder) if Path(name).suffix == ".json"]
        if not files:
            log(tr("no_json_files"))
            return
        self.run_task(lambda: execute_files(files), self._show_many)

    def _show(self, results: object) -> None:
        self.results_view.setPlainText(format_results(results) if isinstance(results, dict) else repr(results))

    def _show_many(self, results: object) -> None:
        blocks = [f"--- {index} ---\n{format_results(result)}" for index, result in enumerate(results or [], 1)
                  if isinstance(result, dict)]
        self.results_view.setPlainText("\n".join(blocks))
