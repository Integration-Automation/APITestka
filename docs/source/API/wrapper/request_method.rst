Request Method
----

.. code-block:: python

    def get_response(response: requests.Response,
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

.. code-block:: python

    def test_api_method(http_method: str, test_url: str,
                    soap: bool = False, record_request_info: bool = True,
                    clean_record: bool = False, result_check_dict: dict = None
                    , verify: bool = False, timeout: int = 5, allow_redirects: bool = False,
                    **kwargs) \
        -> (requests.Response, dict):
        """
        set requests http_method url headers and record response and record report
        :param http_method:
        :param test_url:
        :param soap:
        :param record_request_info:
        :param clean_record:
        :param result_check_dict:
        :param kwargs:
        """