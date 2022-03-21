==================
APITestka Delete Example
==================

.. code-block:: python

    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: delete
        url: http://httpbin.org/delete
        return response_data structure
        response status_code request text status code
        response text request text
        response elapsed request time unit request.time
        test_response.get("response_data").get("elapsed").total_seconds()
        equal test_response.get("response_data").get("request_time_sec")
        : request time (end time - start time) unit sec
        """
        test_response = test_api_method("delete", "http://httpbin.org/delete")
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
        print(test_response.get("response_data").get("elapsed"))
        print(test_response.get("response_data").get("elapsed").total_seconds())
        print(test_response.get("response_data").get("request_time_sec"))