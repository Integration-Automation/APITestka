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
from je_api_testka.utils.generate_report.html_report_generate import generate_html
from je_api_testka.utils.generate_report.html_report_generate import generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json
from je_api_testka.utils.generate_report.json_report import generate_json_report
from je_api_testka.utils.generate_report.xml_report import generate_xml
from je_api_testka.utils.generate_report.xml_report import generate_xml_report
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.mock_server.flask_mock_server import flask_mock_server_instance
from je_api_testka.utils.package_manager.package_manager_class import package_manager
from je_api_testka.utils.scheduler.extend_apscheduler import scheduler_manager


class Executor(object):

    def __init__(self):
        apitestka_logger.info("Init Executor")
        self.event_dict = {
            # Automation api
            "AT_test_api_method": test_api_method_requests,
            "AT_delegate_async_httpx": delegate_async_httpx,
            "AT_test_api_method_httpx": test_api_method_httpx,
            # Report
            "AT_generate_html": generate_html,
            "AT_generate_html_report": generate_html_report,
            "AT_generate_json": generate_json,
            "AT_generate_json_report": generate_json_report,
            "AT_generate_xml": generate_xml,
            "AT_generate_xml_report": generate_xml_report,
            # Execute
            "AT_execute_action": self.execute_action,
            "AT_execute_files": self.execute_files,
            # Add package
            "AT_add_package_to_executor": package_manager.add_package_to_executor,
            "AT_add_package_to_callback_executor": package_manager.add_package_to_callback_executor,
            # Mock server
            "AT_flask_mock_server_add_router": flask_mock_server_instance.add_router,
            "AT_start_flask_mock_server": flask_mock_server_instance.start_mock_server,
            # Scheduler
            "AT_scheduler_event_trigger": self.scheduler_event_trigger,
            "AT_remove_blocking_scheduler_job": scheduler_manager.remove_blocking_job,
            "AT_remove_nonblocking_scheduler_job": scheduler_manager.remove_nonblocking_job,
            "AT_start_blocking_scheduler": scheduler_manager.start_block_scheduler,
            "AT_start_nonblocking_scheduler": scheduler_manager.start_nonblocking_scheduler,
            "AT_start_all_scheduler": scheduler_manager.start_all_scheduler,
            "AT_shutdown_blocking_scheduler": scheduler_manager.shutdown_blocking_scheduler,
            "AT_shutdown_nonblocking_scheduler": scheduler_manager.shutdown_nonblocking_scheduler,
        }
        # get all builtin function and add to event dict
        for function in getmembers(builtins, isbuiltin):
            self.event_dict.update({str(function[0]): function[1]})

    def _execute_event(self, action: list) -> Any:
        """
        :param action: execute action
        :return: what event return
        """
        apitestka_logger.info(f"Executor _execute_event action: {action}")
        event: Callable = self.event_dict.get(action[0])
        if len(action) == 2:
            if isinstance(action[1], dict):
                return event(**action[1])
            else:
                return event(*action[1])
        elif len(action) == 1:
            return event()
        else:
            raise APITesterExecuteException(executor_data_error + " " + str(action))

    def execute_action(self, action_list: [list, dict]) -> Dict[str, str]:
        """
        :param action_list: like this structure
        [
            ["method on event_dict", {"param": params}],
            ["method on event_dict", {"param": params}]
        ]
        for loop and use execute_event function to execute
        :return: recode string, response as list
        """
        apitestka_logger.info(f"Executor execute_action action_list: {action_list}")
        apitestka_logger.info(f"execute_action, action_list: {action_list}")
        if isinstance(action_list, dict):
            action_list: list = action_list.get("api_testka", None)
            if action_list is None:
                raise APITesterExecuteException(executor_list_error)
        execute_record_dict = dict()
        try:
            if len(action_list) < 0 or isinstance(action_list, list) is False:
                raise APITesterExecuteException(executor_list_error)
        except Exception as error:
            apitestka_logger.info(f"execute_action, action_list: {action_list}, "
                                  f"failed: {repr(error)}")
        for action in action_list:
            try:
                event_response = self._execute_event(action)
                execute_record: str = "execute: " + str(action)
                execute_record_dict.update({execute_record: event_response})
            except Exception as error:
                apitestka_logger.info(
                    f"execute_action, action_list: {action_list}, "
                    f"action: {action}, failed: {repr(error)}")
                execute_record = "execute: " + str(action)
                execute_record_dict.update({execute_record: repr(error)})
        for key, value in execute_record_dict.items():
            print(key)
            print(value)
        return execute_record_dict

    def execute_files(self, execute_files_list: list) -> List[Any]:
        """
        :param execute_files_list: list include execute files path
        :return: every execute detail as list
        """
        apitestka_logger.info(f"Executor execute_files execute_files_list: {execute_files_list}")
        apitestka_logger.info(f"execute_files, execute_files_list: {execute_files_list}")
        execute_detail_list: list = list()
        for file in execute_files_list:
            execute_detail_list.append(self.execute_action(read_action_json(file)))
        return execute_detail_list

    def scheduler_event_trigger(
            self, function: str, id: str = None, args: Union[list, tuple] = None,
            kwargs: dict = None, scheduler_type: str = "nonblocking", wait_type: str = "secondly",
            wait_value: int = 1, **trigger_args: Any) -> None:
        apitestka_logger.info(f"Executor scheduler_event_trigger "
                              f"function: {function}"
                              f"id: {id} "
                              f"args: {args} "
                              f"kwargs: {kwargs} "
                              f"scheduler_type: {scheduler_type} "
                              f"wait_type: {wait_type} "
                              f"wait_value: {wait_value} "
                              f"trigger_args: {trigger_args}")
        if scheduler_type == "nonblocking":
            scheduler_event = scheduler_manager.nonblocking_scheduler_event_dict.get(wait_type)
        else:
            scheduler_event = scheduler_manager.blocking_scheduler_event_dict.get(wait_type)
        scheduler_event(self.event_dict.get(function), id, args, kwargs, wait_value, **trigger_args)


executor = Executor()
package_manager.executor = executor


def add_command_to_executor(command_dict: dict) -> None:
    apitestka_logger.info(f"action_executor.py add_command_to_executor command_dict: {command_dict}")
    for command_name, command in command_dict.items():
        if isinstance(command, (types.MethodType, types.FunctionType)):
            executor.event_dict.update({command_name: command})
        else:
            raise APIAddCommandException(add_command_exception_tag)


def execute_action(action_list: list) -> Any:
    apitestka_logger.info(f"action_executor.py execute_action action_list: {action_list}")
    return executor.execute_action(action_list)


def execute_files(execute_files_list: list) -> List[Any]:
    apitestka_logger.info(f"action_executor.py execute_files execute_files_list: {execute_files_list}")
    return executor.execute_files(execute_files_list)
