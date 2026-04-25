import asyncio
import traceback

from PySide6.QtCore import QThread

from je_api_testka.gui.language_wrapper.multi_language_wrapper import language_wrapper
from je_api_testka.gui.message_queue import api_testka_ui_queue
from je_api_testka.httpx_wrapper.async_httpx_method import test_api_method_httpx_async
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx
from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.utils.executor.action_executor import execute_action, execute_files
from je_api_testka.utils.generate_report.html_report_generate import generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml_report
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance


_RESPONSE_FIELDS = [
    "status_code", "text", "headers", "content", "history",
    "encoding", "cookies", "elapsed", "request_method",
    "request_url", "request_body", "request_time_sec",
    "start_time", "end_time",
]


def _process_response(response_data: dict):
    for field in _RESPONSE_FIELDS:
        label = language_wrapper.language_word_dict.get(field, field + ": ")
        value = response_data.get(field)
        api_testka_ui_queue.put(f"{label}{value}")


class APIRequestThread(QThread):
    """Thread for executing API requests with any backend."""

    def __init__(self):
        super().__init__()
        self.backend = "httpx"  # "requests", "httpx", "httpx_async"
        self.url = None
        self.http_method = None
        self.params = None
        self.headers = None
        self.body = None
        self.auth = None
        self.timeout = 5
        self.verify_ssl = False
        self.allow_redirects = False
        self.soap = False
        self.result_check_dict = None

    def run(self):
        try:
            kwargs = {}
            if self.params:
                kwargs["params"] = self.params
            if self.headers:
                kwargs["headers"] = self.headers
            if self.body:
                kwargs["data"] = self.body
            if self.auth:
                if isinstance(self.auth, dict):
                    username = self.auth.get("username", "")
                    password = self.auth.get("password", "")
                    kwargs["auth"] = (username, password)
                else:
                    kwargs["auth"] = self.auth

            response = None
            if self.backend == "requests":
                response = test_api_method_requests(
                    http_method=self.http_method,
                    test_url=self.url,
                    soap=self.soap,
                    result_check_dict=self.result_check_dict,
                    verify=self.verify_ssl,
                    timeout=self.timeout,
                    allow_redirects=self.allow_redirects,
                    **kwargs,
                )
            elif self.backend == "httpx":
                response = test_api_method_httpx(
                    http_method=self.http_method,
                    test_url=self.url,
                    result_check_dict=self.result_check_dict,
                    verify=self.verify_ssl,
                    timeout=self.timeout,
                    **kwargs,
                )
            elif self.backend == "httpx_async":
                response = asyncio.run(
                    test_api_method_httpx_async(
                        http_method=self.http_method,
                        test_url=self.url,
                        result_check_dict=self.result_check_dict,
                        timeout=self.timeout,
                        **kwargs,
                    )
                )

            if response and isinstance(response, dict):
                _process_response(response.get("response_data", {}))
            else:
                api_testka_ui_queue.put("Request failed or returned None (check error records)")
        except Exception as error:
            api_testka_ui_queue.put(f"Error: {repr(error)}")
            api_testka_ui_queue.put(traceback.format_exc())


class ExecutorThread(QThread):
    """Thread for running executor actions."""

    def __init__(self):
        super().__init__()
        self.mode = "action"  # "action" or "files"
        self.action_list = None
        self.file_list = None

    @staticmethod
    def _emit_result_dict(result: dict) -> None:
        for key, value in result.items():
            api_testka_ui_queue.put(f"{key}")
            api_testka_ui_queue.put(f"  => {value}")

    def _run_action_mode(self) -> None:
        result = execute_action(self.action_list)
        self._emit_result_dict(result)

    def _run_files_mode(self) -> None:
        results = execute_files(self.file_list)
        for i, result in enumerate(results):
            api_testka_ui_queue.put(f"--- File {i + 1} ---")
            if isinstance(result, dict):
                self._emit_result_dict(result)

    def run(self):
        try:
            if self.mode == "action" and self.action_list:
                self._run_action_mode()
            elif self.mode == "files" and self.file_list:
                self._run_files_mode()
        except Exception as error:
            api_testka_ui_queue.put(f"Executor Error: {repr(error)}")
            api_testka_ui_queue.put(traceback.format_exc())


class ReportThread(QThread):
    """Thread for generating reports."""

    def __init__(self):
        super().__init__()
        self.report_type = "html"  # "html", "json", "xml"
        self.file_name = "test_report"

    def run(self):
        try:
            if self.report_type == "html":
                generate_html_report(self.file_name)
            elif self.report_type == "json":
                generate_json_report(self.file_name)
            elif self.report_type == "xml":
                generate_xml_report(self.file_name)
            api_testka_ui_queue.put(f"Report generated: {self.file_name} ({self.report_type})")
        except Exception as error:
            api_testka_ui_queue.put(f"Report Error: {repr(error)}")


class MockServerThread(QThread):
    """Thread for running Flask mock server."""

    def __init__(self):
        super().__init__()
        self.host = "localhost"
        self.port = 8090

    def run(self):
        try:
            flask_mock_server_instance.host = self.host
            flask_mock_server_instance.port = self.port
            api_testka_ui_queue.put(f"Mock server starting on {self.host}:{self.port}...")
            flask_mock_server_instance.start_mock_server()
        except Exception as error:
            api_testka_ui_queue.put(f"Mock Server Error: {repr(error)}")
