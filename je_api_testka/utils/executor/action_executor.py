import types
from typing import Any, Callable, Dict, List, Optional, Union

from je_api_testka import test_api_method_httpx
from je_api_testka.ai.backend import select_ai_backend
from je_api_testka.ai.failure_classifier import classify_failures
from je_api_testka.ai.fake_data_generator import generate_fake_payload
from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.connection.cassette import Cassette, CassetteRecord
from je_api_testka.contract.commands import check_contract_against_openapi, verify_contract, write_contract
from je_api_testka.data.env_profile import load_env_profile
from je_api_testka.data.faker_helpers import fake_email, fake_uuid, fake_word
from je_api_testka.data.template_render import render_template
from je_api_testka.data.variable_store import extract_and_store, variable_store
from je_api_testka.diff.contract_diff import diff_openapi_specs
from je_api_testka.diff.response_diff import diff_payloads
from je_api_testka.diff.sla_check import assert_sla
from je_api_testka.graphql_wrapper.graphql_method import test_api_method_graphql
from je_api_testka.httpx_wrapper.async_httpx_method import delegate_async_httpx
from je_api_testka.integrations.curl_import import curl_to_action
from je_api_testka.integrations.github_pr_comment import post_pr_comment
from je_api_testka.integrations.har_import import convert_har
from je_api_testka.integrations.load_density_commands import run_load_test_from, write_load_test
from je_api_testka.integrations.notify import notify_via_webhook
from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.runner.dependency_runner import order_actions
from je_api_testka.runner.metadata import strip_runner_metadata
from je_api_testka.runner.parallel_runner import run_actions_parallel
from je_api_testka.runner.tag_filter import filter_actions_by_tag
from je_api_testka.security.auth_helpers import (
    aws_sigv4_headers,
    basic_auth_header,
    bearer_token_header,
    build_jwt,
)
from je_api_testka.security.cors_check import cors_preflight
from je_api_testka.security.cve_check import run_pip_audit
from je_api_testka.security.fuzz import fuzz_string_inputs
from je_api_testka.security.header_scan import scan_security_headers
from je_api_testka.security.rate_limit_probe import probe_rate_limit
from je_api_testka.security.ssrf_check import probe_ssrf
from je_api_testka.spec.openapi_changelog import openapi_changelog
from je_api_testka.spec.openapi_export import export_openapi
from je_api_testka.spec.records_to_openapi import records_to_openapi
from je_api_testka.spec.schema_inference import infer_schema
from je_api_testka.spec.spec_loop import check_spec_against_tests
from je_api_testka.sse_wrapper.sse_method import test_api_method_sse
from je_api_testka.utils.assert_result.schema_check import check_json_schema, check_jsonpath
from je_api_testka.utils.assert_result.snapshot import assert_snapshot
from je_api_testka.utils.exception.exception_tags import (
    add_command_exception_tag,
    executor_data_error,
    executor_list_error,
)
from je_api_testka.utils.exception.exceptions import APIAddCommandException, APITesterExecuteException
from je_api_testka.utils.generate_report.allure_report import generate_allure_report
from je_api_testka.utils.generate_report.badge import generate_badge
from je_api_testka.utils.generate_report.html_report_generate import generate_html, generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json, generate_json_report
from je_api_testka.utils.generate_report.junit_report import generate_junit_report
from je_api_testka.utils.generate_report.latency_trends import (
    assert_no_latency_anomalies,
    detect_latency_anomalies,
    record_endpoint_latencies,
)
from je_api_testka.utils.generate_report.markdown_report import generate_markdown_report, render_markdown
from je_api_testka.utils.generate_report.run_diff import diff_runs
from je_api_testka.utils.generate_report.trend_report import generate_trend_report
from je_api_testka.utils.generate_report.trend_store import DEFAULT_TREND_DB, list_trend_rows, record_current_run
from je_api_testka.utils.generate_report.xml_report import generate_xml, generate_xml_report
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.mock_server.protocol_mocks import (
    grpc_mock_received,
    start_grpc_mock,
    start_websocket_mock,
    stop_grpc_mock,
    stop_websocket_mock,
    websocket_mock_received,
)
from je_api_testka.utils.package_manager.package_manager_class import package_manager
from je_api_testka.websocket_wrapper.websocket_method import test_api_method_websocket


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


def _detect_latency_anomalies(db_path: str = DEFAULT_TREND_DB, policy: Optional[dict] = None) -> List[dict]:
    """JSON-ready verdicts of :func:`detect_latency_anomalies`."""
    return [verdict.to_dict() for verdict in detect_latency_anomalies(db_path, policy)]


_NAME_ONLY: int = 1  # [name]
_NAME_AND_ARGUMENTS: int = 2  # [name, {kwargs}] or [name, [args]]


class Executor:

    def __init__(self):
        # 初始化 Executor，建立事件字典
        # Initialize Executor and build event dictionary
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
            "AT_record_endpoint_latencies": record_endpoint_latencies,
            "AT_detect_latency_anomalies": _detect_latency_anomalies,
            "AT_assert_no_latency_anomalies": assert_no_latency_anomalies,
            "AT_generate_trend_report": generate_trend_report,
            # Integrations
            "AT_notify_via_webhook": notify_via_webhook,
            "AT_post_pr_comment": post_pr_comment,
            "AT_curl_to_action": curl_to_action,
            "AT_convert_har": convert_har,
            # LoadDensity bridge
            "AT_write_load_test": write_load_test,
            "AT_run_load_test": run_load_test_from,
            # Security checks
            "AT_cors_preflight": cors_preflight,
            "AT_probe_rate_limit": probe_rate_limit,
            "AT_probe_ssrf": probe_ssrf,
            # Spec inference
            "AT_infer_schema": infer_schema,
            "AT_records_to_openapi": records_to_openapi,
            "AT_export_openapi": export_openapi,
            "AT_openapi_changelog": openapi_changelog,
            "AT_check_spec_against_tests": check_spec_against_tests,
            # Consumer contracts (Pact v2 files)
            "AT_write_contract": write_contract,
            "AT_verify_contract": verify_contract,
            "AT_check_contract_against_openapi": check_contract_against_openapi,
            # AI integrations
            "AT_classify_failures": classify_failures,
            "AT_generate_fake_payload": generate_fake_payload,
            "AT_generate_tests_from_openapi": generate_tests_from_openapi,
            "AT_select_ai_backend": select_ai_backend,
            # Extra protocol backends (sync entry points only; async variants
            # are intentionally not registered because they return coroutines
            # that the executor would not await).
            "AT_test_api_method_websocket": test_api_method_websocket,
            "AT_test_api_method_sse": test_api_method_sse,
            "AT_test_api_method_graphql": test_api_method_graphql,
            # Schema / JSONPath / snapshot assertions
            "AT_check_json_schema": check_json_schema,
            "AT_check_jsonpath": check_jsonpath,
            "AT_assert_snapshot": assert_snapshot,
            # Auth helpers
            "AT_basic_auth_header": basic_auth_header,
            "AT_bearer_token_header": bearer_token_header,
            "AT_build_jwt": build_jwt,
            "AT_aws_sigv4_headers": aws_sigv4_headers,
            # Security scans
            "AT_scan_security_headers": scan_security_headers,
            "AT_fuzz_string_inputs": fuzz_string_inputs,
            "AT_run_pip_audit": run_pip_audit,
            # Mock server advanced features (bound methods on the global instance)
            "AT_mock_add_dynamic_route": flask_mock_server_instance.add_dynamic_route,
            "AT_mock_add_template_route": flask_mock_server_instance.add_template_route,
            "AT_mock_add_webhook": flask_mock_server_instance.add_webhook,
            "AT_mock_add_proxy": flask_mock_server_instance.add_proxy,
            "AT_mock_load_openapi": flask_mock_server_instance.load_openapi,
            # WebSocket and gRPC mocks (one of each, running in background threads)
            "AT_mock_start_websocket_server": start_websocket_mock,
            "AT_mock_stop_websocket_server": stop_websocket_mock,
            "AT_mock_websocket_received": websocket_mock_received,
            "AT_mock_start_grpc_server": start_grpc_mock,
            "AT_mock_stop_grpc_server": stop_grpc_mock,
            "AT_mock_grpc_received": grpc_mock_received,
            # Runner
            "AT_run_actions_parallel": run_actions_parallel,
            "AT_filter_actions_by_tag": filter_actions_by_tag,
            "AT_order_actions": order_actions,
            # JUnit / Allure reports
            "AT_generate_junit_report": generate_junit_report,
            "AT_generate_allure_report": generate_allure_report,
        }

    @staticmethod
    def set_allow_arbitrary_packages(enabled: bool) -> None:
        """
        允許或拒絕載入允許清單以外的套件（``AT_add_package_to_executor``）
        Allow (True) or refuse (False) ``AT_add_package_to_executor`` and
        ``AT_add_package_to_callback_executor`` for packages outside the allowlist. Python only,
        never an action command, so an action file cannot open its own gate. Until it is called,
        any package loads with a ``DeprecationWarning``.
        """
        package_manager.set_allow_arbitrary_packages(enabled)

    @staticmethod
    def allow_packages(*packages: str) -> None:
        """
        把套件（連同子模組）加入 ``AT_add_package_to_executor`` 的允許清單
        Add packages, and their submodules, to the allowlist of ``AT_add_package_to_executor``.
        """
        package_manager.allow_packages(*packages)

    def _execute_event(self, action: list) -> Any:
        """
        執行單一事件
        Execute a single event

        :param action: 要執行的事件 (list 格式)
                       Event to execute (list format)
        :return: 事件回傳值 / Event return value
        """
        apitestka_logger.info(f"Executor _execute_event action: {action}")
        # Runner metadata (id, depends_on, tags) orders and filters actions; the command never sees it.
        action = strip_runner_metadata(action)
        event: Callable = self.event_dict.get(action[0])
        if len(action) == _NAME_AND_ARGUMENTS:
            if isinstance(action[1], dict):
                return event(**action[1])  # 使用 kwargs 呼叫 / Call with kwargs
            else:
                return event(*action[1])   # 使用 args 呼叫 / Call with args
        elif len(action) == _NAME_ONLY:
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
