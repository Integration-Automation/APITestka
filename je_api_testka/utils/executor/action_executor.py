import types
from typing import Dict, Callable, Any, List, Union

from je_api_testka import test_api_method_httpx
from je_api_testka.data.env_profile import load_env_profile
from je_api_testka.data.faker_helpers import fake_email, fake_uuid, fake_word
from je_api_testka.data.template_render import render_template
from je_api_testka.data.variable_store import extract_and_store, variable_store
from je_api_testka.connection.cassette import Cassette, CassetteRecord
from je_api_testka.diff.contract_diff import diff_openapi_specs
from je_api_testka.diff.response_diff import diff_payloads
from je_api_testka.diff.sla_check import assert_sla
from je_api_testka.integrations.curl_import import curl_to_action
from je_api_testka.integrations.github_pr_comment import post_pr_comment
from je_api_testka.integrations.har_import import convert_har
from je_api_testka.integrations.notify import notify_via_webhook
from je_api_testka.security.cors_check import cors_preflight
from je_api_testka.security.rate_limit_probe import probe_rate_limit
from je_api_testka.security.ssrf_check import probe_ssrf
from je_api_testka.spec.openapi_changelog import openapi_changelog
from je_api_testka.spec.records_to_openapi import records_to_openapi
from je_api_testka.spec.schema_inference import infer_schema


def _cassette_lookup(file_path: str, method: str, url: str, body: str = "") -> dict:
    cassette = Cassette(file_path)
    record = cassette.get(method, url, body)
    return record.__dict__ if record else {}


def _cassette_record(file_path: str, method: str, url: str, request_body: str,
                     response_status: int, response_body: str,
                     response_headers: dict = None) -> None:
    cassette = Cassette(file_path)
    cassette.put(CassetteRecord(
        method=method, url=url, request_body=request_body,
        response_status=response_status, response_body=response_body,
        response_headers=response_headers or {},
    ))
from je_api_testka.httpx_wrapper.async_httpx_method import delegate_async_httpx
from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.utils.exception.exception_tags import add_command_exception_tag
from je_api_testka.utils.exception.exception_tags import executor_data_error, executor_list_error
from je_api_testka.utils.exception.exceptions import APITesterExecuteException, APIAddCommandException
from je_api_testka.utils.generate_report.badge import generate_badge
from je_api_testka.utils.generate_report.html_report_generate import generate_html, generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json, generate_json_report
from je_api_testka.utils.generate_report.markdown_report import generate_markdown_report, render_markdown
from je_api_testka.utils.generate_report.run_diff import diff_runs
from je_api_testka.utils.generate_report.trend_store import list_trend_rows, record_current_run
from je_api_testka.utils.generate_report.xml_report import generate_xml, generate_xml_report
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.package_manager.package_manager_class import package_manager


class Executor:

    def __init__(self):
        # 初始化 Executor，建立事件字典
        # Initialize Executor and build event dictionary
        apitestka_logger.info("Init Executor")
        self.event_dict = {
            # 自動化 API / Automation API
            "AT_test_api_method": test_api_method_requests,
            "AT_delegate_async_httpx": delegate_async_httpx,
            "AT_test_api_method_httpx": test_api_method_httpx,
            # 報告生成 / Report generation
            "AT_generate_html": generate_html,
            "AT_generate_html_report": generate_html_report,
            "AT_generate_json": generate_json,
            "AT_generate_json_report": generate_json_report,
            "AT_generate_xml": generate_xml,
            "AT_generate_xml_report": generate_xml_report,
            # 執行 / Execute
            "AT_execute_action": self.execute_action,
            "AT_execute_files": self.execute_files,
            # 套件管理 / Package manager
            "AT_add_package_to_executor": package_manager.add_package_to_executor,
            "AT_add_package_to_callback_executor": package_manager.add_package_to_callback_executor,
            # 模擬伺服器 / Mock server
            "AT_flask_mock_server_add_router": flask_mock_server_instance.add_router,
            "AT_start_flask_mock_server": flask_mock_server_instance.start_mock_server,
            # 變數 / Variables
            "AT_set_variable": variable_store.set,
            "AT_get_variable": variable_store.get,
            "AT_clear_variables": variable_store.clear,
            "AT_extract_and_store": extract_and_store,
            "AT_render_template": render_template,
            # 假資料 / Fake data
            "AT_fake_uuid": fake_uuid,
            "AT_fake_email": fake_email,
            "AT_fake_word": fake_word,
            # 環境設定檔 / Env profile
            "AT_load_env_profile": load_env_profile,
            # Diff / Contract / SLA
            "AT_diff_payloads": diff_payloads,
            "AT_diff_openapi_specs": diff_openapi_specs,
            "AT_assert_sla": assert_sla,
            # Cassette
            "AT_cassette_lookup": _cassette_lookup,
            "AT_cassette_record": _cassette_record,
            # Markdown / Run diff / Badge / Trend
            "AT_render_markdown": render_markdown,
            "AT_generate_markdown_report": generate_markdown_report,
            "AT_diff_runs": diff_runs,
            "AT_generate_badge": generate_badge,
            "AT_record_current_run": record_current_run,
            "AT_list_trend_rows": list_trend_rows,
            # Integrations
            "AT_notify_via_webhook": notify_via_webhook,
            "AT_post_pr_comment": post_pr_comment,
            "AT_curl_to_action": curl_to_action,
            "AT_convert_har": convert_har,
            # Security checks
            "AT_cors_preflight": cors_preflight,
            "AT_probe_rate_limit": probe_rate_limit,
            "AT_probe_ssrf": probe_ssrf,
            # Spec inference
            "AT_infer_schema": infer_schema,
            "AT_records_to_openapi": records_to_openapi,
            "AT_openapi_changelog": openapi_changelog,
        }

    def _execute_event(self, action: list) -> Any:
        """
        執行單一事件
        Execute a single event

        :param action: 要執行的事件 (list 格式)
                       Event to execute (list format)
        :return: 事件回傳值 / Event return value
        """
        apitestka_logger.info(f"Executor _execute_event action: {action}")
        event: Callable = self.event_dict.get(action[0])
        if len(action) == 2:
            if isinstance(action[1], dict):
                return event(**action[1])  # 使用 kwargs 呼叫 / Call with kwargs
            else:
                return event(*action[1])   # 使用 args 呼叫 / Call with args
        elif len(action) == 1:
            return event()                # 無參數呼叫 / Call without arguments
        else:
            raise APITesterExecuteException(executor_data_error + " " + str(action))

    def execute_action(self, action_list: Union[list, dict]) -> Dict[str, str]:
        """
        執行多個事件，並記錄結果
        Execute multiple actions and record results

        :param action_list: 事件列表，例如：
                            [["method", {"param": value}], ["method", {"param": value}]]
        :return: 執行紀錄字典 / Execution record dictionary
        """
        apitestka_logger.info(f"Executor execute_action action_list: {action_list}")
        if isinstance(action_list, dict):
            action_list: list = action_list.get("api_testka", [])
            if action_list is None:
                raise APITesterExecuteException(executor_list_error)

        execute_record_dict = {}
        if not isinstance(action_list, list) or not action_list:
            raise APITesterExecuteException(executor_list_error)

        for action in action_list:
            try:
                event_response = self._execute_event(action)
                execute_record: str = "execute: " + str(action)
                execute_record_dict.update({execute_record: event_response})
            except Exception as error:
                apitestka_logger.info(
                    f"execute_action, action_list: {action_list}, action: {action}, failed: {repr(error)}"
                )
                execute_record = "execute: " + str(action)
                execute_record_dict.update({execute_record: repr(error)})

        # 輸出執行結果到 logger / Log execution results
        for key, value in execute_record_dict.items():
            apitestka_logger.info(f"{key} -> {value}")

        return execute_record_dict

    def execute_files(self, execute_files_list: list) -> List[Any]:
        """
        執行多個檔案中的事件
        Execute actions from multiple files

        :param execute_files_list: 檔案路徑列表 / List of file paths
        :return: 每個檔案的執行結果列表 / List of execution details
        """
        apitestka_logger.info(f"Executor execute_files execute_files_list: {execute_files_list}")
        execute_detail_list: list = []
        for file in execute_files_list:
            execute_detail_list.append(self.execute_action(read_action_json(file)))
        return execute_detail_list


# 建立全域 Executor 並綁定到 package_manager
# Create global Executor and bind to package_manager
executor = Executor()
package_manager.executor = executor


def add_command_to_executor(command_dict: dict) -> None:
    """
    新增自訂命令到 Executor
    Add custom command to Executor

    :param command_dict: 命令字典 (名稱: 函式)
                         Command dictionary (name: function)
    """
    apitestka_logger.info(f"action_executor.py add_command_to_executor command_dict: {command_dict}")
    for command_name, command in command_dict.items():
        if isinstance(command, (types.MethodType, types.FunctionType)):
            executor.event_dict.update({command_name: command})
        else:
            raise APIAddCommandException(add_command_exception_tag)


def execute_action(action_list: list) -> Any:
    """
    對外提供的執行事件介面
    Public interface to execute actions
    """
    apitestka_logger.info(f"action_executor.py execute_action action_list: {action_list}")
    return executor.execute_action(action_list)


def execute_files(execute_files_list: list) -> List[Any]:
    """
    對外提供的執行檔案介面
    Public interface to execute files
    """
    apitestka_logger.info(f"action_executor.py execute_files execute_files_list: {execute_files_list}")
    return executor.execute_files(execute_files_list)