=================
Report Generation
=================

Reports are generated from the global ``test_record_instance``,
which automatically records all test results.

Supported formats: **HTML**, **JSON**, **XML**.

HTML Report
-----------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_html_report

   test_api_method_requests("get", "http://httpbin.org/get")
   test_api_method_requests("post", "http://httpbin.org/post")

   # Generates "my_report.html" with success/failure tables
   generate_html_report("my_report")

JSON Report
-----------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_json_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # Generates "my_report_success.json" and "my_report_failure.json"
   generate_json_report("my_report")

XML Report
----------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_xml_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # Generates "my_report_success.xml" and "my_report_failure.xml"
   generate_xml_report("my_report")

Using with Executor
-------------------

Reports can also be generated within keyword-driven testing:

.. code-block:: python

   from je_api_testka import execute_action, generate_html, generate_html_report

   test_action_list = [
       ["AT_test_api_method", {
           "http_method": "get",
           "test_url": "http://httpbin.org/get",
           "headers": {
               "x-requested-with": "XMLHttpRequest",
               "Content-Type": "application/x-www-form-urlencoded",
           }
       }],
       ["AT_test_api_method", {
           "http_method": "post",
           "test_url": "http://httpbin.org/post",
           "params": {"task": "new task"},
           "result_check_dict": {"status_code": 200}
       }]
   ]

   execute_action(test_action_list)
   generate_html()
   generate_html_report()
