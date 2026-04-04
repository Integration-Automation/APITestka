==============
腳本化執行器
==============

Executor 實現了 JSON 關鍵字驅動測試，測試動作以 JSON 陣列定義，
並透過程式化方式執行。

JSON 關鍵字驅動測試
--------------------

建立一個 JSON 檔案（例如 ``test_actions.json``）：

.. code-block:: json

   {
       "api_testka": [
           ["AT_test_api_method", {
               "http_method": "get",
               "test_url": "http://httpbin.org/get",
               "result_check_dict": {"status_code": 200}
           }],
           ["AT_test_api_method", {
               "http_method": "post",
               "test_url": "http://httpbin.org/post",
               "params": {"task": "new task"},
               "result_check_dict": {"status_code": 200}
           }]
       ]
   }

透過 Python 執行 JSON 檔案
----------------------------

.. code-block:: python

   from je_api_testka import execute_action, read_action_json

   execute_action(read_action_json("test_actions.json"))

執行整個目錄的 JSON 檔案
--------------------------

.. code-block:: python

   from je_api_testka import execute_files, get_dir_files_as_list

   execute_files(get_dir_files_as_list("path/to/json_dir"))

新增自訂命令
-------------

.. code-block:: python

   from je_api_testka import add_command_to_executor, execute_action

   def my_custom_function(url):
       print(f"自訂測試：{url}")

   add_command_to_executor({"my_test": my_custom_function})

   execute_action([
       ["my_test", ["http://example.com"]]
   ])

內建 Executor 命令
-------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - 命令
     - 說明
   * - ``AT_test_api_method``
     - 使用 requests 後端測試 API
   * - ``AT_test_api_method_httpx``
     - 使用 httpx 同步後端測試 API
   * - ``AT_delegate_async_httpx``
     - 使用 httpx 非同步後端測試 API（同步呼叫）
   * - ``AT_generate_html``
     - 產生 HTML 報告資料
   * - ``AT_generate_html_report``
     - 產生 HTML 報告檔案
   * - ``AT_generate_json``
     - 產生 JSON 報告資料
   * - ``AT_generate_json_report``
     - 產生 JSON 報告檔案
   * - ``AT_generate_xml``
     - 產生 XML 報告資料
   * - ``AT_generate_xml_report``
     - 產生 XML 報告檔案
   * - ``AT_execute_action``
     - 執行巢狀動作列表
   * - ``AT_execute_files``
     - 從多個檔案執行動作
   * - ``AT_add_package_to_executor``
     - 動態載入套件到執行器
   * - ``AT_add_package_to_callback_executor``
     - 動態載入套件到回呼執行器
   * - ``AT_flask_mock_server_add_router``
     - 新增路由到模擬伺服器
   * - ``AT_start_flask_mock_server``
     - 啟動模擬伺服器
