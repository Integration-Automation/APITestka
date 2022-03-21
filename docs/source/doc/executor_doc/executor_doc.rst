==================
APITestka Executor Doc
==================

.. code-block:: python

    from je_api_testka import test_record
    from je_api_testka import APITesterExecuteException
    from je_api_testka import execute_action

    test_action_list = [
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

    for action_response in execute_action(test_action_list)[1]:
        response = action_response.get("response_data")
        print(response.get("text"))
        print(response.get("start_time"))
        print(response.get("end_time"))
        assert response.get("start_time") is not None
        assert response.get("end_time") is not None

    print(test_record.record_list)
    print(test_record.error_record_list)