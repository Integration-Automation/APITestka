import datetime

from je_api_testka.requests_wrapper.requests_http_method_wrapper import api_tester_method
from requests.structures import CaseInsensitiveDict

from je_api_testka.utils.exception.api_test_exceptions import APITesterGetDataException
from je_api_testka.utils.get_data_strcture.get_api_data import get_api_response_data

from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_get_data_error_message

from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_get_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_put_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_delete_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_post_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_head_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_options_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_patch_error_message
from je_api_testka.utils.exception.api_test_eceptions_tag import api_test_session_error_message

from je_api_testka.utils.test_record.record_test_result_class import test_record

from je_api_testka.utils.assert_result.result_check import check_result

exception_message_dict = {
    "get": api_test_get_error_message,
    "put": api_test_put_error_message,
    "delete": api_test_delete_error_message,
    "post": api_test_post_error_message,
    "head": api_test_head_error_message,
    "options": api_test_options_error_message,
    "patch": api_test_patch_error_message,
    "session_get": api_test_session_error_message,
    "session_put": api_test_session_error_message,
    "session_patch": api_test_session_error_message,
    "session_post": api_test_session_error_message,
    "session_head": api_test_session_error_message,
    "session_delete": api_test_session_error_message,
    "session_options": api_test_session_error_message,

}


def get_response(response, start_time, end_time):
    try:
        return get_api_response_data(response, start_time, end_time)
    except APITesterGetDataException:
        raise APITesterGetDataException(api_test_get_data_error_message)


def test_api_method(http_method: str, test_url: str,
                    soap: bool = False, record_request_info: bool = True,
                    clean_record: bool = False, result_check_dict: dict = None, **kwargs):
    start_time = datetime.datetime.now()
    if soap is False:
        response = api_tester_method(http_method, test_url=test_url, **kwargs)
    else:
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/soap+xml"
        return test_api_method(http_method, test_url=test_url, headers=headers, **kwargs)
    end_time = datetime.datetime.now()
    response_data = get_response(response, start_time, end_time)
    if record_request_info:
        test_record.record_list.append(response_data)
    elif clean_record:
        test_record.clean_record()
    if result_check_dict is None:
        return {"response": response, "response_data": response_data}
    else:
        check_result(response_data, result_check_dict)
        return {"response": response, "response_data": response_data}
