from je_api_testka.requests_wrapper.request_method import test_api_method
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_execute_action_error
from je_api_testka.utils.exception.api_test_exceptions import APITesterExecuteException
from je_api_testka.utils.exception.api_test_eceptions_tag import executor_data_error

event_dict = {
    # test api
    "test_api_method": test_api_method,
}


def execute_event(action):
    event = event_dict.get(action[0])
    if len(action) == 2:
        return event(**action[1])
    else:
        raise APITesterExecuteException(executor_data_error)


def execute_action(action_list):
    execute_record_string = ""
    event_response_list = []
    for action in action_list:
        try:
            event_response = execute_event(action)
        except APITesterExecuteException:
            raise APITesterExecuteException(api_test_execute_action_error)
        print("execute: ", str(action))
        execute_record_string = "".join(execute_record_string)
        event_response_list.append(event_response)
    return execute_record_string, event_response_list


