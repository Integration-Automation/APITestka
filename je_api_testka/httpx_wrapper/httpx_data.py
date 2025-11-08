from json import JSONDecodeError
from typing import Dict, Union

from httpx import Response
from requests.utils import dict_from_cookiejar

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def get_httpx_data(response: Response,
                   start_time: Union[str, float, int],
                   end_time: Union[str, float, int]) -> Dict[str, str]:
    """
    將 HTTPX Response 轉換成字典，包含狀態碼、內容、標頭、cookies 等資訊
    Convert HTTPX Response into dictionary including status code, content, headers, cookies, etc.
    """
    apitestka_logger.info(
        "httpx_data.py get_httpx_data "
        f"response: {response} "
        f"start_time:{start_time} "
        f"end_time: {end_time}"
    )

    # 建立回應資料字典
    # Build response data dictionary
    response_data = {
        "status_code": response.status_code,   # 狀態碼 / HTTP status code
        "text": response.text,                 # 回應文字 / Response text
        "content": response.content,           # 回應內容 (bytes) / Response content (bytes)
        "headers": response.headers,           # 回應標頭 / Response headers
        "history": response.history,           # 請求歷史紀錄 / Request history
        "encoding": response.encoding,         # 編碼方式 / Response encoding
        "cookies": dict_from_cookiejar(response.cookies),  # Cookies 轉換成 dict / Convert cookies to dict
        "elapsed": response.elapsed,           # 請求耗時 / Request elapsed time
        "request_time_sec": response.elapsed.total_seconds(),  # 耗時秒數 / Elapsed time in seconds
        "request_method": response.request.method,  # 請求方法 / Request method
        "request_url": response.request.url,        # 請求 URL / Request URL
        "request_body": "",                         # 請求 Body (預設空) / Request body (default empty)
        "start_time": start_time,                   # 測試開始時間 / Test start time
        "end_time": end_time                        # 測試結束時間 / Test end time
    }

    try:
        # 嘗試解析 JSON，如果狀態碼為 200 則加入 JSON 資料
        # Try to parse JSON, add JSON data if status code is 200
        if response_data.get("status_code") == 200:
            response_data.update({"json": response.json()})
        else:
            response_data.update({"json": None})
    except JSONDecodeError:
        # 若 JSON 解析失敗，設定為 None
        # If JSON parsing fails, set to None
        response_data.update({"json": None})

    return response_data