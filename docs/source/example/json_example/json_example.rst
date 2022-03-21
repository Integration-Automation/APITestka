==================
APITestka Json Example
==================

.. code-block:: python

    from je_api_testka import APITesterException
    from je_api_testka import reformat_json
    from je_api_testka import read_action_json
    from je_api_testka import write_action_json
    from je_api_testka import test_api_method

    if __name__ == "__main__":
        """
        http method: get
        url: http://httpbin.org/get
        try to get json and print
        reformat_json: reformat one line json str to pretty json string
        write_action_json: write action list to action file
        read_action_json: read action json
        """
        test_response = test_api_method("get", "http://httpbin.org/get")
        print(reformat_json(test_response.get("response_data").get("json_data")))
        test_json_string = '[["get", "http://httpbin.org/get", false, {"headers": {"x-requested-with": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded", "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36"}}], ["post", "http://httpbin.org/post", false, {"params": {"task": "new task"}}]]'
        print(reformat_json(test_json_string))

        test_list = \
    [
        ["test_api_method",
         {"http_method": "get", "test_url": "http://httpbin.org/get",
          "headers": {
              'x-requested-with': 'XMLHttpRequest',
              'Content-Type': 'application/x-www-form-urlencoded',
              'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
          }
          }
         ],
        ["test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 200}
          }
         ]
    ]

    write_action_json(os.getcwd() + "/test.json", test_list)
    read_json = reformat_json(read_action_json(os.getcwd() + "/test.json"))
    print(read_json)
