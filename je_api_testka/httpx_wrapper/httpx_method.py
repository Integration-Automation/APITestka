from datetime import datetime
from typing import Dict, Union

from httpx import get, put, patch, post, head, delete, options, Response

from je_api_testka.httpx_wrapper.httpx_data import get_httpx_data
from je_api_testka.utils.assert_result.result_check import check_result
from je_api_testka.utils.exception.exception_tags import (
    get_data_error_message,
    wrong_http_method_error_message,
    http_method_have_wrong_type,
)
from je_api_testka.utils.exception.exceptions import APITesterGetDataException, APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

# 定義 HTTP 方法字典，對應到 httpx 的方法
# Define HTTP method dictionary mapping to httpx methods
http_method_dict = {
    "get": get,
    "put": put,
    "patch": patch,
    "post": post,
    "head": head,
    "delete": delete,
    "options": options,
}


def get_http_method_httpx(http_method: str) -> Union[get, put, patch, post, head, delete]:
    """
    根據字串取得對應的 HTTP 方法，若不存在則拋出例外
    Get corresponding HTTP method from string, raise exception if not exists
    """
    apitestka_logger.info(
        "httpx_method.py get_http_method_httpx "
        f"http_method: {http_method}"
    )
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
                       start_time: Union[str, float, int],
                       end_time: Union[str, float, int]) -> Dict[str, str]:
    """
    將 HTTPX Response 轉換成字典，包含狀態碼、內容、標頭、cookies 等資訊
    Convert HTTPX Response into dictionary including status code, content, headers, cookies, etc.
    """
    apitestka_logger.info(
        "httpx_method.py get_httpx_response "
        f"response: {response} "
        f"start_time: {start_time} "
        f"end_time: {end_time} "
    )
    try:
        return get_httpx_data(response, start_time, end_time)
    except APITesterGetDataException:
        raise APITesterGetDataException(get_data_error_message)


def send_httpx_requests(http_method: str, test_url: str, verify: bool = False, timeout: int = 5, **kwargs) -> Response:
    """
    發送 HTTP 請求，支援多種方法 (GET, POST, PUT...)
    Send HTTP request with multiple methods (GET, POST, PUT...)
    :param http_method: 使用的 HTTP 方法 / HTTP method used
    :param test_url: 測試的 URL / URL to test
    :param verify: 是否驗證 SSL / Whether to verify SSL
    :param timeout: 請求逾時秒數 / Request timeout in seconds
    :param kwargs: 其他參數 / Additional parameters
    :return: Response 物件 / Response object
    """
    apitestka_logger.info(
        "httpx_method.py get_httpx_response "
        f"http_method: {http_method} "
        f"test_url: {test_url} "
        f"verify: {verify} "
        f"timeout: {timeout} "
        f"kwargs: {kwargs}"
    )
    method = get_http_method_httpx(http_method)
    if method is None:
        apitestka_logger.error(
            f"httpx send_httpx_requests failed. {APITesterException(wrong_http_method_error_message)}")
        raise APITesterException(wrong_http_method_error_message)
    else:
        response = method(test_url, verify=verify, timeout=timeout, **kwargs)
    return response


def test_api_method_httpx(http_method: str, test_url: str, record_request_info: bool = True,
                          clean_record: bool = False, result_check_dict: dict = None,
                          verify: bool = False, timeout: int = 5,
                          **kwargs) -> dict[str, Response | dict[str, str]] | None:
    """
    測試 API 方法，記錄請求與回應，並可進行結果檢查
    Test API method, record request/response, and optionally check result
    """
    apitestka_logger.info(
        "httpx_method.py test_api_method_httpx "
        f"http_method: {http_method} "
        f"test_url: {test_url} "
        f"record_request_info: {record_request_info} "
        f"clean_record: {clean_record} "
        f"result_check_dict: {result_check_dict} "
        f"verify: {verify} "
        f"timeout: {timeout} "
        f"kwargs: {kwargs}"
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
            repr(error)
        ])