Requests Wrapper API
----

.. code-block:: python

    def get_http_method(http_method: str) -> [
    requests.get, requests.put, requests.patch, requests.post, requests.head, requests.delete,
    Session.get, Session.put, Session.patch, Session.post, Session.head, Session.head, Session.options
    ]:
        """
        :param http_method: what http method we use to api test
        :return: one of method in http_method_dict if not exists will raise exception
        """

.. code-block:: python

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