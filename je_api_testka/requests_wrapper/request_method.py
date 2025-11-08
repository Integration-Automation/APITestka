from datetime import datetime
from typing import Dict, Union, Optional

import requests
from requests import Session
from requests import delete, get, head, options, patch, post, put
from requests.structures import CaseInsensitiveDict

from je_api_testka.utils.assert_result.result_check import check_result
from je_api_testka.utils.exception.exception_tags import (
    get_data_error_message,
    http_method_have_wrong_type,
    wrong_http_method_error_message,
)
from je_api_testka.utils.exception.exceptions import APITesterException, APITesterGetDataException
from je_api_testka.requests_wrapper.requests_data import get_requests_data
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.test_record.test_record_class import test_record_instance

# 建立 Session 物件，用於持久化連線
# Create Session object for persistent connections
_session = Session()

# 定義 HTTP 方法字典，包含 requests 與 session 方法
# Define HTTP method dictionary including requests and session methods
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


def get_http_method(http_method: str):
    """
    根據字串取得對應的 HTTP 方法，若不存在則拋出例外
    Get corresponding HTTP method from string, raise exception if not exists
    """
    apitestka_logger.info("request_method.py get_http_method")
    try:
        if not isinstance(http_method, str):
            apitestka_logger.error(
                f"requests get_http_method failed. {APITesterException(wrong_http_method_error_message)}"
            )
            raise APITesterException(wrong_http_method_error_message)
        http_method = str(http_method).lower()
        if http_method not in http_method_dict:
            apitestka_logger.error(
                f"requests get_http_method failed. {APITesterException(http_method_have_wrong_type)}"
            )
            raise APITesterException(http_method_have_wrong_type)
        return http_method_dict.get(http_method)
    except APITesterException as error:
        apitestka_logger.error(f"requests get_http_method failed. {repr(error)}")


def send_requests(http_method: str, test_url: str, verify: bool = False, timeout: int = 5,
                  allow_redirects: bool = False, **kwargs) -> requests.Response:
    """
    發送 HTTP 請求，支援多種方法 (GET, POST, PUT...)
    Send HTTP request with multiple methods (GET, POST, PUT...)
    :param http_method: 使用的 HTTP 方法 / HTTP method used
    :param test_url: 測試的 URL / URL to test
    :param verify: 是否驗證 SSL / Whether to verify SSL
    :param timeout: 請求逾時秒數 / Request timeout in seconds
    :param allow_redirects: 是否允許重導 / Allow redirects
    :param kwargs: 其他參數 / Additional parameters
    :return: Response 物件 / Response object
    """
    apitestka_logger.info(
        "request_method.py get_http_method "
        f"http_method: {http_method} test_url: {test_url} verify: {verify} "
        f"timeout: {timeout} allow_redirects: {allow_redirects} kwargs: {kwargs}"
    )
    method = get_http_method(http_method)
    if method is None:
        apitestka_logger.error(
            f"requests api_tester_method failed. {APITesterException(wrong_http_method_error_message)}"
        )
        raise APITesterException(wrong_http_method_error_message)
    else:
        response = method(test_url, verify=verify, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
    return response


def get_response(response: requests.Response,
                 start_time: Union[str, float, int, datetime],
                 end_time: Union[str, float, int, datetime]) -> Dict[str, str]:
    """
    將 requests Response 轉換成字典，包含狀態碼、內容、標頭、cookies 等資訊
    Convert requests Response into dictionary including status code, content, headers, cookies, etc.
    """
    apitestka_logger.info(
        "request_method.py get_response "
        f"response: {response} start_time: {start_time} end_time: {end_time}"
    )
    try:
        return get_requests_data(response, start_time, end_time)
    except APITesterGetDataException:
        raise APITesterGetDataException(get_data_error_message)


def test_api_method_requests(http_method: str, test_url: str,
                             soap: bool = False, record_request_info: bool = True,
                             clean_record: bool = False, result_check_dict: dict = None,
                             verify: bool = False, timeout: int = 5, allow_redirects: bool = False,
                             **kwargs) -> Optional[requests.Response, Dict[str, str]]:
    """
    測試 API 方法，記錄請求與回應，並可進行結果檢查
    Test API method, record request/response, and optionally check result
    """
    apitestka_logger.info(
        "request_method.py test_api_method_requests "
        f"http_method: {http_method} test_url: {test_url} soap: {soap} "
        f"record_request_info: {record_request_info} clean_record: {clean_record} "
        f"result_check_dict: {result_check_dict} verify: {verify} timeout: {timeout} "
        f"allow_redirects: {allow_redirects} kwargs: {kwargs}"
    )
    try:
        start_time: datetime = datetime.now()
        if soap is False:
            # 一般 HTTP 請求 / Normal HTTP request
            response = send_requests(http_method, test_url=test_url, verify=verify, timeout=timeout,
                                     allow_redirects=allow_redirects, **kwargs)
        else:
            # SOAP 請求，設定 Content-Type / SOAP request with Content-Type header
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
            repr(error)
        ])