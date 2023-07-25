from json import JSONDecodeError
from typing import Dict

from httpx import Response
from requests.utils import dict_from_cookiejar


def get_httpx_data(response: Response,
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
    response_data = {
        "status_code": response.status_code,
        "text": response.text,
        "content": response.content,
        "headers": response.headers,
        "history": response.history,
        "encoding": response.encoding,
        "cookies": dict_from_cookiejar(response.cookies),
        "elapsed": response.elapsed,
        "request_time_sec": response.elapsed.total_seconds(),
        "request_method": response.request.method,
        "request_url": response.request.url,
        "request_body": "",
        "start_time": start_time,
        "end_time": end_time
    }
    try:
        if response_data.get("status_code") == 200:
            response_data.update({"json": response.json()})
        else:
            response_data.update({"json": None})
    except JSONDecodeError:
        response_data.update({"json": None})
    return response_data
