from requests import Session
from requests import delete
from requests import get
from requests import head
from requests import options
from requests import patch
from requests import post
from requests import put

from je_api_testka.utils.exception.api_test_eceptions_tag import wrong_http_method_error_message
from je_api_testka.utils.exception.api_test_exceptions import APITesterException

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
    response = get_http_method(http_method)
    if response is None:
        raise APITesterException(wrong_http_method_error_message)
    else:
        response = response(test_url, **kwargs)
    return response
