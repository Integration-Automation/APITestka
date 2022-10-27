from json import JSONDecodeError

from requests import Response
from requests.utils import dict_from_cookiejar


def get_api_response_data(response: Response,
                          start_time: [str, float, int],
                          end_time: [str, float, int]) -> dict:
    """
    use requests response to create data dict
    :param response: requests response
    :param start_time: test start time
    :param end_time: test end time
    :return: data dict include [status_code, text, content, headers, history, encoding, cookies,
    elapsed, request_time_sec, request_method, request_url, request_body, start_time, end_time]
    """
    response_data = {
        "status_code": str(response.status_code),
        "text": str(response.text).encode("utf-8"),
        "content": str(response.content).encode("utf-8"),
        "headers": str(response.headers).encode("utf-8"),
        "history": str(response.history).encode("utf-8"),
        "encoding": str(response.encoding).encode("utf-8"),
        "cookies": str(dict_from_cookiejar(response.cookies)).encode("utf-8"),
        "elapsed": str(response.elapsed).encode("utf-8"),
        "request_time_sec": str(response.elapsed.total_seconds()).encode("utf-8"),
        "request_method": str(response.request.method).encode("utf-8"),
        "request_url": str(response.request.url).encode("utf-8"),
        "request_body": str(response.request.body).encode("utf-8"),
        "start_time": str(start_time).encode("utf-8"),
        "end_time": str(end_time).encode("utf-8")
    }
    try:
        if response_data.get("status_code") == 200:
            response_data.update({"json": response.json()})
        else:
            response_data.update({"json": None})
    except JSONDecodeError:
        response_data.update({"json": None})
    return response_data
