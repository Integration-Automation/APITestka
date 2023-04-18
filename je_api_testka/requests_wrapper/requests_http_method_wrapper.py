import sys

import requests
from requests import Session
from requests import delete
from requests import get
from requests import head
from requests import options
from requests import patch
from requests import post
from requests import put

from je_api_testka.utils.exception.exception_tags import http_method_have_wrong_type
from je_api_testka.utils.exception.exception_tags import wrong_http_method_error_message
from je_api_testka.utils.exception.exceptions import APITesterException

_session = Session()

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


def get_http_method(http_method: str) -> [
    requests.get, requests.put, requests.patch, requests.post, requests.head, requests.delete,
    Session.get, Session.put, Session.patch, Session.post, Session.head, Session.head, Session.options
]:
    """
    :param http_method: what http method we use to api test
    :return: one of method in http_method_dict if not exists will raise exception
    """
    try:
        if not isinstance(http_method, str):
            raise APITesterException(wrong_http_method_error_message)
        http_method = str(http_method).lower()
        if http_method not in http_method_dict:
            raise APITesterException(http_method_have_wrong_type)
        return http_method_dict.get(http_method)
    except APITesterException as error:
        print(repr(error), file=sys.stderr)


def api_tester_method(http_method: str, test_url: str, verify: bool = False, timeout: int = 5,
                      allow_redirects: bool = False, **kwargs) -> requests.Response:
    """
    :param http_method: what http method we use to api test
    :param test_url: what url we want to test
    :param kwargs: use to setting param
    :param verify: this connect need verify or not
    :param timeout: timeout sec
    :param allow_redirects: allow to redirects to another request
    :return: test response
    """
    response = get_http_method(http_method)
    if response is None:
        raise APITesterException(wrong_http_method_error_message)
    else:
        response = response(test_url, verify=verify, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
    return response
