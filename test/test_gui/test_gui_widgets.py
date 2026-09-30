"""Offscreen tests of the redesigned GUI: shell, pages, languages and themes."""
from __future__ import annotations

import json
import os
import time

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from je_api_testka.data.variable_store import variable_store  # noqa: E402
from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper  # noqa: E402
from je_api_testka.gui.main_widget import PAGE_KEYS, APITestkaWidget  # noqa: E402
from je_api_testka.gui.main_window import APITestkaUI  # noqa: E402
from je_api_testka.gui.message_queue import api_testka_ui_queue  # noqa: E402
from je_api_testka.gui.pages.executor_page import format_results  # noqa: E402
from je_api_testka.gui.pages.openapi_page import generated_tests, spec_check_text  # noqa: E402
from je_api_testka.gui.pages.records_page import record_rows  # noqa: E402
from je_api_testka.gui.pages.trends_page import verdict_rows  # noqa: E402
from je_api_testka.utils.generate_report.latency_trends import EndpointVerdict  # noqa: E402
from je_api_testka.utils.test_record.test_record_class import test_record_instance  # noqa: E402

WAIT_MS = 15000


@pytest.fixture(scope="module")
def qapp():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


@pytest.fixture
def widget(qapp):
    created = APITestkaWidget()
    yield created
    created.deleteLater()
    qapp.processEvents()


def _finish(qapp, task) -> None:
    assert task.wait(WAIT_MS)
    qapp.processEvents()


def _wait_until(qapp, predicate) -> bool:
    deadline = time.monotonic() + WAIT_MS / 1000
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        time.sleep(0.02)
    return False


def test_shell_has_every_page_and_switches(widget):
    assert widget.page_titles()[0] == "Request"
    assert widget.stack.count() == len(PAGE_KEYS)
    for key in PAGE_KEYS:
        widget.show_page(key)
        assert widget.stack.currentWidget() is widget.pages[key]


def test_console_drains_the_queue(widget):
    api_testka_ui_queue.put("hello console")
    widget.pull_log()
    assert "hello console" in widget.console.toPlainText()


def test_request_page_sends_and_records_history(qapp, widget, mock_url):
    page = widget.pages["page_request"]
    page.url_input.setText(f"{mock_url}/get")
    page.params_input.setPlainText('{"q": "1"}')
    page.send()
    _finish(qapp, page._task)
    assert page.status_label.text() == "200"
    assert page.status_label.property("status") == "success"
    assert '"q": "1"' in page.response_body.toPlainText()
    assert page.history_list.count() == 1
    page.url_input.clear()
    page._load_history_item(page.history_list.item(0))
    assert page.url_input.text() == f"{mock_url}/get"


def test_request_page_reports_bad_json_and_failures(qapp, widget, mock_url):
    page = widget.pages["page_request"]
    page.headers_input.setPlainText("{nope")
    page.send()
    assert page.status_label.property("status") == "server-error"
    assert "Headers: not valid JSON" in page.response_body.toPlainText()
    page.headers_input.clear()
    page.url_input.setText(f"{mock_url}/missing")
    page.backend_combo.setCurrentIndex(page.backend_combo.findData("requests"))
    page.send()
    _finish(qapp, page._task)
    assert page.status_label.text() == "Request failed"


def test_copy_as_action(qapp, widget):
    page = widget.pages["page_request"]
    page.url_input.setText("https://api.invalid/items")
    page.body_input.setPlainText('{"a": 1}')
    page.copy_as_action()
    action = json.loads(QtWidgets.QApplication.clipboard().text())
    assert action[0] == "AT_test_api_method"
    assert action[1]["json"] == {"a": 1}


def test_environments_feed_the_request_page(widget):
    environments = widget.environments
    environments.upsert("staging", {"base": "https://staging.invalid"})
    env_page, request_page = widget.pages["page_environments"], widget.pages["page_request"]
    env_page._reload("staging")
    assert request_page.environment_combo.findData("staging") > 0
    env_page._activate()
    try:
        assert variable_store.get("base") == "https://staging.invalid"
    finally:
        variable_store.clear()


def test_records_page_lists_the_record(widget):
    test_record_instance.test_record_list.append(
        {"request_method": "GET", "request_url": "https://api.invalid/a", "status_code": 200,
         "request_time_sec": 0.0123})
    page = widget.pages["page_records"]
    widget.show_page("page_records")
    assert page.table.rowCount() == 1
    assert page.table.item(0, 3).text() == "12.3"
    assert "1 succeeded" in page.count_label.text()
    page.clear_records()
    assert page.table.rowCount() == 0


def test_executor_page_runs_typed_actions(qapp, widget):
    page = widget.pages["page_executor"]
    page.actions_editor.setPlainText('[["AT_fake_uuid"]]')
    page.run_typed()
    assert _wait_until(qapp, lambda: "AT_fake_uuid" in page.results_view.toPlainText())


def test_page_helpers():
    assert format_results({"execute: ['AT_x']": 1}) == "execute: ['AT_x']\n  => 1"
    rows = record_rows([{"request_method": "POST", "request_url": "u", "status_code": 201}])
    assert rows == [["POST", "u", "201", ""]]
    verdict = EndpointVerdict("GET /a", "p95_ms", 12.0, None, None, 2, "insufficient_history")
    assert verdict_rows([verdict]) == [["GET /a", "12.0", "", "", "insufficient_history"]]


def test_openapi_page_helpers(tmp_path):
    spec = tmp_path / "openapi.json"
    spec.write_text(json.dumps({"servers": [{"url": "https://api.invalid"}],
                                "paths": {"/a": {"get": {"responses": {"200": {}}}}}}), encoding="utf-8")
    assert "[UNTESTED] GET /a" in spec_check_text(str(spec), 0.0, str(tmp_path / "missing.json"))
    assert json.loads((tmp_path / "missing.json").read_text(encoding="utf-8"))[0][1]["test_url"] == "https://api.invalid/a"
    assert json.loads(generated_tests(str(spec), "noop"))[0][0] == "AT_test_api_method"


def test_window_languages_and_themes(qapp):
    window = APITestkaUI(theme="light")
    try:
        assert "#f6f8fa" in window.styleSheet()
        window.apply_theme("dark")
        assert "#0d1117" in window.styleSheet()
        for language, first_page in (("Traditional_Chinese", "請求"), ("Simplified_Chinese", "请求"),
                                     ("Japanese", "リクエスト")):
            window.switch_language(language)
            assert window.api_testka_widget.page_titles()[0] == first_page
        assert [action.text() for action in window.menuBar().actions()] == ["言語", "テーマ"]
    finally:
        language_wrapper.reset_language("English")
        window.deleteLater()
        qapp.processEvents()
