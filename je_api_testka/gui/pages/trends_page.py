"""Trends page: record this run's per-endpoint latencies, judge them, open the trend report."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QLineEdit, QTableWidget, QTableWidgetItem, QWidget

from je_api_testka.gui.widgets import SAVE_FILE, BasePage, FileField, form_group, log, primary_button, tr
from je_api_testka.utils.generate_report.latency_trends import (
    EndpointVerdict,
    detect_latency_anomalies,
    record_endpoint_latencies,
)
from je_api_testka.utils.generate_report.trend_report import DEFAULT_TREND_REPORT, generate_trend_report
from je_api_testka.utils.generate_report.trend_store import DEFAULT_TREND_DB

VERDICT_COLUMNS = ("endpoint", "latest", "baseline", "z", "status")


def verdict_rows(verdicts: List[EndpointVerdict]) -> List[List[str]]:
    """Return the table cells for each verdict."""
    def number(value: Optional[float]) -> str:
        return "" if value is None else f"{value:.1f}"
    return [[item.endpoint, number(item.latest), number(item.baseline_median), number(item.robust_z), item.status]
            for item in verdicts]


class TrendsPage(BasePage):
    """Latency history per endpoint, with the anomaly verdicts in a table."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_trends"), tr("trends_help"), parent)
        self.db_field = FileField(SAVE_FILE, "SQLite (*.sqlite *.db)", DEFAULT_TREND_DB)
        self.label_input = QLineEdit()
        self.label_input.setPlaceholderText("build-128")
        self.report_field = FileField(SAVE_FILE, "HTML (*.html)", DEFAULT_TREND_REPORT)
        self.body.addWidget(form_group(tr("trend_database"), [
            (tr("database"), self.db_field), (tr("run_label"), self.label_input),
            (tr("report_file"), self.report_field),
        ], [primary_button(tr("record_run"), self.record), primary_button(tr("check_anomalies"), self.check),
            primary_button(tr("open_report"), self.open_report)]))
        self.table = QTableWidget(0, len(VERDICT_COLUMNS))
        self.table.setHorizontalHeaderLabels([tr(f"column_{name}") for name in VERDICT_COLUMNS])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(240)
        self.body.addWidget(self.table, stretch=1)

    def record(self) -> None:
        """Store the shared test record's latencies as one run."""
        db, label = self.db_field.path(), self.label_input.text().strip()
        self.run_task(lambda: record_endpoint_latencies(db, label),
                      lambda result: log(tr("run_recorded").format(**result)))

    def check(self) -> None:
        """Judge the latest run and fill the table."""
        db = self.db_field.path()
        self.run_task(lambda: detect_latency_anomalies(db), self._fill)

    def _fill(self, verdicts: object) -> None:
        rows = verdict_rows(list(verdicts or []))
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for column, value in enumerate(row):
                self.table.setItem(row_index, column, QTableWidgetItem(value))

    def open_report(self) -> None:
        """Write the HTML trend report and open it in the browser."""
        output, db = self.report_field.path(), self.db_field.path()
        self.run_task(lambda: generate_trend_report(output, db),
                      lambda path: QDesktopServices.openUrl(QUrl.fromLocalFile(str(Path(str(path)).resolve()))))
