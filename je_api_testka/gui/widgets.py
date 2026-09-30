"""
Small Qt building blocks shared by the GUI pages.

* :func:`tr` looks a key up in the active language.
* :class:`TaskThread` runs a callable off the UI thread and reports back with signals.
* :class:`FileField`, :func:`page_title`, :func:`primary_button`, :func:`monospace_view`
  and :func:`form_group` keep the page modules short and consistent.
* :class:`BasePage` gives every page a title, a scrollable body and ``run_task``.
"""
from __future__ import annotations

import traceback
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.message_queue import api_testka_ui_queue
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

JSON_FILTER: str = "JSON (*.json)"
ANY_FILTER: str = "All files (*)"
OPEN_FILE: str = "open"
SAVE_FILE: str = "save"
DIRECTORY: str = "directory"


def tr(key: str) -> str:
    """Return the active language's text for ``key`` (the key itself when missing)."""
    return language_wrapper.language_word_dict.get(key, key)


def log(message: str) -> None:
    """Append ``message`` to the console panel."""
    api_testka_ui_queue.put(message)


class TaskThread(QThread):
    """Run ``function`` in a worker thread; ``succeeded`` carries its result, ``failed`` the error text."""

    succeeded = Signal(object)
    failed = Signal(str)

    def __init__(self, function: Callable[[], object], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._function = function

    def run(self) -> None:
        # A worker must never die silently: every error is logged and handed back to the page.
        try:
            result = self._function()
        except Exception as error:  # noqa: BLE001 - reported to the UI and the log below
            apitestka_logger.error(f"GUI task failed: {error!r}\n{traceback.format_exc()}")
            self.failed.emit(str(error) or repr(error))
            return
        self.succeeded.emit(result)


class FileField(QWidget):
    """A path box with a browse button (``open``, ``save`` or ``directory`` mode)."""

    def __init__(self, mode: str = OPEN_FILE, file_filter: str = JSON_FILTER, text: str = "",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._mode = mode
        self._filter = file_filter
        self.line_edit = QLineEdit(text)
        browse = QPushButton(tr("browse"))
        browse.clicked.connect(self._browse)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit, stretch=1)
        layout.addWidget(browse)

    def path(self) -> str:
        """Return the entered path, stripped."""
        return self.line_edit.text().strip()

    def _browse(self) -> None:
        if self._mode == DIRECTORY:
            chosen = QFileDialog.getExistingDirectory(self, tr("browse"), self.path())
        elif self._mode == SAVE_FILE:
            chosen, _selected = QFileDialog.getSaveFileName(self, tr("browse"), self.path(), self._filter)
        else:
            chosen, _selected = QFileDialog.getOpenFileName(self, tr("browse"), self.path(), self._filter)
        if chosen:
            self.line_edit.setText(chosen)


def page_title(text: str) -> QLabel:
    """Return a page heading label."""
    label = QLabel(text)
    label.setObjectName("pageTitle")
    return label


def muted_label(text: str) -> QLabel:
    """Return a secondary-text label that wraps."""
    label = QLabel(text)
    label.setProperty("role", "muted")
    label.setWordWrap(True)
    return label


def primary_button(text: str, handler: Callable[[], None]) -> QPushButton:
    """Return an accent button wired to ``handler``."""
    button = QPushButton(text)
    button.setProperty("role", "primary")
    button.clicked.connect(handler)
    return button


def plain_button(text: str, handler: Callable[[], None]) -> QPushButton:
    """Return a normal button wired to ``handler``."""
    button = QPushButton(text)
    button.clicked.connect(handler)
    return button


def code_editor(placeholder: str = "") -> QPlainTextEdit:
    """Return an editable monospaced text box, e.g. for JSON."""
    editor = QPlainTextEdit()
    editor.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
    editor.setPlaceholderText(placeholder)
    return editor


def monospace_view(placeholder: str = "") -> QPlainTextEdit:
    """Return a read-only monospaced text box for reports and responses."""
    view = code_editor(placeholder)
    view.setReadOnly(True)
    return view


def form_group(title: str, rows: Sequence[Tuple[str, QWidget]], buttons: Iterable[QPushButton] = ()) -> QGroupBox:
    """Return a titled group with labelled rows and a right-aligned button row."""
    group = QGroupBox(title)
    form = QFormLayout(group)
    for label, widget in rows:
        form.addRow(label, widget)
    button_list: List[QPushButton] = list(buttons)
    if button_list:
        row = QHBoxLayout()
        row.addStretch(1)
        for button in button_list:
            row.addWidget(button)
        form.addRow(row)
    return group


class BasePage(QWidget):
    """A page with a title, an optional description and a scrollable body layout (``self.body``)."""

    def __init__(self, title: str, description: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._tasks: List[TaskThread] = []
        content = QWidget()
        self.body = QVBoxLayout(content)
        self.body.addWidget(page_title(title))
        if description:
            self.body.addWidget(muted_label(description))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 12, 16, 12)
        outer.addWidget(scroll)

    def run_task(self, function: Callable[[], object], on_success: Callable[[object], None],
                 on_failure: Optional[Callable[[str], None]] = None) -> TaskThread:
        """Run ``function`` in the background and call back on the UI thread."""
        task = TaskThread(function, self)
        task.succeeded.connect(on_success)
        task.failed.connect(on_failure or (lambda message: log(f"{tr('error')}: {message}")))
        task.finished.connect(lambda: self._tasks.remove(task) if task in self._tasks else None)
        self._tasks.append(task)
        task.start()
        return task
