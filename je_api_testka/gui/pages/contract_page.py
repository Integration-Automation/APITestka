"""Contracts page: record a consumer contract, verify it against a provider, compare it with OpenAPI."""
from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QComboBox, QLineEdit, QWidget

from je_api_testka.contract.commands import read_openapi, write_contract
from je_api_testka.contract.openapi_compat import check_pact_against_openapi
from je_api_testka.contract.pact import BODY_RULE_EQUALITY, BODY_RULE_TYPE, read_pact
from je_api_testka.contract.verifier import ProviderTarget, verify_pact
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


class ContractPage(BasePage):
    """The three contract steps, with their report below."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_contracts"), tr("contracts_help"), parent)
        self.consumer_input = QLineEdit("web")
        self.provider_input = QLineEdit("api")
        self.body_rule = QComboBox()
        self.body_rule.addItem(tr("body_rule_type"), BODY_RULE_TYPE)
        self.body_rule.addItem(tr("body_rule_equality"), BODY_RULE_EQUALITY)
        self.output_field = FileField(SAVE_FILE, text="pacts/contract.json")
        self.body.addWidget(form_group(tr("record_contract"), [
            (tr("consumer"), self.consumer_input), (tr("provider"), self.provider_input),
            (tr("body_rule"), self.body_rule), (tr("contract_file"), self.output_field),
        ], [primary_button(tr("record_from_records"), self.record)]))
        self.contract_field = FileField()
        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("http://localhost:8000")
        self.states_url_input = QLineEdit()
        self.openapi_field = FileField()
        self.body.addWidget(form_group(tr("check_contract"), [
            (tr("contract_file"), self.contract_field), (tr("provider_base_url"), self.base_url_input),
            (tr("provider_states_url"), self.states_url_input), (tr("openapi_file"), self.openapi_field),
        ], [primary_button(tr("verify_provider"), self.verify), primary_button(tr("compare_openapi"), self.compare)]))
        self.report_view = monospace_view()
        self.report_view.setMinimumHeight(200)
        self.body.addWidget(self.report_view, stretch=1)

    def record(self) -> None:
        """Write a contract from the shared test record."""
        output = self.output_field.path()
        consumer, provider = self.consumer_input.text().strip(), self.provider_input.text().strip()
        rule = self.body_rule.currentData()
        self.run_task(lambda: write_contract(output, consumer, provider, body_rule=rule),
                      lambda path: log(tr("written").format(path=path)))

    def verify(self) -> None:
        """Replay the contract against the provider and show the report."""
        contract, base_url = self.contract_field.path(), self.base_url_input.text().strip()
        target = ProviderTarget(base_url, provider_states_url=self.states_url_input.text().strip() or None)
        self.run_task(lambda: verify_pact(read_pact(contract), target).render_text(), self._show)

    def compare(self) -> None:
        """Check the contract against the provider's OpenAPI document and show the report."""
        contract, openapi = self.contract_field.path(), self.openapi_field.path()
        self.run_task(lambda: check_pact_against_openapi(read_pact(contract), read_openapi(openapi)).render_text(),
                      self._show)

    def _show(self, text: object) -> None:
        self.report_view.setPlainText(str(text))
