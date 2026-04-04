==========
報告產生
==========

報告從全域的 ``test_record_instance`` 產生，所有測試結果會自動記錄。

支援格式：**HTML**、**JSON**、**XML**。

HTML 報告
---------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_html_report

   test_api_method_requests("get", "http://httpbin.org/get")
   test_api_method_requests("post", "http://httpbin.org/post")

   # 產生 "my_report.html"，包含成功/失敗表格
   generate_html_report("my_report")

JSON 報告
---------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_json_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # 產生 "my_report_success.json" 和 "my_report_failure.json"
   generate_json_report("my_report")

XML 報告
--------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_xml_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # 產生 "my_report_success.xml" 和 "my_report_failure.xml"
   generate_xml_report("my_report")

搭配 Executor 使用
-------------------

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
