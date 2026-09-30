"""
Standalone APITestka window: the embeddable widget plus Language and Theme menus.

Run with ``python -m je_api_testka.gui.main_window``.
"""
from __future__ import annotations

import sys
from typing import Optional

from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.main_widget import APITestkaWidget
from je_api_testka.gui.theme import THEME_DARK, THEME_LIGHT, THEME_SYSTEM, build_stylesheet, resolve_theme
from je_api_testka.gui.widgets import tr

LANGUAGES = (("English", "menu_language_english"), ("Traditional_Chinese", "menu_language_traditional_chinese"),
             ("Simplified_Chinese", "menu_language_simplified_chinese"), ("Japanese", "menu_language_japanese"))
THEME_CHOICES = ((THEME_SYSTEM, "menu_theme_system"), (THEME_LIGHT, "menu_theme_light"),
                 (THEME_DARK, "menu_theme_dark"))
DEFAULT_SIZE = (1280, 820)


class APITestkaUI(QMainWindow):
    """Main window; switching the language rebuilds the widget, switching the theme restyles it."""

    def __init__(self, theme: str = THEME_SYSTEM) -> None:
        super().__init__()
        self.theme = theme
        if sys.platform in ("win32", "cygwin", "msys"):
            from ctypes import windll  # Windows only: group the taskbar icon under this app
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(tr("application_name"))
        self.resize(*DEFAULT_SIZE)
        self.api_testka_widget: Optional[APITestkaWidget] = None
        self._rebuild()
        self.apply_theme(theme)

    def _rebuild(self) -> None:
        self.setWindowTitle(tr("application_name"))
        self.api_testka_widget = APITestkaWidget()
        self.setCentralWidget(self.api_testka_widget)
        self.menuBar().clear()
        self._add_choice_menu(tr("menu_language"), LANGUAGES, language_wrapper.language, self.switch_language)
        self._add_choice_menu(tr("menu_theme"), THEME_CHOICES, self.theme, self.apply_theme)
        self.statusBar().showMessage(tr("ready"))

    def _add_choice_menu(self, title: str, choices: tuple, current: str, handler) -> QMenu:
        menu = self.menuBar().addMenu(title)
        group = QActionGroup(menu)
        for value, key in choices:
            action = QAction(tr(key), menu, checkable=True)
            action.setChecked(value == current)
            action.triggered.connect(lambda _checked=False, chosen=value: handler(chosen))
            group.addAction(action)
            menu.addAction(action)
        return menu

    def switch_language(self, language: str) -> None:
        """Switch the interface language and rebuild the pages in it."""
        language_wrapper.reset_language(language)
        self._rebuild()

    def apply_theme(self, theme: str) -> None:
        """Apply ``system``, ``light`` or ``dark``."""
        self.theme = theme
        self.setStyleSheet(build_stylesheet(resolve_theme(theme)))


def main() -> int:
    """Start the standalone GUI."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = APITestkaUI()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
