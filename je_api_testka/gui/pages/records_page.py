"""Records & Reports page: the shared test record as a table, and every report format."""
from __future__ import annotations

import json
from typing import Callable, Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from je_api_testka.diff.sla_check import record_latency_ms
from je_api_testka.gui.widgets import BasePage, form_group, log, monospace_view, plain_button, primary_button, tr
from je_api_testka.utils.generate_report.allure_report import generate_allure_report
from je_api_testka.utils.generate_report.html_report_generate import generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json_report
from je_api_testka.utils.generate_report.junit_report import generate_junit_report
from je_api_testka.utils.generate_report.markdown_report import generate_markdown_report
from je_api_testka.utils.generate_report.xml_report import generate_xml_report
from je_api_testka.utils.test_record.test_record_class import test_record_instance

COLUMNS = ("method", "url", "status", "time_ms")
REPORT_WRITERS: Dict[str, Callable[[str], object]] = {
    "HTML": generate_html_report,
    "JSON": generate_json_report,
    "XML": generate_xml_report,
    "JUnit": lambda name: generate_junit_report(f"{name}.xml"),
    "Markdown": lambda name: generate_markdown_report(f"{name}.md"),
    "Allure": lambda name: generate_allure_report(f"{name}-allure"),
}


def record_rows(records: List[dict]) -> List[List[str]]:
    """Return the table cells (method, URL, status, time) for success records."""
    rows = []
    for record in records:
        latency = record_latency_ms(record)
        rows.append([str(record.get("request_method") or ""), str(record.get("request_url") or ""),
                     str(record.get("status_code") or ""), "" if latency is None else f"{latency:.1f}"])
    return rows


class RecordsPage(BasePage):
    """Browse successes and failures, clear the record, and write reports."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_records"), tr("records_help"), parent)
        top = QHBoxLayout()
        self.count_label = QLabel()
        top.addWidget(self.count_label)
        top.addStretch(1)
        top.addWidget(plain_button(tr("refresh"), self.refresh))
        top.addWidget(plain_button(tr("clear_records"), self.clear_records))
        self.body.addLayout(top)
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels([tr(f"column_{name}") for name in COLUMNS])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.currentCellChanged.connect(lambda row, *_rest: self._show_detail(row))
        self.detail_view = monospace_view()
        self.failures_view = monospace_view(tr("no_failures"))
        splitter.addWidget(self.table)
        splitter.addWidget(self.detail_view)
        splitter.addWidget(self.failures_view)
        splitter.setMinimumHeight(420)
        self.body.addWidget(splitter, stretch=1)
        self.report_name = QLineEdit("test_report")
        buttons = [primary_button(name, lambda _checked=False, kind=name: self.write_report(kind))
                   for name in REPORT_WRITERS]
        self.body.addWidget(form_group(tr("reports"), [(tr("report_name"), self.report_name)], buttons))
        self.refresh()

    def refresh(self) -> None:
        """Reload the table and the failure list from the shared test record."""
        successes = list(test_record_instance.test_record_list)
        failures = list(test_record_instance.error_record_list)
        self.count_label.setText(tr("records_count").format(success=len(successes), error=len(failures)))
        rows = record_rows(successes)
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column, value in enumerate(row):
                self.table.setItem(row_index, column, QTableWidgetItem(value))
        self.failures_view.setPlainText("\n\n".join(json.dumps(entry, indent=2, default=str) for entry in failures))
        self.detail_view.clear()

    def _show_detail(self, row: int) -> None:
        records = test_record_instance.test_record_list
        if 0 <= row < len(records):
            self.detail_view.setPlainText(json.dumps(records[row], indent=2, default=str, ensure_ascii=False))

    def clear_records(self) -> None:
        """Empty the shared test record."""
        test_record_instance.clean_record()
        self.refresh()
        log(tr("records_cleared"))

    def write_report(self, kind: str) -> None:
        """Write the ``kind`` report named after the report-name box."""
        name = self.report_name.text().strip() or "test_report"
        self.run_task(lambda: REPORT_WRITERS[kind](name),
                      lambda _result: log(tr("report_written").format(kind=kind, name=name)))
