"""Public facade of APITestka; ``__all__`` is the supported import surface (architecture.md §3)."""
from flask import redirect, request

from je_api_testka.graphql_wrapper.graphql_method import (
    test_api_method_graphql,
    test_api_method_graphql_async,
)
from je_api_testka.httpx_wrapper.async_httpx_method import test_api_method_httpx_async
from je_api_testka.httpx_wrapper.httpx_method import test_api_method_httpx
from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.sse_wrapper.sse_method import iter_sse_events, test_api_method_sse
from je_api_testka.utils.assert_result.schema_check import check_json_schema, check_jsonpath
from je_api_testka.utils.assert_result.snapshot import assert_snapshot
from je_api_testka.utils.callback.callback_function_executor import callback_executor
from je_api_testka.utils.executor.action_executor import (
    add_command_to_executor,
    execute_action,
    execute_files,
    executor,
)
from je_api_testka.utils.file_process.get_dir_file_list import get_dir_files_as_list
from je_api_testka.utils.generate_report.html_report_generate import generate_html, generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json, generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml, generate_xml_report
from je_api_testka.utils.json.json_file.json_file import read_action_json, write_action_json
from je_api_testka.utils.json.json_format.json_process import reformat_json
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.project.create_project_structure import create_project_dir
from je_api_testka.utils.retry.retry_policy import RetryPolicy, retry_call
from je_api_testka.utils.socket_server.api_testka_socket_server import start_apitestka_socket_server
from je_api_testka.utils.test_record.test_record_class import test_record_instance
from je_api_testka.utils.xml.change_xml_structure.change_xml_structure import (
    dict_to_elements_tree,
    elements_tree_to_dict,
)
from je_api_testka.utils.xml.xml_file.xml_file import XMLParser, reformat_xml_file
from je_api_testka.websocket_wrapper.websocket_method import (
    test_api_method_websocket,
    test_api_method_websocket_async,
)

__all__ = ["test_api_method_requests", "test_api_method_httpx", "test_api_method_httpx_async",
           "add_command_to_executor",
           "execute_action", "execute_files", "executor",
           "get_dir_files_as_list",
           "generate_html", "generate_html_report", "read_action_json",
           "write_action_json", "reformat_json", "generate_json", "generate_json_report",
           "start_apitestka_socket_server",
           "test_record_instance", "dict_to_elements_tree", "elements_tree_to_dict",
           "XMLParser", "reformat_xml_file", "generate_xml", "generate_xml_report",
           "callback_executor", "create_project_dir", "flask_mock_server_instance",
           "request", "redirect",
           "test_api_method_websocket", "test_api_method_websocket_async",
           "iter_sse_events", "test_api_method_sse",
           "test_api_method_graphql", "test_api_method_graphql_async",
           "check_json_schema", "check_jsonpath", "assert_snapshot",
           "RetryPolicy", "retry_call",
           ]
