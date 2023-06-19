from datetime import datetime
from typing import Dict

import requests
from requests.structures import CaseInsensitiveDict

from je_api_testka.requests_wrapper.requests_http_method_wrapper import api_tester_method
from je_api_testka.utils.assert_result.result_check import check_result
from je_api_testka.utils.exception.exception_tags import delete_error_message
from je_api_testka.utils.exception.exception_tags import get_data_error_message
from je_api_testka.utils.exception.exception_tags import get_error_message
from je_api_testka.utils.exception.exception_tags import head_error_message
from je_api_testka.utils.exception.exception_tags import options_error_message
from je_api_testka.utils.exception.exception_tags import patch_error_message
from je_api_testka.utils.exception.exception_tags import post_error_message
from je_api_testka.utils.exception.exception_tags import put_error_message
from je_api_testka.utils.exception.exception_tags import session_error_message
from je_api_testka.utils.exception.exceptions import APITesterGetDataException
from je_api_testka.utils.get_data_strcture.get_api_data import get_api_response_data
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

exception_message_dict = {
    "get": get_error_message,
    "put": put_error_message,
    "delete": delete_error_message,
    "post": post_error_message,
    "head": head_error_message,
    "options": options_error_message,
    "patch": patch_error_message,
    "session_get": session_error_message,
    "session_put": session_error_message,
    "session_patch": session_error_message,
    "session_post": session_error_message,
    "session_head": session_error_message,
    "session_delete": session_error_message,
    "session_options": session_error_message,

}


def get_response(response: requests.Response,
                 start_time: [str, float, int],
                 end_time: [str, float, int]) -> Dict[str, str]:
    """
    use requests response to create data dict
    :param response: requests response
    :param start_time: test start time
    :param end_time: test end time
    :return: data dict include [status_code, text, content, headers, history, encoding, cookies,
    elapsed, request_time_sec, request_method, request_url, request_body, start_time, end_time]
    """
    try:
        return get_api_response_data(response, start_time, end_time)
    except APITesterGetDataException:
        raise APITesterGetDataException(get_data_error_message)


def test_api_method(http_method: str, test_url: str,
                    soap: bool = False, record_request_info: bool = True,
                    clean_record: bool = False, result_check_dict: dict = None
                    , verify: bool = False, timeout: int = 5, allow_redirects: bool = False,
                    **kwargs) -> (requests.Response, Dict[str, str]):
    """
    set requests http_method url headers and record response and record report
    :param http_method:
    :param test_url:
    :param soap:
    :param record_request_info:
    :param clean_record:
    :param result_check_dict:
    :param kwargs:
    """
    apitestka_logger.info(
        f"test_api_method, http_method: {http_method}, test_url:{test_url}, soap: {soap}, "
        f"record_request_info: {record_request_info}, clean_record: {clean_record}, "
        f"result_check_dict: {result_check_dict}, verify: {verify}, timeout: {timeout}, "
        f"allow_redirects: {allow_redirects}"
    )
    try:
        start_time: datetime = datetime.now()
        if soap is False:
            response = api_tester_method(http_method, test_url=test_url, verify=verify, timeout=timeout,
                                         allow_redirects=allow_redirects, **kwargs)
        else:
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/soap+xml"
            return test_api_method(http_method, test_url=test_url, headers=headers, **kwargs)
        end_time = datetime.now()
        response_data = get_response(response, start_time, end_time)
        response.raise_for_status()
        if clean_record:
            test_record_instance.clean_record()
        if result_check_dict is None:
            if record_request_info:
                test_record_instance.test_record_list.append(response_data)
            return {"response": response, "response_data": response_data}
        else:
            check_result(response_data, result_check_dict)
            if record_request_info:
                test_record_instance.test_record_list.append(response_data)
            return {"response": response, "response_data": response_data}
    except Exception as error:
        apitestka_logger.error(
            f"test_api_method, http_method: {http_method}, test_url:{test_url}, soap: {soap}, "
            f"record_request_info: {record_request_info}, clean_record: {clean_record}, "
            f"result_check_dict: {result_check_dict}, verify: {verify}, timeout: {timeout}, "
            f"allow_redirects: {allow_redirects}, failed: {repr(error)}"
        )
        test_record_instance.error_record_list.append([
            {
                "http_method": http_method,
                "test_url": test_url,
                "soap": soap,
                "record_request_info": record_request_info,
                "clean_record": clean_record,
                "result_check_dict": result_check_dict
            },
            repr(error)]
        )
