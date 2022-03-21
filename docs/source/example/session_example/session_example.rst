==================
APITestka Session Example
==================

.. code-block:: python

    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: get with session
        url: http://httpbin.org/get
        response status_code request status code
        response elapsed request time unit request.time
        """

        test_response = test_api_method("session_get", "http://httpbin.org/get")
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
