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

套件閘門
--------

``AT_add_package_to_executor`` 與 ``AT_add_package_to_callback_executor`` 會匯入 Python 套件，
並把它的成員註冊成命令，所以只要 action 檔（或 socket 用戶端）寫得出 ``os``、``subprocess``，
就能執行任何東西。哪些套件可以載入，由宿主程式決定：

.. code-block:: python

   from je_api_testka import executor

   executor.allow_packages("my_helpers")          # 這些套件與其子模組
   executor.set_allow_arbitrary_packages(False)   # 其他套件在匯入前就拒絕

這兩個開關都不是 action 命令，所以 action 檔不能自己打開閘門。被拒絕的套件會以
``APITesterExecuteException`` 記錄在該動作的結果裡。``set_allow_arbitrary_packages(True)``
則載入任何套件、不發警告。

宿主程式呼叫任一個開關之前，任何套件仍會載入，但會發出 ``DeprecationWarning``；
之後的版本會預設拒絕允許清單以外的套件。
