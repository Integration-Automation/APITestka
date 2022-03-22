==================
APITestka Http Method Doc
==================

.. code-block:: python

    def api_tester_method(http_method: str, test_url: str, **kwargs):
    """
    http method:
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
    "session_options": session.options
    test_url: url
    """
    def test_api_method(http_method: str, test_url: str,
                    soap: bool = False, record_request_info: bool = True,
                    clean_record: bool = False, result_check_dict: dict = None, **kwargs):
    """
    http_method and test_url as same as api_tester_method
    soap: type is soap True or False
    record_request_info: enable record True or False
    clean_record: clean record list True or False
    result_check_dict: iter and check value on result_check_dict
    """
