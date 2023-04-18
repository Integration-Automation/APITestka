GET API Data API
----

.. code-block:: python

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