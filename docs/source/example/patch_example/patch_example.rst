==================
APITestka Patch Example
==================

.. code-block:: python

    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: patch
        url: http://httpbin.org/patch
        response status_code request status code
        response elapsed request time unit request.time
        send patch with params
        """
        test_response = test_api_method("patch", "http://httpbin.org/patch", params={"task": "new task"})
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
