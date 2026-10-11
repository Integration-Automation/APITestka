"""
The embeddable APITestka GUI.

:class:`APITestkaWidget` is a sidebar of pages (one per feature) above a console
that shows the log queue. It takes no required arguments, which PyBreeze relies
on when it embeds it (``architecture.md`` §6); the standalone window
:class:`~je_api_testka.gui.main_window.APITestkaUI` adds menus and a theme.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QPlainTextEdit,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from je_api_testka.gui.env_manager_model import EnvManagerModel
from je_api_testka.gui.history_panel import HistoryPanelModel
from je_api_testka.gui.message_queue import api_testka_ui_queue
from je_api_testka.gui.pages.contract_page import ContractPage
from je_api_testka.gui.pages.environment_page import EnvironmentPage
from je_api_testka.gui.pages.executor_page import ExecutorPage
from je_api_testka.gui.pages.load_page import LoadPage
from je_api_testka.gui.pages.mock_page import MockPage
from je_api_testka.gui.pages.openapi_page import OpenAPIPage
from je_api_testka.gui.pages.records_page import RecordsPage
from je_api_testka.gui.pages.request_page import RequestPage
from je_api_testka.gui.pages.tools_page import ToolsPage
from je_api_testka.gui.pages.trends_page import TrendsPage
from je_api_testka.gui.widgets import muted_label, plain_button, tr

PAGE_KEYS = ("page_request", "page_environments", "page_executor", "page_records", "page_mock",
             "page_contracts", "page_openapi", "page_load", "page_trends", "page_tools")
SIDEBAR_WIDTH: int = 190
LOG_POLL_MS: int = 50
MAX_CONSOLE_BLOCKS: int = 5000


class APITestkaWidget(QWidget):
    """Sidebar navigation over the feature pages, with the console underneath."""

    def __init__(self, parent: Optional[QWidget] = None, *, history: Optional[HistoryPanelModel] = None,
                 environments: Optional[EnvManagerModel] = None) -> None:
        """
        :param history: request history to show and extend (default: a new, empty one).
        :param environments: environments to edit and use (default: a new, empty set). The standalone window
            passes the same two models to every rebuild, so a language switch keeps them.
        """
        super().__init__(parent)
        self.history = history if history is not None else HistoryPanelModel()
        self.environments = environments if environments is not None else EnvManagerModel()
        self.pages: Dict[str, QWidget] = self._build_pages()
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(SIDEBAR_WIDTH)
        self.sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.stack = QStackedWidget()
        for key in PAGE_KEYS:
            self.sidebar.addItem(tr(key))
            self.stack.addWidget(self.pages[key])
        self.sidebar.currentRowChanged.connect(self._show_row)
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(self.stack)
        splitter.addWidget(self._build_console())
        splitter.setSizes([640, 160])
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar)
        layout.addWidget(splitter, stretch=1)
        self.pages["page_environments"].changed.connect(self.pages["page_request"].refresh_environments)
        self.sidebar.setCurrentRow(0)
        self.pull_log_timer = QTimer(self)
        self.pull_log_timer.setInterval(LOG_POLL_MS)
        self.pull_log_timer.timeout.connect(self.pull_log)
        self.pull_log_timer.start()

    def _build_pages(self) -> Dict[str, QWidget]:
        return {
            "page_request": RequestPage(self.history, self.environments),
            "page_environments": EnvironmentPage(self.environments),
            "page_executor": ExecutorPage(),
            "page_records": RecordsPage(),
            "page_mock": MockPage(),
            "page_contracts": ContractPage(),
            "page_openapi": OpenAPIPage(),
            "page_load": LoadPage(),
            "page_trends": TrendsPage(),
            "page_tools": ToolsPage(),
        }

    def _build_console(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 4, 16, 8)
        header = QHBoxLayout()
        header.addWidget(muted_label(tr("console")))
        header.addStretch(1)
        self.console = QPlainTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(MAX_CONSOLE_BLOCKS)
        header.addWidget(plain_button(tr("clear"), self.console.clear))
        layout.addLayout(header)
        layout.addWidget(self.console)
        return panel

    def _show_row(self, row: int) -> None:
        self.stack.setCurrentIndex(row)
        page = self.stack.currentWidget()
        refresh = getattr(page, "refresh", None)
        if callable(refresh):
            refresh()

    def show_page(self, key: str) -> None:
        """Switch to the page named by ``key`` (one of :data:`PAGE_KEYS`)."""
        self.sidebar.setCurrentRow(PAGE_KEYS.index(key))

    def page_titles(self) -> List[str]:
        """Return the sidebar labels in order."""
        return [self.sidebar.item(row).text() for row in range(self.sidebar.count())]

    def pull_log(self) -> None:
        """Move queued log messages into the console."""
        while not api_testka_ui_queue.empty():
            self.console.appendPlainText(str(api_testka_ui_queue.get_nowait()))
