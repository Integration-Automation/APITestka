import sys
import types
import typing

from je_api_testka.requests_wrapper.request_method import test_api_method
from je_api_testka.utils.exception.exception_tag import add_command_exception_tag
from je_api_testka.utils.exception.exception_tag import executor_data_error, executor_list_error
from je_api_testka.utils.exception.exceptions import APITesterExecuteException, APIAddCommandException
from je_api_testka.utils.html_report.html_report_generate import generate_html
from je_api_testka.utils.json.json_file.json_file import read_action_json


class Executor(object):

    def __init__(self):
        self.event_dict = {
            # test api
            "test_api_method": test_api_method,
            "generate_html": generate_html,
        }

    def _execute_event(self, action: list):
        """
        :param action: execute action
        :return: what event return
        """
        event: typing.Callable = self.event_dict.get(action[0])
        if len(action) == 2:
            return event(**action[1])
        else:
            raise APITesterExecuteException(executor_data_error + " " + str(action))

    def execute_action(self, action_list: [list, dict]) -> dict:
        """
        :param action_list: like this structure
        [
            ["method on event_dict", {"param": params}],
            ["method on event_dict", {"param": params}]
        ]
        for loop and use execute_event function to execute
        :return: recode string, response as list
        """
        if isinstance(action_list, dict):
            action_list: list = action_list.get("api_testka", None)
            if action_list is None:
                raise APITesterExecuteException(executor_list_error)
        execute_record_dict = dict()
        try:
            if len(action_list) > 0 or isinstance(action_list, list) is False:
                pass
            else:
                raise APITesterExecuteException(executor_list_error)
        except Exception as error:
            print(repr(error), file=sys.stderr)
        for action in action_list:
            try:
                event_response = self._execute_event(action)
                execute_record: str = "execute: " + str(action)
                execute_record_dict.update({execute_record: event_response})
            except Exception as error:
                print(repr(error), file=sys.stderr)
                print(action, file=sys.stderr)
                execute_record = "execute: " + str(action)
                execute_record_dict.update({execute_record: repr(error)})
        for key, value in execute_record_dict.items():
            print(key)
            print(value)
        return execute_record_dict

    def execute_files(self, execute_files_list: list):
        """
        :param execute_files_list: list include execute files path
        :return: every execute detail as list
        """
        execute_detail_list: list = list()
        for file in execute_files_list:
            execute_detail_list.append(self.execute_action(read_action_json(file)))
        return execute_detail_list


executor = Executor()


def add_command_to_executor(command_dict: dict):
    for command_name, command in command_dict.items():
        if isinstance(command, (types.MethodType, types.FunctionType)):
            executor.event_dict.update({command_name: command})
        else:
            raise APIAddCommandException(add_command_exception_tag)


def execute_action(action_list: list):
    return executor.execute_action(action_list)


def execute_files(execute_files_list: list):
    return executor.execute_files(execute_files_list)
