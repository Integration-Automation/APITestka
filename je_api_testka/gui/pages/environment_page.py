"""Environments page: named variable sets that fill ``{{placeholders}}`` in requests."""
from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QInputDialog, QListWidget, QWidget

from je_api_testka.gui.env_manager_model import EnvManagerModel
from je_api_testka.gui.widgets import JSON_FILTER, BasePage, code_editor, log, plain_button, primary_button, tr


class EnvironmentPage(BasePage):
    """List, edit, activate, import and export environments; ``changed`` fires after every edit."""

    changed = Signal()

    def __init__(self, environments: EnvManagerModel, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_environments"), tr("environments_help"), parent)
        self._environments = environments
        row = QHBoxLayout()
        self.env_list = QListWidget()
        self.env_list.currentTextChanged.connect(self._show_environment)
        self.values_editor = code_editor('{"base": "https://staging.example.com", "token": "..."}')
        row.addWidget(self.env_list, stretch=1)
        row.addWidget(self.values_editor, stretch=2)
        self.body.addLayout(row, stretch=1)
        buttons = QHBoxLayout()
        for text, handler in ((tr("new"), self._new), (tr("save"), self._save), (tr("delete"), self._delete),
                              (tr("import"), self._import), (tr("export"), self._export)):
            buttons.addWidget(plain_button(text, handler))
        buttons.addStretch(1)
        buttons.addWidget(primary_button(tr("activate"), self._activate))
        self.body.addLayout(buttons)
        self._reload()

    def _reload(self, select: str = "") -> None:
        self.env_list.clear()
        for environment in self._environments.list_envs():
            self.env_list.addItem(environment.name)
        matches = self.env_list.findItems(select, Qt.MatchFlag.MatchExactly) if select else []
        if matches:
            self.env_list.setCurrentItem(matches[0])
        self.changed.emit()

    def _selected(self) -> str:
        item = self.env_list.currentItem()
        return item.text() if item is not None else ""

    def _show_environment(self, name: str) -> None:
        values = next((env.values for env in self._environments.list_envs() if env.name == name), {})
        self.values_editor.setPlainText(json.dumps(values, indent=2, ensure_ascii=False))

    def _new(self) -> None:
        name, accepted = QInputDialog.getText(self, tr("new"), tr("environment_name"))
        if accepted and name.strip():
            self._environments.upsert(name.strip(), {})
            self._reload(name.strip())

    def _save(self) -> None:
        name = self._selected()
        if not name:
            return
        try:
            values = json.loads(self.values_editor.toPlainText() or "{}")
        except json.JSONDecodeError as error:
            log(f"{tr('error')}: {error}")
            return
        if not isinstance(values, dict):
            log(f"{tr('error')}: {tr('environment_must_be_object')}")
            return
        self._environments.upsert(name, {str(key): str(value) for key, value in values.items()})
        self._reload(name)
        log(tr("saved").format(name=name))

    def _delete(self) -> None:
        if self._selected():
            self._environments.remove(self._selected())
            self._reload()

    def _activate(self) -> None:
        name = self._selected()
        if name:
            self._environments.activate(name)
            self.changed.emit()
            log(tr("environment_activated").format(name=name))

    def _import(self) -> None:
        path, _selected = QFileDialog.getOpenFileName(self, tr("import"), "", JSON_FILTER)
        if not path:
            return
        try:
            self._environments.import_from_file(path)
        except (OSError, ValueError, TypeError) as error:
            log(f"{tr('error')}: {error}")
            return
        self._reload()

    def _export(self) -> None:
        path, _selected = QFileDialog.getSaveFileName(self, tr("export"), "environments.json", JSON_FILTER)
        if path:
            self._environments.export_to_file(path)
            log(tr("written").format(path=path))
