from requests.utils import dict_from_cookiejar


def get_api_response_data(response):
    return {
        "status_code": response.status_code,
        "text": response.text,
        "json": response.json,
        "content": response.content,
        "headers": response.headers,
        "history": response.history,
        "encoding": response.encoding,
        "cookies": dict_from_cookiejar(response.cookies),
        "elapsed": response.elapsed,
        "request_time_sec": response.elapsed.total_seconds(),
        "request_method": response.request.method,
        "request_url": response.request.url,
        "request_body": response.request.body
    }
