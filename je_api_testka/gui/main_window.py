import sys

from PySide6.QtWidgets import QMainWindow, QApplication
from qt_material import QtStyleTools

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.main_widget import APITestkaWidget


class APITestkaUI(QMainWindow, QtStyleTools):
    """
    API Testka 主視窗
    Main window for API Testka application
    """

    def __init__(self):
        super().__init__()

        # 設定應用程式 ID (Windows 平台需要，讓工作列顯示正確圖示與名稱)
        # Set application ID (required on Windows for correct taskbar icon and name)
        self.id: str = language_wrapper.language_word_dict.get("application_name")

        if sys.platform in ["win32", "cygwin", "msys"]:
            from ctypes import windll
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.id)

        # 設定字體樣式
        # Set font style
        self.setStyleSheet(
            "font-size: 12pt;"
            "font-family: 'Lato';"
        )

        # 套用 Material Design 主題
        # Apply Material Design theme
        self.apply_stylesheet(self, "dark_amber.xml")

        # 建立並設定主控件
        # Create and set main widget
        self.api_testka_widget: APITestkaWidget = APITestkaWidget()
        self.setCentralWidget(self.api_testka_widget)

if "__main__" == __name__:
    app = QApplication(sys.argv)
    window = APITestkaUI()
    window.show()
    sys.exit(app.exec())