"""Mock servers page: the HTTP mock, and HTTP + WebSocket + gRPC endpoints from a config file."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

from PySide6.QtWidgets import QLabel, QLineEdit, QSpinBox, QWidget

from je_api_testka.gui.widgets import BasePage, FileField, form_group, log, plain_button, primary_button, tr
from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer
from je_api_testka.utils.mock_server.mock_config import apply_mock_config, read_mock_config, stop_protocol_mocks

DEFAULT_MOCK_HOST: str = "127.0.0.1"
DEFAULT_MOCK_PORT: int = 8090
_MAX_PORT: int = 65535
# HTTP mocks serving in this process. They outlive the page (a language switch rebuilds it), so a rebuilt
# page still shows them; an entry goes when its server stops or fails to start.
_serving: List[Tuple[str, int]] = []


def start_mock(host: str, port: int, config_path: str = "") -> FlaskMockServer:
    """Configure a mock (from ``config_path`` when given), then serve HTTP until the process ends."""
    server = FlaskMockServer(host, port)
    if config_path:
        endpoints = apply_mock_config(read_mock_config(config_path), server,
                                      base_dir=str(Path(config_path).resolve().parent))
        for kind, address in endpoints.items():
            log(f"{kind}: {address}")
    log(tr("mock_listening").format(host=host, port=port))
    _serving.append((host, port))
    try:
        server.start_mock_server()
    finally:
        _serving.remove((host, port))
    return server


class MockPage(BasePage):
    """Start the Flask mock, optionally with WebSocket and gRPC endpoints from a mock config file."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(tr("page_mock"), tr("mock_help"), parent)
        self.host_input = QLineEdit(DEFAULT_MOCK_HOST)
        self.port_input = QSpinBox()
        self.port_input.setRange(1, _MAX_PORT)
        self.port_input.setValue(DEFAULT_MOCK_PORT)
        self.config_field = FileField()
        self.status_label = QLabel(tr("mock_stopped"))
        self.start_button = primary_button(tr("start"), self.start)
        self.body.addWidget(form_group(tr("http_mock"), [
            (tr("host"), self.host_input), (tr("port"), self.port_input),
            (tr("mock_config_file"), self.config_field), (tr("status"), self.status_label),
        ], [plain_button(tr("stop_protocol_mocks"), self.stop_protocol_mocks), self.start_button]))
        self.body.addStretch(1)
        if _serving:
            host, port = _serving[-1]
            self.start_button.setEnabled(False)
            self.status_label.setText(tr("mock_running").format(host=host, port=port))

    def start(self) -> None:
        """Start the mock in the background; the Flask server then runs until the application exits."""
        host, port, config_path = self.host_input.text().strip(), self.port_input.value(), self.config_field.path()
        self.start_button.setEnabled(False)
        self.status_label.setText(tr("mock_running").format(host=host, port=port))
        self.run_task(lambda: start_mock(host, port, config_path), lambda _server: None, self._failed)

    def _failed(self, message: str) -> None:
        self.start_button.setEnabled(True)
        self.status_label.setText(tr("mock_stopped"))
        log(f"{tr('error')}: {message}")

    def stop_protocol_mocks(self) -> None:
        """Stop the WebSocket and gRPC mocks started from the config file."""
        stop_protocol_mocks()
        log(tr("protocol_mocks_stopped"))
