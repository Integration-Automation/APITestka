Generate Report
----

* Generate Report can generate reports in the following formats:
 * HTML
 * JSON
 * XML

* Generate Report is mainly used to record and confirm which steps were executed and whether they were successful or not.
* The following example is used with keywords and an executor. If you don't understand, please first take a look at the executor.

Here's an example of generating an HTML report.

.. code-block:: python

    from je_api_testka import generate_html
    from je_api_testka import generate_html_report
    from je_api_testka import execute_action

    test_action_list = [
        ["AT_test_api_method",
         {"http_method": "get", "test_url": "http://httpbin.org/get",
          "headers": {
              "x-requested-with": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
          }
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 200}
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 300}
          }
         ]
    ]
    execute_action(test_action_list)
    generate_html()
    generate_html_report()

Here's an example of generating an JSON report.

.. code-block:: python

    from je_api_testka import generate_json, generate_json_report
    from je_api_testka import execute_action
    test_action_list = [
        ["AT_test_api_method",
         {"http_method": "get", "test_url": "http://httpbin.org/get",
          "headers": {
              "x-requested-with": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
          }
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 200}
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 300}
          }
         ]
    ]
    execute_action(test_action_list)
    generate_json()
    generate_json_report()

Here's an example of generating an XML report.

.. code-block:: python

    from je_api_testka import generate_xml, generate_xml_report
    from je_api_testka import execute_action
    test_action_list = [
        ["AT_test_api_method",
         {"http_method": "get", "test_url": "http://httpbin.org/get",
          "headers": {
              "x-requested-with": "XMLHttpRequest",
              "Content-Type": "application/x-www-form-urlencoded",
              "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
          }
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 200}
          }
         ],
        ["AT_test_api_method",
         {"http_method": "post", "test_url": "http://httpbin.org/post", "params": {"task": "new task"},
          "result_check_dict": {"status_code": 300}
          }
         ]
    ]
    execute_action(test_action_list)
    generate_xml()
    generate_xml_report()
