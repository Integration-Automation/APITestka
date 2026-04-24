import sys

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QApplication
from qt_material import QtStyleTools

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.main_widget import APITestkaWidget


class APITestkaUI(QMainWindow, QtStyleTools):

    def __init__(self):
        super().__init__()

        self.id = language_wrapper.language_word_dict.get("application_name")
        if sys.platform in ["win32", "cygwin", "msys"]:
            from ctypes import windll
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.id)

        self.setStyleSheet("font-size: 12pt; font-family: 'Lato';")
        self.apply_stylesheet(self, "dark_amber.xml")
        self.setWindowTitle(self.id)
        self.resize(1000, 750)

        self.api_testka_widget = APITestkaWidget()
        self.setCentralWidget(self.api_testka_widget)

        self._build_menu_bar()

    def _build_menu_bar(self):
        menu_bar = self.menuBar()

        # Language menu
        lang_menu = menu_bar.addMenu(
            language_wrapper.language_word_dict.get("menu_language")
        )

        english_action = QAction(
            language_wrapper.language_word_dict.get("menu_language_english"), self
        )
        english_action.triggered.connect(lambda: self._switch_language("English"))
        lang_menu.addAction(english_action)

        chinese_action = QAction(
            language_wrapper.language_word_dict.get("menu_language_chinese"), self
        )
        chinese_action.triggered.connect(lambda: self._switch_language("Traditional_Chinese"))
        lang_menu.addAction(chinese_action)

    def _switch_language(self, language):
        language_wrapper.reset_language(language)
        # Rebuild the UI with the new language
        self.api_testka_widget = APITestkaWidget()
        self.setCentralWidget(self.api_testka_widget)
        self._build_menu_bar()
        self.setWindowTitle(language_wrapper.language_word_dict.get("application_name"))


if "__main__" == __name__:
    app = QApplication(sys.argv)
    window = APITestkaUI()
    window.show()
    sys.exit(app.exec())
