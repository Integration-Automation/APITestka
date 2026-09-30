"""Request page: build a request, send it, read the response; history on the left."""
from __future__ import annotations

import json
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from je_api_testka.gui.env_manager_model import EnvManagerModel
from je_api_testka.gui.history_panel import HistoryEntry, HistoryPanelModel
from je_api_testka.gui.request_model import (
    BACKENDS,
    DEFAULT_TIMEOUT_SECONDS,
    HTTP_METHODS,
    SESSION_METHODS,
    RequestSpec,
    describe_response,
    parse_body,
    parse_json_field,
    send_request,
)
from je_api_testka.gui.widgets import (
    TaskThread,
    code_editor,
    log,
    monospace_view,
    muted_label,
    plain_button,
    primary_button,
    tr,
)
from je_api_testka.utils.executor.request_action import build_request_action

_MAX_TIMEOUT_SECONDS: int = 600


class RequestPage(QWidget):
    """Request builder, response viewer and history, sharing the environments of the Environments page."""

    def __init__(self, history: HistoryPanelModel, environments: EnvManagerModel,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._history = history
        self._environments = environments
        self._task: Optional[TaskThread] = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.addLayout(self._build_toolbar())
        splitter = QSplitter()
        splitter.addWidget(self._build_history())
        splitter.addWidget(self._build_request_tabs())
        splitter.addWidget(self._build_response())
        splitter.setSizes([180, 420, 520])
        layout.addWidget(splitter, stretch=1)
        self.refresh_environments()

    def _build_toolbar(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self.method_combo = QComboBox()
        for method in (*HTTP_METHODS, *SESSION_METHODS):
            self.method_combo.addItem(method.upper(), method)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(tr("url_placeholder"))
        self.url_input.returnPressed.connect(self.send)
        self.backend_combo = QComboBox()
        for backend in BACKENDS:
            self.backend_combo.addItem(tr(f"backend_{backend}"), backend)
        self.backend_combo.setCurrentIndex(BACKENDS.index("httpx"))
        self.environment_combo = QComboBox()
        self.environment_combo.activated.connect(self._on_environment_chosen)
        self.send_button = primary_button(tr("send"), self.send)
        self.url_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        for combo in (self.method_combo, self.backend_combo, self.environment_combo):
            combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
            combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        row.addWidget(self.method_combo)
        row.addWidget(self.url_input, stretch=1)
        row.addWidget(self.backend_combo)
        row.addWidget(self.environment_combo)
        row.addWidget(self.send_button)
        row.addWidget(plain_button(tr("copy_as_action"), self.copy_as_action))
        return row

    def _build_history(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.addWidget(muted_label(tr("history")))
        self.history_list = QListWidget()
        self.history_list.itemActivated.connect(self._load_history_item)
        self.history_list.itemClicked.connect(self._load_history_item)
        layout.addWidget(self.history_list, stretch=1)
        layout.addWidget(plain_button(tr("clear"), self._clear_history))
        return panel

    def _build_request_tabs(self) -> QTabWidget:
        tabs = QTabWidget()
        self.params_input = code_editor('{"page": 1}')
        self.headers_input = code_editor('{"Accept": "application/json"}')
        self.body_input = code_editor(tr("body_placeholder"))
        self.auth_input = code_editor('{"username": "user", "password": "pass"}')
        for widget, key in ((self.params_input, "params"), (self.headers_input, "headers"),
                            (self.body_input, "body"), (self.auth_input, "auth")):
            tabs.addTab(widget, tr(key))
        tabs.addTab(self._build_options(), tr("options"))
        return tabs

    def _build_options(self) -> QWidget:
        options = QWidget()
        form = QFormLayout(options)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, _MAX_TIMEOUT_SECONDS)
        self.timeout_spin.setValue(DEFAULT_TIMEOUT_SECONDS)
        self.verify_check = QCheckBox(tr("verify_ssl"))
        self.verify_check.setChecked(True)
        self.redirect_check = QCheckBox(tr("allow_redirects"))
        self.soap_check = QCheckBox(tr("soap"))
        self.result_check_input = QLineEdit()
        self.result_check_input.setPlaceholderText('{"status_code": 200}')
        form.addRow(tr("timeout"), self.timeout_spin)
        form.addRow("", self.verify_check)
        form.addRow("", self.redirect_check)
        form.addRow("", self.soap_check)
        form.addRow(tr("result_check"), self.result_check_input)
        return options

    def _build_response(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 0, 0, 0)
        header = QHBoxLayout()
        self.status_label = QLabel(tr("no_response"))
        self.meta_label = muted_label("")
        header.addWidget(self.status_label)
        header.addStretch(1)
        header.addWidget(self.meta_label)
        layout.addLayout(header)
        tabs = QTabWidget()
        self.response_body = monospace_view()
        self.response_headers = monospace_view()
        tabs.addTab(self.response_body, tr("response_body"))
        tabs.addTab(self.response_headers, tr("response_headers"))
        layout.addWidget(tabs, stretch=1)
        return panel

    def build_spec(self) -> RequestSpec:
        """Collect the form into a :class:`RequestSpec`; raises ``ValueError`` for a bad JSON box."""
        return RequestSpec(
            method=self.method_combo.currentData(), url=self.url_input.text(),
            backend=self.backend_combo.currentData(),
            params=parse_json_field(self.params_input.toPlainText(), tr("params")),
            headers=parse_json_field(self.headers_input.toPlainText(), tr("headers")),
            body=parse_body(self.body_input.toPlainText()),
            auth=parse_json_field(self.auth_input.toPlainText(), tr("auth")),
            timeout=self.timeout_spin.value(), verify=self.verify_check.isChecked(),
            allow_redirects=self.redirect_check.isChecked(), soap=self.soap_check.isChecked(),
            result_check=parse_json_field(self.result_check_input.text(), tr("result_check")),
        )

    def send(self) -> None:
        """Send the request in the background and show the response."""
        try:
            spec = self.build_spec()
        except ValueError as error:
            self._show_error(str(error))
            return
        self.send_button.setEnabled(False)
        self.status_label.setText(tr("sending"))
        self._task = TaskThread(lambda: send_request(spec), self)
        self._task.succeeded.connect(lambda data: self._show_response(spec, data))
        self._task.failed.connect(self._show_error)
        self._task.finished.connect(lambda: self.send_button.setEnabled(True))
        self._task.start()

    def _set_status(self, text: str, status_class: str) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("status", status_class)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _show_response(self, spec: RequestSpec, response_data: dict) -> None:
        view = describe_response(response_data)
        self._set_status(str(view.status), view.status_class)
        self.meta_label.setText(tr("response_meta").format(ms=view.elapsed_ms, size=view.size_bytes))
        self.response_body.setPlainText(view.body)
        self.response_headers.setPlainText(view.headers)
        self._history.push(HistoryEntry(spec.method, spec.url.strip(), view.status, f"{view.elapsed_ms:.0f} ms"))
        self._refresh_history()

    def _show_error(self, message: str) -> None:
        self._set_status(tr("request_failed"), "server-error")
        self.meta_label.setText("")
        self.response_body.setPlainText(message)
        self.response_headers.clear()
        log(f"{tr('request_failed')}: {message}")

    def copy_as_action(self) -> None:
        """Put the request as an ``AT_test_api_method`` action on the clipboard."""
        try:
            spec = self.build_spec()
        except ValueError as error:
            self._show_error(str(error))
            return
        options = {key: value for key, value in (("params", spec.params), ("timeout", spec.timeout),
                                                 ("result_check_dict", spec.result_check)) if value}
        action = build_request_action(spec.method, spec.url.strip(), headers=spec.headers, body=spec.body, **options)
        QApplication.clipboard().setText(json.dumps(action, ensure_ascii=False))
        log(tr("copied_action"))

    def _refresh_history(self) -> None:
        self.history_list.clear()
        for entry in reversed(self._history.all()):
            item = QListWidgetItem(f"{entry.status or '-'}  {entry.method.upper()}  {entry.url}")
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)

    def _load_history_item(self, item: QListWidgetItem) -> None:
        entry: HistoryEntry = item.data(Qt.ItemDataRole.UserRole)
        self.method_combo.setCurrentIndex(max(self.method_combo.findData(entry.method), 0))
        self.url_input.setText(entry.url)

    def _clear_history(self) -> None:
        self._history.clear()
        self._refresh_history()

    def refresh_environments(self) -> None:
        """Reload the environment list (after the Environments page changed it)."""
        self.environment_combo.clear()
        self.environment_combo.addItem(tr("no_environment"), "")
        for environment in self._environments.list_envs():
            self.environment_combo.addItem(environment.name, environment.name)
        index = self.environment_combo.findData(self._environments.active)
        self.environment_combo.setCurrentIndex(max(index, 0))

    def _on_environment_chosen(self, _index: int) -> None:
        name = self.environment_combo.currentData()
        if name:
            self._environments.activate(name)
            log(tr("environment_activated").format(name=name))
