import json

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTabWidget, QFormLayout, QPushButton, QTextEdit,
    QCheckBox, QSpinBox, QFileDialog, QGroupBox,
    QPlainTextEdit,
)

from je_api_testka.gui.api_testka_gui_thread import (
    APIRequestThread, ExecutorThread, ReportThread, MockServerThread,
)
from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.message_queue import api_testka_ui_queue
from je_api_testka.utils.json.json_format.json_process import reformat_json
from je_api_testka.utils.json.json_file.json_file import read_action_json, write_action_json
from je_api_testka.utils.project.create_project_structure import create_project_dir
from je_api_testka.utils.test_record.test_record_class import test_record_instance
from je_api_testka.utils.file_process.get_dir_file_list import get_dir_files_as_list


_JSON_FILE_FILTER = "JSON Files (*.json)"


def _t(key):
    """Shorthand to get translated string."""
    return language_wrapper.language_word_dict.get(key, key)


class APITestkaWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threads = []

        main_layout = QVBoxLayout()

        self.main_tabs = QTabWidget()
        main_layout.addWidget(self.main_tabs)

        # Log panel at the bottom
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        self.log_panel.setMaximumHeight(200)

        log_layout = QVBoxLayout()
        log_header = QHBoxLayout()
        log_header.addWidget(QLabel(_t("response_and_log")))
        self.clear_log_btn = QPushButton(_t("clear"))
        self.clear_log_btn.clicked.connect(self.log_panel.clear)
        self.clear_log_btn.setMaximumWidth(80)
        log_header.addWidget(self.clear_log_btn)
        log_layout.addLayout(log_header)
        log_layout.addWidget(self.log_panel)

        main_layout.addLayout(log_layout)

        # Build all tabs
        self._build_api_request_tab()
        self._build_executor_tab()
        self._build_reports_tab()
        self._build_mock_server_tab()
        self._build_test_records_tab()
        self._build_tools_tab()

        # Timer for pulling from queue
        self.pull_log_timer = QTimer()
        self.pull_log_timer.setInterval(20)
        self.pull_log_timer.timeout.connect(self.pull_log)
        self.pull_log_timer.start()

        self.setLayout(main_layout)

    # ─── API Request Tab ───────────────────────────────────────────

    def _build_api_request_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # URL + Method + Backend row
        url_row = QHBoxLayout()
        url_row.addWidget(QLabel(_t("url")))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://httpbin.org/get")
        url_row.addWidget(self.url_input, stretch=3)

        self.method_combo = QComboBox()
        methods = [
            "get", "post", "put", "patch", "delete", "head", "options",
            "session_get", "session_post", "session_put", "session_patch",
            "session_delete", "session_head", "session_options",
        ]
        for m in methods:
            self.method_combo.addItem(_t(m), m)
        url_row.addWidget(self.method_combo)

        url_row.addWidget(QLabel(_t("backend")))
        self.backend_combo = QComboBox()
        self.backend_combo.addItem(_t("backend_requests"), "requests")
        self.backend_combo.addItem(_t("backend_httpx"), "httpx")
        self.backend_combo.addItem(_t("backend_httpx_async"), "httpx_async")
        self.backend_combo.setCurrentIndex(1)
        url_row.addWidget(self.backend_combo)

        layout.addLayout(url_row)

        # Param / Headers / Body / Auth tabs
        self.request_tabs = QTabWidget()

        # Params
        param_widget = QWidget()
        param_layout = QVBoxLayout()
        self.param_input = QPlainTextEdit()
        self.param_input.setPlaceholderText(_t("param_placeholder"))
        self.param_input.setMaximumHeight(100)
        param_layout.addWidget(self.param_input)
        param_widget.setLayout(param_layout)
        self.request_tabs.addTab(param_widget, _t("param"))

        # Headers
        headers_widget = QWidget()
        headers_layout = QVBoxLayout()
        self.headers_input = QPlainTextEdit()
        self.headers_input.setPlaceholderText(_t("headers_placeholder"))
        self.headers_input.setMaximumHeight(100)
        headers_layout.addWidget(self.headers_input)
        headers_widget.setLayout(headers_layout)
        self.request_tabs.addTab(headers_widget, _t("headers"))

        # Body
        body_widget = QWidget()
        body_layout = QVBoxLayout()
        self.body_input = QPlainTextEdit()
        self.body_input.setPlaceholderText(_t("body_placeholder"))
        self.body_input.setMaximumHeight(100)
        body_layout.addWidget(self.body_input)
        body_widget.setLayout(body_layout)
        self.request_tabs.addTab(body_widget, _t("body"))

        # Auth
        auth_widget = QWidget()
        auth_layout = QVBoxLayout()
        self.auth_input = QPlainTextEdit()
        self.auth_input.setPlaceholderText(_t("auth_placeholder"))
        self.auth_input.setMaximumHeight(100)
        auth_layout.addWidget(self.auth_input)
        auth_widget.setLayout(auth_layout)
        self.request_tabs.addTab(auth_widget, _t("auth"))

        layout.addWidget(self.request_tabs)

        # Options row
        options_row = QHBoxLayout()

        options_row.addWidget(QLabel(_t("timeout")))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 300)
        self.timeout_spin.setValue(5)
        options_row.addWidget(self.timeout_spin)

        self.verify_ssl_cb = QCheckBox(_t("verify_ssl"))
        options_row.addWidget(self.verify_ssl_cb)

        self.allow_redirects_cb = QCheckBox(_t("allow_redirects"))
        options_row.addWidget(self.allow_redirects_cb)

        self.soap_cb = QCheckBox(_t("soap"))
        options_row.addWidget(self.soap_cb)

        options_row.addStretch()
        layout.addLayout(options_row)

        # Result check
        check_row = QHBoxLayout()
        check_row.addWidget(QLabel(_t("result_check")))
        self.result_check_input = QLineEdit()
        self.result_check_input.setPlaceholderText(_t("result_check_placeholder"))
        check_row.addWidget(self.result_check_input)
        layout.addLayout(check_row)

        # Send button
        self.send_btn = QPushButton(_t("send"))
        self.send_btn.clicked.connect(self._on_send)
        layout.addWidget(self.send_btn)

        tab.setLayout(layout)
        self.main_tabs.addTab(tab, _t("tab_api_request"))

    def _parse_json_field(self, text):
        text = text.strip()
        if not text:
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _on_send(self):
        thread = APIRequestThread()
        thread.url = self.url_input.text().strip()
        thread.http_method = self.method_combo.currentData()
        thread.backend = self.backend_combo.currentData()
        thread.params = self._parse_json_field(self.param_input.toPlainText())
        thread.headers = self._parse_json_field(self.headers_input.toPlainText())
        thread.auth = self._parse_json_field(self.auth_input.toPlainText())
        thread.timeout = self.timeout_spin.value()
        thread.verify_ssl = self.verify_ssl_cb.isChecked()
        thread.allow_redirects = self.allow_redirects_cb.isChecked()
        thread.soap = self.soap_cb.isChecked()
        thread.result_check_dict = self._parse_json_field(self.result_check_input.text())

        body_text = self.body_input.toPlainText().strip()
        if body_text:
            # Try to parse as JSON, otherwise send as string
            try:
                thread.body = json.loads(body_text)
            except json.JSONDecodeError:
                thread.body = body_text

        self._start_thread(thread)

    # ─── Executor Tab ──────────────────────────────────────────────

    def _build_executor_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Manual action input
        group_manual = QGroupBox(_t("executor_json_input"))
        manual_layout = QVBoxLayout()
        self.executor_json_input = QPlainTextEdit()
        self.executor_json_input.setPlaceholderText(_t("executor_json_placeholder"))
        manual_layout.addWidget(self.executor_json_input)
        self.executor_run_btn = QPushButton(_t("executor_run"))
        self.executor_run_btn.clicked.connect(self._on_executor_run)
        manual_layout.addWidget(self.executor_run_btn)
        group_manual.setLayout(manual_layout)
        layout.addWidget(group_manual)

        # File execution
        group_file = QGroupBox(_t("executor_file_path"))
        file_layout = QHBoxLayout()
        self.executor_file_input = QLineEdit()
        file_layout.addWidget(self.executor_file_input)
        browse_file_btn = QPushButton(_t("browse"))
        browse_file_btn.clicked.connect(self._on_executor_browse_file)
        file_layout.addWidget(browse_file_btn)
        self.executor_run_file_btn = QPushButton(_t("executor_run_file"))
        self.executor_run_file_btn.clicked.connect(self._on_executor_run_file)
        file_layout.addWidget(self.executor_run_file_btn)
        group_file.setLayout(file_layout)
        layout.addWidget(group_file)

        # Directory execution
        group_dir = QGroupBox(_t("executor_dir_path"))
        dir_layout = QHBoxLayout()
        self.executor_dir_input = QLineEdit()
        dir_layout.addWidget(self.executor_dir_input)
        browse_dir_btn = QPushButton(_t("browse"))
        browse_dir_btn.clicked.connect(self._on_executor_browse_dir)
        dir_layout.addWidget(browse_dir_btn)
        self.executor_run_dir_btn = QPushButton(_t("executor_run_dir"))
        self.executor_run_dir_btn.clicked.connect(self._on_executor_run_dir)
        dir_layout.addWidget(self.executor_run_dir_btn)
        group_dir.setLayout(dir_layout)
        layout.addWidget(group_dir)

        layout.addStretch()
        tab.setLayout(layout)
        self.main_tabs.addTab(tab, _t("tab_executor"))

    def _on_executor_run(self):
        text = self.executor_json_input.toPlainText().strip()
        if not text:
            return
        try:
            action_list = json.loads(text)
        except json.JSONDecodeError as e:
            api_testka_ui_queue.put(f"JSON parse error: {e}")
            return
        thread = ExecutorThread()
        thread.mode = "action"
        thread.action_list = action_list
        self._start_thread(thread)

    def _on_executor_browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select JSON File", "", _JSON_FILE_FILTER)
        if path:
            self.executor_file_input.setText(path)

    def _on_executor_run_file(self):
        path = self.executor_file_input.text().strip()
        if not path:
            return
        try:
            action_list = read_action_json(path)
        except Exception as e:
            api_testka_ui_queue.put(f"File read error: {e}")
            return
        thread = ExecutorThread()
        thread.mode = "action"
        thread.action_list = action_list
        self._start_thread(thread)

    def _on_executor_browse_dir(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if path:
            self.executor_dir_input.setText(path)

    def _on_executor_run_dir(self):
        path = self.executor_dir_input.text().strip()
        if not path:
            return
        try:
            files = get_dir_files_as_list(path)
            json_files = [f for f in files if f.endswith(".json")]
        except Exception as e:
            api_testka_ui_queue.put(f"Dir read error: {e}")
            return
        if not json_files:
            api_testka_ui_queue.put("No JSON files found in directory")
            return
        thread = ExecutorThread()
        thread.mode = "files"
        thread.file_list = json_files
        self._start_thread(thread)

    # ─── Reports Tab ───────────────────────────────────────────────

    def _build_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel(_t("report_file_name")))
        self.report_name_input = QLineEdit()
        self.report_name_input.setText(_t("report_file_name_default"))
        name_row.addWidget(self.report_name_input)
        layout.addLayout(name_row)

        btn_row = QHBoxLayout()
        html_btn = QPushButton(_t("report_generate_html"))
        html_btn.clicked.connect(lambda: self._on_generate_report("html"))
        btn_row.addWidget(html_btn)

        json_btn = QPushButton(_t("report_generate_json"))
        json_btn.clicked.connect(lambda: self._on_generate_report("json"))
        btn_row.addWidget(json_btn)

        xml_btn = QPushButton(_t("report_generate_xml"))
        xml_btn.clicked.connect(lambda: self._on_generate_report("xml"))
        btn_row.addWidget(xml_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        tab.setLayout(layout)
        self.main_tabs.addTab(tab, _t("tab_reports"))

    def _on_generate_report(self, report_type):
        thread = ReportThread()
        thread.report_type = report_type
        thread.file_name = self.report_name_input.text().strip() or "test_report"
        self._start_thread(thread)

    # ─── Mock Server Tab ───────────────────────────────────────────

    def _build_mock_server_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        form = QFormLayout()
        self.mock_host_input = QLineEdit("localhost")
        form.addRow(_t("mock_host"), self.mock_host_input)
        self.mock_port_input = QSpinBox()
        self.mock_port_input.setRange(1, 65535)
        self.mock_port_input.setValue(8090)
        form.addRow(_t("mock_port"), self.mock_port_input)
        layout.addLayout(form)

        self.mock_status_label = QLabel(_t("mock_status") + " " + _t("mock_status_stopped"))
        layout.addWidget(self.mock_status_label)

        self.mock_start_btn = QPushButton(_t("mock_start"))
        self.mock_start_btn.clicked.connect(self._on_mock_start)
        layout.addWidget(self.mock_start_btn)

        layout.addStretch()
        tab.setLayout(layout)
        self.main_tabs.addTab(tab, _t("tab_mock_server"))

    def _on_mock_start(self):
        thread = MockServerThread()
        thread.host = self.mock_host_input.text().strip()
        thread.port = self.mock_port_input.value()
        self.mock_status_label.setText(_t("mock_status") + " " + _t("mock_status_running"))
        self.mock_start_btn.setEnabled(False)
        self._start_thread(thread)

    # ─── Test Records Tab ──────────────────────────────────────────

    def _build_test_records_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.records_count_label = QLabel(
            _t("records_count").format(success=0, error=0)
        )
        layout.addWidget(self.records_count_label)

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton(_t("records_refresh"))
        refresh_btn.clicked.connect(self._on_records_refresh)
        btn_row.addWidget(refresh_btn)
        clean_btn = QPushButton(_t("records_clean"))
        clean_btn.clicked.connect(self._on_records_clean)
        btn_row.addWidget(clean_btn)
        layout.addLayout(btn_row)

        # Success records
        layout.addWidget(QLabel(_t("records_success")))
        self.success_records_text = QTextEdit()
        self.success_records_text.setReadOnly(True)
        layout.addWidget(self.success_records_text)

        # Error records
        layout.addWidget(QLabel(_t("records_error")))
        self.error_records_text = QTextEdit()
        self.error_records_text.setReadOnly(True)
        layout.addWidget(self.error_records_text)

        tab.setLayout(layout)
        self.main_tabs.addTab(tab, _t("tab_test_records"))

    def _on_records_refresh(self):
        success = test_record_instance.test_record_list
        error = test_record_instance.error_record_list
        self.records_count_label.setText(
            _t("records_count").format(success=len(success), error=len(error))
        )
        self.success_records_text.setPlainText(
            json.dumps(success, indent=2, default=str) if success else "[]"
        )
        self.error_records_text.setPlainText(
            json.dumps(error, indent=2, default=str) if error else "[]"
        )

    def _on_records_clean(self):
        test_record_instance.clean_record()
        self._on_records_refresh()
        api_testka_ui_queue.put("Test records cleaned")

    # ─── Tools Tab ─────────────────────────────────────────────────

    def _build_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # JSON Reformat
        json_group = QGroupBox(_t("tools_json_reformat"))
        json_layout = QVBoxLayout()
        json_layout.addWidget(QLabel(_t("tools_json_input")))
        self.tools_json_input = QPlainTextEdit()
        self.tools_json_input.setMaximumHeight(120)
        json_layout.addWidget(self.tools_json_input)

        json_btn_row = QHBoxLayout()
        format_btn = QPushButton(_t("tools_json_format_btn"))
        format_btn.clicked.connect(self._on_json_format)
        json_btn_row.addWidget(format_btn)
        read_btn = QPushButton(_t("tools_json_read"))
        read_btn.clicked.connect(self._on_json_read)
        json_btn_row.addWidget(read_btn)
        write_btn = QPushButton(_t("tools_json_write"))
        write_btn.clicked.connect(self._on_json_write)
        json_btn_row.addWidget(write_btn)
        json_layout.addLayout(json_btn_row)

        json_layout.addWidget(QLabel(_t("tools_json_output")))
        self.tools_json_output = QPlainTextEdit()
        self.tools_json_output.setReadOnly(True)
        self.tools_json_output.setMaximumHeight(120)
        json_layout.addWidget(self.tools_json_output)
        json_group.setLayout(json_layout)
        layout.addWidget(json_group)

        # XML Reformat
        xml_group = QGroupBox(_t("tools_xml_reformat"))
        xml_layout = QHBoxLayout()
        xml_layout.addWidget(QLabel(_t("tools_xml_input")))
        self.tools_xml_path_input = QLineEdit()
        xml_layout.addWidget(self.tools_xml_path_input)
        xml_browse_btn = QPushButton(_t("browse"))
        xml_browse_btn.clicked.connect(self._on_xml_browse)
        xml_layout.addWidget(xml_browse_btn)
        xml_reformat_btn = QPushButton(_t("tools_xml_reformat_btn"))
        xml_reformat_btn.clicked.connect(self._on_xml_reformat)
        xml_layout.addWidget(xml_reformat_btn)
        xml_group.setLayout(xml_layout)
        layout.addWidget(xml_group)

        # Create Project
        project_group = QGroupBox(_t("tools_create_project"))
        project_layout = QFormLayout()
        self.tools_project_path_input = QLineEdit()
        project_path_row = QHBoxLayout()
        project_path_row.addWidget(self.tools_project_path_input)
        project_browse_btn = QPushButton(_t("browse"))
        project_browse_btn.clicked.connect(self._on_project_browse)
        project_path_row.addWidget(project_browse_btn)
        project_layout.addRow(_t("tools_project_path"), project_path_row)

        self.tools_project_name_input = QLineEdit(_t("tools_project_name_default"))
        project_layout.addRow(_t("tools_project_name"), self.tools_project_name_input)

        project_create_btn = QPushButton(_t("tools_project_create_btn"))
        project_create_btn.clicked.connect(self._on_project_create)
        project_layout.addWidget(project_create_btn)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)

        layout.addStretch()
        tab.setLayout(layout)
        self.main_tabs.addTab(tab, _t("tab_tools"))

    def _on_json_format(self):
        text = self.tools_json_input.toPlainText().strip()
        if not text:
            return
        try:
            result = reformat_json(text)
            self.tools_json_output.setPlainText(result)
        except Exception as e:
            self.tools_json_output.setPlainText(f"Error: {e}")

    def _on_json_read(self):
        path, _ = QFileDialog.getOpenFileName(self, "Read JSON", "", _JSON_FILE_FILTER)
        if not path:
            return
        try:
            data = read_action_json(path)
            self.tools_json_input.setPlainText(json.dumps(data, indent=2, ensure_ascii=False))
        except Exception as e:
            api_testka_ui_queue.put(f"JSON read error: {e}")

    def _on_json_write(self):
        text = self.tools_json_input.toPlainText().strip()
        if not text:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Write JSON", "", _JSON_FILE_FILTER)
        if not path:
            return
        try:
            data = json.loads(text)
            write_action_json(path, data)
            api_testka_ui_queue.put(f"JSON written to {path}")
        except Exception as e:
            api_testka_ui_queue.put(f"JSON write error: {e}")

    def _on_xml_browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select XML", "", "XML Files (*.xml)")
        if path:
            self.tools_xml_path_input.setText(path)

    def _on_xml_reformat(self):
        from je_api_testka.utils.xml.xml_file.xml_file import reformat_xml_file
        path = self.tools_xml_path_input.text().strip()
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                xml_content = f.read()
            result = reformat_xml_file(xml_content)
            with open(path, "w", encoding="utf-8") as f:
                f.write(result)
            api_testka_ui_queue.put(f"XML reformatted: {path}")
        except Exception as e:
            api_testka_ui_queue.put(f"XML reformat error: {e}")

    def _on_project_browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if path:
            self.tools_project_path_input.setText(path)

    def _on_project_create(self):
        path = self.tools_project_path_input.text().strip() or None
        name = self.tools_project_name_input.text().strip() or "APITestka"
        try:
            create_project_dir(project_path=path, parent_name=name)
            api_testka_ui_queue.put(f"Project created: {name}")
        except Exception as e:
            api_testka_ui_queue.put(f"Project creation error: {e}")

    # ─── Common ────────────────────────────────────────────────────

    def _start_thread(self, thread):
        self._threads.append(thread)
        thread.finished.connect(lambda: self._threads.remove(thread) if thread in self._threads else None)
        thread.start()

    def pull_log(self):
        while not api_testka_ui_queue.empty():
            message = api_testka_ui_queue.get_nowait()
            self.log_panel.append(str(message))
