"""OpenAPI page: infer a document from the record, run the test-as-spec check, generate tests."""
from __future__ import annotations

import json
from typing import Optional

from PySide6.QtWidgets import QComboBox, QDoubleSpinBox, QLineEdit, QWidget

from je_api_testka.ai.backend import BACKEND_NAMES, select_ai_backend
from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.contract.commands import read_openapi
from je_api_testka.gui.widgets import (
    SAVE_FILE,
    BasePage,
    FileField,
    form_group,
    log,
    monospace_view,
    primary_button,
    tr,
)
from je_api_testka.spec.openapi_export import export_openapi
from je_api_testka.spec.spec_loop import check_records_against_spec, missing_test_actions, write_json_document
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def spec_check_text(spec_path: str, min_coverage: float, missing_actions_path: str = "") -> str:
    """Run the test-as-spec check on the shared test record and return the text report."""
    spec = read_openapi(spec_path)
    report = check_records_against_spec(list(test_record_instance.test_record_list), spec)
    if missing_actions_path:
        write_json_document(missing_actions_path, missing_test_actions(spec, report))
    return report.render_text(min_coverage)


def generated_tests(spec_path: str, backend: str, output_path: str = "") -> str:
    """Generate test actions for a document with the chosen AI backend; return them as JSON text."""
    select_ai_backend(backend)
    actions = generate_tests_from_openapi(read_openapi(spec_path))
    if output_path:
        write_json_document(output_path, actions)
    return json.dumps(actions, indent=2, ensure_ascii=False)


class OpenAPIPage(BasePage):
    """Spec inference, the test-as-spec check and test generation."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_openapi"), tr("openapi_help"), parent)
        self.title_input = QLineEdit("APITestka Inferred")
        self.export_field = FileField(SAVE_FILE, text="openapi.inferred.json")
        self.body.addWidget(form_group(tr("infer_openapi"), [
            (tr("title"), self.title_input), (tr("output_file"), self.export_field),
        ], [primary_button(tr("export"), self.export)]))
        self.spec_field = FileField()
        self.coverage_spin = QDoubleSpinBox()
        self.coverage_spin.setRange(0.0, 1.0)
        self.coverage_spin.setSingleStep(0.05)
        self.missing_field = FileField(SAVE_FILE)
        self.backend_combo = QComboBox()
        for name in BACKEND_NAMES:
            self.backend_combo.addItem(name, name)
        self.body.addWidget(form_group(tr("spec_and_tests"), [
            (tr("openapi_file"), self.spec_field), (tr("min_coverage"), self.coverage_spin),
            (tr("missing_actions_file"), self.missing_field), (tr("ai_backend"), self.backend_combo),
        ], [primary_button(tr("check_spec"), self.check), primary_button(tr("generate_tests"), self.generate)]))
        self.report_view = monospace_view()
        self.report_view.setMinimumHeight(220)
        self.body.addWidget(self.report_view, stretch=1)

    def export(self) -> None:
        """Write the document inferred from the shared test record."""
        output, title = self.export_field.path(), self.title_input.text().strip()
        self.run_task(lambda: export_openapi(output, title=title), lambda path: log(tr("written").format(path=path)))

    def check(self) -> None:
        """Check the committed document against the shared test record."""
        spec, coverage, missing = self.spec_field.path(), self.coverage_spin.value(), self.missing_field.path()
        self.run_task(lambda: spec_check_text(spec, coverage, missing), self._show)

    def generate(self) -> None:
        """Generate test actions for the document."""
        spec, backend, output = self.spec_field.path(), self.backend_combo.currentData(), self.missing_field.path()
        self.run_task(lambda: generated_tests(spec, backend, output), self._show)

    def _show(self, text: object) -> None:
        self.report_view.setPlainText(str(text))
