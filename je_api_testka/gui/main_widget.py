import json

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QTabWidget, QFormLayout, QPushButton, QTextEdit
)

from je_api_testka.gui.api_testka_gui_thread import APITestkaGUIThread
from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.message_queue import api_testka_ui_queue


class APITestkaWidget(QWidget):
    """
    API Testka 主視窗元件
    Main widget for API Testka GUI
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 建立主版面配置
        # Create main layout
        main_layout = QVBoxLayout()

        # -------------------------------
        # URL 與 Method 選擇區
        # URL and HTTP Method selection
        # -------------------------------
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel(language_wrapper.language_word_dict.get("url")))

        self.url_input = QLineEdit()
        url_layout.addWidget(self.url_input)

        self.method_combobox = QComboBox()
        self.method_combobox.addItems([
            language_wrapper.language_word_dict.get("get"),
            language_wrapper.language_word_dict.get("post"),
            language_wrapper.language_word_dict.get("put"),
            language_wrapper.language_word_dict.get("patch"),
            language_wrapper.language_word_dict.get("delete"),
            language_wrapper.language_word_dict.get("head"),
            language_wrapper.language_word_dict.get("options"),
        ])
        url_layout.addWidget(self.method_combobox)
        main_layout.addLayout(url_layout)

        # -------------------------------
        # Tabs for Param, Auth, Header, Body
        # -------------------------------
        self.tabs = QTabWidget()
        self.param_tab = QWidget()
        self.auth_tab = QWidget()
        self.header_tab = QWidget()
        self.body_tab = QWidget()

        self.tabs.addTab(self.param_tab, language_wrapper.language_word_dict.get("param"))
        # 可依需求開啟其他 Tab
        # Uncomment if needed
        # self.tabs.addTab(self.auth_tab, "Auth")
        # self.tabs.addTab(self.header_tab, "Header")
        # self.tabs.addTab(self.body_tab, "Body")

        # Param Tab layout
        param_layout = QFormLayout()
        self.param_input = QLineEdit()
        param_layout.addRow(language_wrapper.language_word_dict.get("param"), self.param_input)
        self.param_tab.setLayout(param_layout)

        main_layout.addWidget(self.tabs)

        # -------------------------------
        # Send Button
        # -------------------------------
        self.send_button = QPushButton(language_wrapper.language_word_dict.get("send"))
        self.send_button.clicked.connect(self.start_api_request)
        main_layout.addWidget(self.send_button)

        # -------------------------------
        # Log Panel
        # -------------------------------
        self.log_panel = QTextEdit()
        self.log_panel.setReadOnly(True)
        main_layout.addWidget(QLabel(language_wrapper.language_word_dict.get("response_and_log")))
        main_layout.addWidget(self.log_panel)

        # -------------------------------
        # Thread + Timer
        # -------------------------------
        self.test_api_thread: APITestkaGUIThread | None = None
        self.pull_log_timer = QTimer()
        self.pull_log_timer.setInterval(20)  # 每 20ms 檢查一次佇列
        self.pull_log_timer.timeout.connect(self.pull_log)

        self.setLayout(main_layout)

    def start_api_request(self):
        """
        開始 API 測試請求
        Start API request in a separate thread
        """
        self.log_panel.clear()
        self.pull_log_timer.stop()
        self.pull_log_timer.start()

        self.test_api_thread = APITestkaGUIThread()
        self.test_api_thread.url = self.url_input.text()
        self.test_api_thread.test_method = self.method_combobox.currentText().lower()

        # 嘗試解析 JSON 參數
        # Try to parse JSON parameters
        param_text = self.param_input.text().strip()
        if param_text:
            try:
                self.test_api_thread.param = json.loads(param_text)
            except json.JSONDecodeError:
                # 若 JSON 格式錯誤，忽略並繼續
                # Ignore invalid JSON and continue
                self.test_api_thread.param = None

        self.test_api_thread.start()

    def pull_log(self):
        """
        從佇列中拉取訊息並顯示在 Log Panel
        Pull messages from queue and display in log panel
        """
        while not api_testka_ui_queue.empty():
            message = api_testka_ui_queue.get_nowait()
            self.log_panel.append(str(message))