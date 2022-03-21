==================
APITestka Put Example
==================

.. code-block:: python

    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: put
        url: http://httpbin.org/put
        response status_code request status code
        response elapsed request time unit request.time
        send put with params
        """
        test_response = test_api_method("put", "http://httpbin.org/put", params={"task": "new task"})
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
