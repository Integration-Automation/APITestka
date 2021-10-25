from requests import get
from requests import put
from requests import patch
from requests import post
from requests import head
from requests import patch
from requests import delete
from requests import options


def get_http_method(http_method):
    return {"get": get, "put": put, "patch": patch, "post": post, "head": head, "delete": delete, "options": options}.get(http_method)


def api_tester_method(http_method, test_url, data=None, **kwargs):
    if kwargs is None:
        if http_method in ["post"]:
            response = get_http_method(http_method)(test_url, data)
        else:
            response = get_http_method(http_method)(test_url)
    else:
        if http_method in ["post"]:
            response = get_http_method(http_method)(test_url, data, **kwargs)
        else:
            response = get_http_method(http_method)(test_url, **kwargs)
    return response
