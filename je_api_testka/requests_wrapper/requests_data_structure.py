from requests import delete
from requests import get
from requests import head
from requests import options
from requests import patch
from requests import post
from requests import put


def get_http_method(http_method):
    return {
        "get": get,
        "put": put,
        "patch": patch,
        "post": post,
        "head": head,
        "delete": delete,
        "options": options
    }.get(http_method)


def api_tester_method(http_method, test_url, **kwargs):
    if kwargs is None:
        response = get_http_method(http_method)(test_url)
    else:
        response = get_http_method(http_method)(test_url, **kwargs)
    return response
