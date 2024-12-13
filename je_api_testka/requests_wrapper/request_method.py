from datetime import datetime
from typing import Dict

import requests
from requests import Session
from requests import delete
from requests import get
from requests import head
from requests import options
from requests import patch
from requests import post
from requests import put
from requests.structures import CaseInsensitiveDict

from je_api_testka.utils.assert_result.result_check import check_result
from je_api_testka.utils.exception.exception_tags import get_data_error_message
from je_api_testka.utils.exception.exception_tags import http_method_have_wrong_type
from je_api_testka.utils.exception.exception_tags import wrong_http_method_error_message
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.exception.exceptions import APITesterGetDataException
from je_api_testka.requests_wrapper.requests_data import get_requests_data
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

_session = Session()

http_method_dict = {
    "get": get,
    "put": put,
    "patch": patch,
    "post": post,
    "head": head,
    "delete": delete,
    "options": options,
    "session_get": _session.get,
    "session_put": _session.put,
    "session_patch": _session.patch,
    "session_post": _session.post,
    "session_head": _session.head,
    "session_delete": _session.delete,
    "session_options": _session.options,
}


def get_http_method(http_method: str) -> [
    requests.get, requests.put, requests.patch, requests.post, requests.head, requests.delete,
    Session.get, Session.put, Session.patch, Session.post, Session.head, Session.head, Session.options
]:
    """
    :param http_method: what http method we use to api test
    :return: one of method in http_method_dict if not exists will raise exception
    """
    apitestka_logger.info("request_method.py get_http_method")
    try:
        if not isinstance(http_method, str):
            apitestka_logger.error(
                f"requests get_http_method failed. {APITesterException(wrong_http_method_error_message)}")
            raise APITesterException(wrong_http_method_error_message)
        http_method = str(http_method).lower()
        if http_method not in http_method_dict:
            apitestka_logger.error(
                f"requests get_http_method failed. {APITesterException(http_method_have_wrong_type)}")
            raise APITesterException(http_method_have_wrong_type)
        return http_method_dict.get(http_method)
    except APITesterException as error:
        apitestka_logger.error(
            f"requests get_http_method failed. {repr(error)}")


def send_requests(http_method: str, test_url: str, verify: bool = False, timeout: int = 5,
                  allow_redirects: bool = False, **kwargs) -> requests.Response:
    """
    :param http_method: what http method we use to api test
    :param test_url: what url we want to test
    :param kwargs: use to setting param
    :param verify: this connect need verify or not
    :param timeout: timeout sec
    :param allow_redirects: allow to redirects to another request
    :return: test method
    """
    apitestka_logger.info("request_method.py get_http_method "
                          f"http_method: {http_method} "
                          f"test_url: {test_url} "
                          f"verify: {verify} "
                          f"timeout: {timeout} "
                          f"allow_redirects: {allow_redirects} "
                          f"kwargs: {kwargs}")
    method = get_http_method(http_method)
    if method is None:
        apitestka_logger.error(
            f"requests api_tester_method failed. {APITesterException(wrong_http_method_error_message)}")
        raise APITesterException(wrong_http_method_error_message)
    else:
        response = method(test_url, verify=verify, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
    return response


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
    apitestka_logger.info("request_method.py get_response "
                          f"response: {response} "
                          f"start_time: {start_time} "
                          f"end_time: {end_time}"
                          )
    try:
        return get_requests_data(response, start_time, end_time)
    except APITesterGetDataException:
        raise APITesterGetDataException(get_data_error_message)


def test_api_method_requests(http_method: str, test_url: str,
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
    apitestka_logger.info("request_method.py test_api_method_requests "
                          f"http_method: {http_method} "
                          f"test_url: {test_url} "
                          f"soap: {soap} "
                          f"record_request_info: {record_request_info} "
                          f"clean_record: {clean_record} "
                          f"result_check_dict: {result_check_dict} "
                          f"verify: {verify} "
                          f"timeout: {timeout} "
                          f"allow_redirects: {allow_redirects} "
                          f"kwargs: {kwargs}"
                          )
    try:
        start_time: datetime = datetime.now()
        if soap is False:
            response = send_requests(http_method, test_url=test_url, verify=verify, timeout=timeout,
                                     allow_redirects=allow_redirects, **kwargs)
        else:
            headers = CaseInsensitiveDict()
            headers["Content-Type"] = "application/soap+xml"
            return test_api_method_requests(http_method, test_url=test_url, headers=headers, **kwargs)
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
            f"requests test_api_method, http_method: {http_method}, test_url:{test_url}, soap: {soap}, "
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
