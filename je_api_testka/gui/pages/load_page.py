"""Load test page: run APITestka requests as a LoadDensity load test."""
from __future__ import annotations

import json
from typing import Optional

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QLineEdit, QSpinBox, QWidget

from je_api_testka.gui.widgets import BasePage, FileField, form_group, monospace_view, primary_button, tr
from je_api_testka.integrations.load_density import LOAD_USERS, TASK_MODES, LoadProfile, build_load_test
from je_api_testka.integrations.load_density_commands import load_plan
from je_api_testka.integrations.load_density_runner import LoadThresholds, run_load_test

_MAX_USERS: int = 100000
_MAX_SECONDS: int = 86400
_MAX_P95_MS: float = 600000.0


def load_test_text(action_file: str, profile: LoadProfile, thresholds: LoadThresholds, python: str = "") -> str:
    """Run the load test (action file, or the shared test record) and return the result as JSON text."""
    plan = load_plan(action_file or None)
    result = run_load_test(build_load_test(plan.tasks, profile), thresholds, python=python or None)
    return json.dumps({**result.to_dict(), "skipped": plan.skipped}, indent=2, ensure_ascii=False)


def _spin(maximum: int, value: int) -> QSpinBox:
    spin = QSpinBox()
    spin.setRange(1, maximum)
    spin.setValue(value)
    return spin


class LoadPage(BasePage):
    """Profile, limits and the interpreter that has LoadDensity installed."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_load"), tr("load_help"), parent)
        self.actions_field = FileField()
        self.user_combo = QComboBox()
        for user in LOAD_USERS:
            self.user_combo.addItem(user, user)
        self.mode_combo = QComboBox()
        for mode in TASK_MODES:
            self.mode_combo.addItem(mode, mode)
        self.users_spin = _spin(_MAX_USERS, 10)
        self.spawn_spin = _spin(_MAX_USERS, 5)
        self.time_spin = _spin(_MAX_SECONDS, 30)
        self.failure_spin = QDoubleSpinBox()
        self.failure_spin.setRange(0.0, 1.0)
        self.failure_spin.setSingleStep(0.01)
        self.failure_spin.setValue(1.0)
        self.p95_spin = QDoubleSpinBox()
        self.p95_spin.setRange(0.0, _MAX_P95_MS)
        self.p95_spin.setSpecialValueText(tr("no_limit"))
        self.python_input = QLineEdit()
        self.python_input.setPlaceholderText(tr("python_placeholder"))
        self.run_button = primary_button(tr("run_load_test"), self.run_load)
        self.body.addWidget(form_group(tr("load_profile"), [
            (tr("action_file_or_records"), self.actions_field), (tr("load_user"), self.user_combo),
            (tr("users"), self.users_spin), (tr("spawn_rate"), self.spawn_spin), (tr("seconds"), self.time_spin),
            (tr("task_mode"), self.mode_combo), (tr("max_failure_rate"), self.failure_spin),
            (tr("max_p95_ms"), self.p95_spin), (tr("python"), self.python_input),
        ], [self.run_button]))
        self.result_view = monospace_view()
        self.result_view.setMinimumHeight(220)
        self.body.addWidget(self.result_view, stretch=1)

    def run_load(self) -> None:
        """Run the load test in the background and show LoadDensity's summary."""
        profile = LoadProfile(self.user_combo.currentData(), self.users_spin.value(), self.spawn_spin.value(),
                              self.time_spin.value(), self.mode_combo.currentData())
        thresholds = LoadThresholds(self.failure_spin.value(), self.p95_spin.value() or None)
        action_file, python = self.actions_field.path(), self.python_input.text().strip()
        self.run_button.setEnabled(False)
        task = self.run_task(lambda: load_test_text(action_file, profile, thresholds, python),
                             lambda text: self.result_view.setPlainText(str(text)),
                             self.result_view.setPlainText)
        task.finished.connect(lambda: self.run_button.setEnabled(True))
