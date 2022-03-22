==================
APITestka Get Example
==================

.. code-block:: python

    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: get
        url: http://httpbin.org/get
        return response_data structure
        response status_code request text status code
        response text: request text
        response headers: request headers
        response content: request content
        response history: request history
        response encoding: request encoding
        response cookies: request cookies
        response elapsed request time unit request.time
        response request_method: request method [GET/POST/DELETE/PUT]... etc
        response json_data: request json
        """
        test_response = test_api_method("get", "http://httpbin.org/get")
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("text"))
        print(test_response.get("response_data").get("headers"))
        print(test_response.get("response_data").get("content"))
        print(test_response.get("response_data").get("history"))
        print(test_response.get("response_data").get("encoding"))
        print(test_response.get("response_data").get("cookies"))
        print(test_response.get("response_data").get("elapsed"))
        print(test_response.get("response_data").get("request_method"))
        print(test_response.get("response_data").get("request_url"))
        print(test_response.get("response_data").get("request_body"))
        test_response = test_api_method("get", "http://httpbin.org/get")
        print(test_response.get("response_data").get("status_code"))
        print(test_response.get("response_data").get("json_data"))
