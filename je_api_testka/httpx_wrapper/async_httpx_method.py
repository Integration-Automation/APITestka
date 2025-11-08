import asyncio
from datetime import datetime
from typing import Dict, Union, Optional

from httpx import get, put, patch, post, head, delete, Response, AsyncClient

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

# 定義 HTTP 方法字典，對應到 AsyncClient 的方法
# Define HTTP method dictionary mapping to AsyncClient methods
http_method_dict = {
    "get": AsyncClient.get,
    "put": AsyncClient.put,
    "patch": AsyncClient.patch,
    "post": AsyncClient.post,
    "head": AsyncClient.head,
    "delete": AsyncClient.delete,
    "options": AsyncClient.options,
}


async def get_http_method_httpx_async(http_method: str) -> Optional[get, put, patch, post, head, delete]:
    """
    根據字串取得對應的 HTTP 方法，若不存在則拋出例外
    Get corresponding HTTP method from string, raise exception if not exists
    """
    apitestka_logger.info(f"async_httpx_method.py get_http_method_httpx_async http_method: {http_method}")
    try:
        if not isinstance(http_method, str):
            raise APITesterException(wrong_http_method_error_message)
        http_method = str(http_method).lower()
        if http_method not in http_method_dict:
            raise APITesterException(http_method_have_wrong_type)
        return http_method_dict.get(http_method)
    except APITesterException as error:
        apitestka_logger.error(f"httpx get_http_method_httpx_async failed. {repr(error)}")


async def get_httpx_response_async(
    response: Response, start_time: Union[str, float, int, datetime], end_time: Union[str, float, int, datetime]
) -> Dict[str, str]:
    """
    將 HTTPX Response 轉換成字典，包含狀態碼、內容、標頭等資訊
    Convert HTTPX Response into dictionary including status code, content, headers, etc.
    """
    apitestka_logger.info(
        "async_httpx_method.py get_httpx_response_async "
        f"response: {response} start_time: {start_time} end_time: {end_time}"
    )
    try:
        return get_httpx_data(response, start_time, end_time)
    except APITesterGetDataException:
        apitestka_logger.error(
            f"get_httpx_response_async failed. {APITesterGetDataException(get_data_error_message)}"
        )
        raise APITesterGetDataException(get_data_error_message)


async def send_httpx_requests_async(
    http_method: str, test_url: str, timeout: int = 5, http2: bool = False, **kwargs
) -> Response:
    """
    發送 HTTP 請求，支援多種方法 (GET, POST, PUT...)
    Send HTTP request with multiple methods (GET, POST, PUT...)
    """
    apitestka_logger.info(
        "async_httpx_method.py send_httpx_requests_async "
        f"http_method: {http_method} test_url: {test_url} timeout: {timeout} http2: {http2} kwargs: {kwargs}"
    )
    method = await get_http_method_httpx_async(http_method)
    if method is None:
        apitestka_logger.error(
            f"httpx send_httpx_requests_async failed. {APITesterException(wrong_http_method_error_message)}"
        )
        raise APITesterException(wrong_http_method_error_message)
    else:
        async with AsyncClient(http2=http2) as client:
            # 建立 client 方法字典，確保正確呼叫
            # Create client method dictionary to ensure correct call
            client_method_dict = {
                "get": client.get,
                "put": client.put,
                "patch": client.patch,
                "post": client.post,
                "head": client.head,
                "delete": client.delete,
                "options": client.options,
            }
            method = client_method_dict.get(http_method)
            response = await method(url=test_url, timeout=timeout, **kwargs)
    return response


async def test_api_method_httpx_async(
    http_method: str,
    test_url: str,
    record_request_info: bool = True,
    clean_record: bool = False,
    result_check_dict: dict = None,
    timeout: int = 5,
    http2: bool = False,
    **kwargs,
) -> Optional[Response, Dict[str, str]]:
    """
    測試 API 方法，記錄請求與回應，並可進行結果檢查
    Test API method, record request/response, and optionally check result
    """
    apitestka_logger.info(
        "async_httpx_method.py test_api_method_httpx_async "
        f"http_method: {http_method} test_url:{test_url} record_request_info: {record_request_info} "
        f"clean_record: {clean_record} result_check_dict: {result_check_dict} timeout: {timeout} kwargs: {kwargs}"
    )
    try:
        start_time: datetime = datetime.now()
        end_time = datetime.now()
        response = await send_httpx_requests_async(
            http_method, test_url=test_url, timeout=timeout, http2=http2, **kwargs
        )
        response_data = await get_httpx_response_async(response, start_time, end_time)
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
            "async_httpx_method.py test_api_method_httpx_async "
            f"http_method: {http_method} test_url:{test_url} record_request_info: {record_request_info} "
            f"clean_record: {clean_record} result_check_dict: {result_check_dict} timeout: {timeout} kwargs: {kwargs} "
            f"failed: {repr(error)}"
        )
        test_record_instance.error_record_list.append(
            [
                {
                    "http_method": http_method,
                    "test_url": test_url,
                    "record_request_info": record_request_info,
                    "clean_record": clean_record,
                    "result_check_dict": result_check_dict,
                },
                repr(error),
            ]
        )


def delegate_async_httpx(
    http_method: str,
    test_url: str,
    record_request_info: bool = True,
    clean_record: bool = False,
    result_check_dict: dict = None,
    timeout: int = 5,
    **kwargs,
) -> Optional[Response, Dict[str, str]]:
    """
    同步呼叫非同步 API 測試方法，方便在非 async 環境使用
    Run async API test method synchronously, useful in non-async environments
    """
    apitestka_logger.info(
        "async_httpx_method.py delegate_async_httpx "
        f"http_method: {http_method} test_url:{test_url} record_request_info: {record_request_info} "
        f"clean_record: {clean_record} result_check_dict: {result_check_dict} timeout: {timeout} kwargs: {kwargs}"
    )
    return asyncio.run(
        test_api_method_httpx_async(
            http_method, test_url, record_request_info, clean_record, result_check_dict, timeout, **kwargs
        )
    )