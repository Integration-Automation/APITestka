from PySide6.QtCore import QThread

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.message_queue import api_testka_ui_queue
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx


def _process_response(response_data: dict):
    """
    Process API response and push results into UI queue
    處理 API 回應並將結果推送到 UI 佇列
    """
    # 定義要輸出的欄位 (避免重複程式碼)
    response_fields = [
        "status_code", "text", "headers", "content", "history",
        "encoding", "cookies", "elapsed", "request_method",
        "request_url", "request_body"
    ]

    for field in response_fields:
        # 取得多語言字典中的對應文字
        label = language_wrapper.language_word_dict.get(field, "")
        value = response_data.get(field)
        api_testka_ui_queue.put(f"{label}{value}")


class APITestkaGUIThread(QThread):
    """
    GUI Thread for executing API tests asynchronously
    GUI 執行緒，用於非同步執行 API 測試
    """

    def __init__(self):
        super().__init__()
        self.url: str | None = None
        self.test_method: str | None = None
        self.param: dict | None = None

    def run(self):
        """
        Run the API test in a separate thread
        在獨立執行緒中執行 API 測試
        """
        test_response = test_api_method_httpx(
            http_method=self.test_method,
            test_url=self.url,
            params=self.param
        )

        if test_response and isinstance(test_response, dict):
            _process_response(test_response.get("response_data", {}))

