import builtins
import types
from inspect import getmembers, isbuiltin
from typing import Dict, Callable, Any, List, Union

from je_api_testka import test_api_method_httpx
from je_api_testka.httpx_wrapper.async_httpx_method import delegate_async_httpx
from je_api_testka.requests_wrapper.request_method import test_api_method_requests
from je_api_testka.utils.exception.exception_tags import add_command_exception_tag
from je_api_testka.utils.exception.exception_tags import executor_data_error, executor_list_error
from je_api_testka.utils.exception.exceptions import APITesterExecuteException, APIAddCommandException
from je_api_testka.utils.generate_report.html_report_generate import generate_html, generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json, generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml, generate_xml_report
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.package_manager.package_manager_class import package_manager


class Executor(object):

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
        }
        # 取得所有 Python 內建函式並加入事件字典
        # Get all builtin functions and add to event dictionary
        for function in getmembers(builtins, isbuiltin):
            self.event_dict.update({str(function[0]): function[1]})

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
        apitestka_logger.info(f"execute_action, action_list: {action_list}")
        if isinstance(action_list, dict):
            action_list: list = action_list.get("api_testka", [])
            if action_list is None:
                raise APITesterExecuteException(executor_list_error)

        execute_record_dict = dict()
        try:
            if len(action_list) < 0 or isinstance(action_list, list) is False:
                raise APITesterExecuteException(executor_list_error)
        except Exception as error:
            apitestka_logger.info(f"execute_action, action_list: {action_list}, failed: {repr(error)}")

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

        # 輸出執行結果到 console / Print execution results to console
        for key, value in execute_record_dict.items():
            print(key)
            print(value)

        return execute_record_dict

    def execute_files(self, execute_files_list: list) -> List[Any]:
        """
        執行多個檔案中的事件
        Execute actions from multiple files

        :param execute_files_list: 檔案路徑列表 / List of file paths
        :return: 每個檔案的執行結果列表 / List of execution details
        """
        apitestka_logger.info(f"Executor execute_files execute_files_list: {execute_files_list}")
        apitestka_logger.info(f"execute_files, execute_files_list: {execute_files_list}")
        execute_detail_list: list = list()
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