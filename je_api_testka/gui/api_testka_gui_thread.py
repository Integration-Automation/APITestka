from PySide6.QtCore import QThread

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.message_queue import api_testka_ui_queue
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx


class APITestkaGUIThread(QThread):

    def __init__(self):
        super().__init__()
        self.url = None
        self.test_method = None
        self.param = None

    def run(self):
        test_response = test_api_method_httpx(
            http_method=self.test_method,
            test_url=self.url,
            params=self.param
        )
        if test_response is not None and isinstance(test_response, dict):
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("status_code") +
                                    str(test_response.get("response_data").get("status_code")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("text") +
                                    str(test_response.get("response_data").get("text")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("headers") +
                                    str(test_response.get("response_data").get("headers")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("content") +
                                    str(test_response.get("response_data").get("content")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("history") +
                                    str(test_response.get("response_data").get("history")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("encoding") +
                                    str(test_response.get("response_data").get("encoding")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("cookies") +
                                    str(test_response.get("response_data").get("cookies")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("elapsed") +
                                    str(test_response.get("response_data").get("elapsed")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("request_method") +
                                    str(test_response.get("response_data").get("request_method")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("request_url") +
                                    str(test_response.get("response_data").get("request_url")))
            api_testka_ui_queue.put(language_wrapper.language_word_dict.get("request_body") +
                                    str(test_response.get("response_data").get("request_body")))
