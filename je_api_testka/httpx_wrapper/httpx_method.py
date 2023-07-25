from datetime import datetime
from typing import Dict

from httpx import get, put, patch, post, head, delete, options, Response

from je_api_testka.httpx_wrapper.httpx_data import get_httpx_data
from je_api_testka.utils.assert_result.result_check import check_result
from je_api_testka.utils.test_record.test_record_class import test_record_instance

from je_api_testka.utils.exception.exception_tags import get_data_error_message, wrong_http_method_error_message, \
    http_method_have_wrong_type
from je_api_testka.utils.exception.exceptions import APITesterGetDataException, APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

http_method_dict = {
    "get": get,
    "put": put,
    "patch": patch,
    "post": post,
    "head": head,
    "delete": delete,
    "options": options,
}


def get_http_method_httpx(http_method: str) -> [
    get, put, patch, post, head, delete,
]:
    """
    :param http_method: what http method we use to api test
    :return: one of method in http_method_dict if not exists will raise exception
    """
    try:
        if not isinstance(http_method, str):
            apitestka_logger.error(
                f"httpx get_http_method_httpx failed. {APITesterException(wrong_http_method_error_message)}")
            raise APITesterException(wrong_http_method_error_message)
        http_method = str(http_method).lower()
        if http_method not in http_method_dict:
            apitestka_logger.error(
                f"httpx get_http_method_httpx failed. {APITesterException(http_method_have_wrong_type)}")
            raise APITesterException(http_method_have_wrong_type)
        return http_method_dict.get(http_method)
    except APITesterException as error:
        apitestka_logger.error(
            f"httpx get_http_method_httpx failed. {repr(error)}")


def get_httpx_response(response: Response,
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
        return get_httpx_data(response, start_time, end_time)
    except APITesterGetDataException:
        raise APITesterGetDataException(get_data_error_message)


def send_httpx_requests(http_method: str, test_url: str, verify: bool = False, timeout: int = 5, **kwargs) -> Response:
    """
    :param http_method: what http method we use to api test
    :param test_url: what url we want to test
    :param kwargs: use to setting param
    :param verify: this connect need verify or not
    :param timeout: timeout sec
    :return: test method
    """
    method = get_http_method_httpx(http_method)
    if method is None:
        apitestka_logger.error(
            f"httpx send_httpx_requests failed. {APITesterException(wrong_http_method_error_message)}")
        raise APITesterException(wrong_http_method_error_message)
    else:
        response = method(test_url, verify=verify, timeout=timeout, **kwargs)
    return response


def test_api_method_httpx(http_method: str, test_url: str, record_request_info: bool = True,
                          clean_record: bool = False, result_check_dict: dict = None
                          , verify: bool = False, timeout: int = 5,
                          **kwargs) -> (Response, Dict[str, str]):
    """
    set requests http_method url headers and record response and record report
    :param http_method:
    :param test_url:
    :param record_request_info:
    :param clean_record:
    :param result_check_dict:
    :param kwargs:
    """
    apitestka_logger.info(
        f"httpx test_api_method_httpx, http_method: {http_method}, test_url:{test_url}, "
        f"record_request_info: {record_request_info}, clean_record: {clean_record}, "
        f"result_check_dict: {result_check_dict}, verify: {verify}, timeout: {timeout}"
    )
    try:
        start_time: datetime = datetime.now()
        end_time = datetime.now()
        response = send_httpx_requests(http_method, test_url=test_url, verify=verify, timeout=timeout, **kwargs)
        response_data = get_httpx_response(response, start_time, end_time)
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
            f"httpx test_api_method_httpx, http_method: {http_method}, test_url:{test_url}, "
            f"record_request_info: {record_request_info}, clean_record: {clean_record}, "
            f"result_check_dict: {result_check_dict}, verify: {verify}, timeout: {timeout}, "
            f"failed: {repr(error)}"
        )
        test_record_instance.error_record_list.append([
            {
                "http_method": http_method,
                "test_url": test_url,
                "record_request_info": record_request_info,
                "clean_record": clean_record,
                "result_check_dict": result_check_dict
            },
            repr(error)]
        )
