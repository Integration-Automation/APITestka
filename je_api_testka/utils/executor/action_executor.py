import sys
import types

from je_api_testka.requests_wrapper.request_method import test_api_method
from je_api_testka.utils.exception.exception_tag import executor_data_error, executor_list_error
from je_api_testka.utils.exception.exception_tag import add_command_exception_tag
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

    def execute_event(self, action: list):
        """
        :param action: execute action
        :return: what event return
        """
        event = self.event_dict.get(action[0])
        if len(action) == 2:
            return event(**action[1])
        else:
            raise APITesterExecuteException(executor_data_error)

    def execute_action(self, action_list: list):
        """
        :param action_list: like this structure
        [
            ["method on event_dict", {"param": params}],
            ["method on event_dict", {"param": params}]
        ]
        for loop and use execute_event function to execute
        :return: recode string, response as list
        """
        execute_record_string = ""
        event_response_list = []
        try:
            if len(action_list) > 0 or type(action_list) is not list:
                pass
            else:
                raise APITesterExecuteException(executor_list_error)
        except Exception as error:
            print(repr(error), file=sys.stderr)
        for action in action_list:
            try:
                event_response = self.execute_event(action)
                print("execute: ", str(action))
                execute_record_string = "".join(execute_record_string)
                event_response_list.append(event_response)
            except Exception as error:
                print(repr(error), file=sys.stderr)
        return execute_record_string, event_response_list

    def execute_files(self, execute_files_list: list):
        """
        :param execute_files_list: list include execute files path
        :return: every execute detail as list
        """
        execute_detail_list = list()
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
