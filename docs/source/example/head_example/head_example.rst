==================
APITestka Head Example
==================

.. code-block:: python

    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: head
        url: http://httpbin.org/get
        return response_data structure
        set headers
        response_data all response
        response status_code request status code
        response elapsed request time unit request.time
        """
        test_response = test_api_method("head", "http://httpbin.org/get", headers={
            'x-requested-with': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
        })
        print(test_response.get("response_data"))
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("elapsed"))
