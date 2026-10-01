"""Tools page: JSON formatting and files, XML reformatting, project scaffolding."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QFileDialog, QLineEdit, QWidget

from je_api_testka.gui.widgets import (
    DIRECTORY,
    JSON_FILTER,
    BasePage,
    FileField,
    code_editor,
    form_group,
    log,
    monospace_view,
    plain_button,
    primary_button,
    tr,
)
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.json.json_file.json_file import read_action_json, write_action_json
from je_api_testka.utils.json.json_format.json_process import reformat_json
from je_api_testka.utils.project.create_project_structure import create_project_dir
from je_api_testka.utils.xml.xml_file.xml_file import reformat_xml_file


class ToolsPage(BasePage):
    """Small helpers that used to live in the Tools tab."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_tools"), "", parent)
        self.json_input = code_editor('{"a": 1}')
        self.json_output = monospace_view()
        for editor in (self.json_input, self.json_output):
            editor.setMinimumHeight(120)
        self.body.addWidget(form_group(tr("json_tools"), [(tr("input"), self.json_input),
                                                          (tr("output"), self.json_output)],
                                       [plain_button(tr("read_file"), self.read_json),
                                        plain_button(tr("write_file"), self.write_json),
                                        primary_button(tr("format"), self.format_json)]))
        self.xml_field = FileField(file_filter="XML (*.xml)")
        self.body.addWidget(form_group(tr("xml_tools"), [(tr("xml_file"), self.xml_field)],
                                       [primary_button(tr("reformat_in_place"), self.reformat_xml)]))
        self.project_field = FileField(DIRECTORY)
        self.project_name = QLineEdit("APITestka")
        self.body.addWidget(form_group(tr("create_project"), [(tr("folder"), self.project_field),
                                                              (tr("project_name"), self.project_name)],
                                       [primary_button(tr("create"), self.create_project)]))
        self.body.addStretch(1)

    def format_json(self) -> None:
        """Pretty-print the JSON input into the output box."""
        try:
            self.json_output.setPlainText(reformat_json(self.json_input.toPlainText()))
        except APITesterException as error:
            self.json_output.setPlainText(f"{tr('error')}: {error}")

    def read_json(self) -> None:
        """Load a JSON file into the input box."""
        path, _selected = QFileDialog.getOpenFileName(self, tr("read_file"), "", JSON_FILTER)
        if not path:
            return
        try:
            self.json_input.setPlainText(json.dumps(read_action_json(path), indent=2, ensure_ascii=False))
        except APITesterException as error:
            log(f"{tr('error')}: {error}")

    def write_json(self) -> None:
        """Save the input box as a JSON file."""
        path, _selected = QFileDialog.getSaveFileName(self, tr("write_file"), "", JSON_FILTER)
        if not path:
            return
        try:
            write_action_json(path, json.loads(self.json_input.toPlainText()))
        except (json.JSONDecodeError, APITesterException) as error:
            log(f"{tr('error')}: {error}")
            return
        log(tr("written").format(path=path))

    def reformat_xml(self) -> None:
        """Reformat the chosen XML file in place."""
        path = self.xml_field.path()
        if not path:
            return
        try:
            target = Path(path)
            target.write_text(reformat_xml_file(target.read_text(encoding="utf-8")), encoding="utf-8")
        except (OSError, APITesterException) as error:
            log(f"{tr('error')}: {error}")
            return
        log(tr("written").format(path=path))

    def create_project(self) -> None:
        """Scaffold a project folder with keyword and executor templates."""
        name = self.project_name.text().strip() or "APITestka"
        try:
            create_project_dir(project_path=self.project_field.path() or None, parent_name=name)
        except OSError as error:
            log(f"{tr('error')}: {error}")
            return
        log(tr("project_created").format(name=name))
