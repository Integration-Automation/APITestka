from requests import delete
from requests import get
from requests import head
from requests import options
from requests import patch
from requests import post
from requests import put
from requests import Session

session = Session()


def get_http_method(http_method: str):
    return {
        "get": get,
        "put": put,
        "patch": patch,
        "post": post,
        "head": head,
        "delete": delete,
        "options": options,
        "session_get": session.get,
        "session_put": session.put,
        "session_patch": session.patch,
        "session_post": session.post,
        "session_head": session.head,
        "session_delete": session.delete,
        "session_options": session.options,
    }.get(http_method)


def api_tester_method(http_method: str, test_url: str, **kwargs):
    if kwargs is None:
        response = get_http_method(http_method)(test_url)
    else:
        response = get_http_method(http_method)(test_url, **kwargs)
    return response
