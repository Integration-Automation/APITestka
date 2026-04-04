==========
開始使用
==========

創建專案
--------

在 APITestka 裡可以創建專案，創建專案後將會自動生成範例文件。
範例文件包含 Python executor 檔案以及 ``keyword.json`` 檔案。

.. code-block:: python

   from je_api_testka import create_project_dir

   # 在當前工作目錄創建
   create_project_dir()

   # 在指定路徑創建
   create_project_dir("project_path")

   # 在指定路徑創建並自訂專案名稱
   create_project_dir("project_path", "My First Project")

或使用 CLI：

.. code-block:: bash

   python -m je_api_testka --create_project project_path

執行 Executor
--------------

進入專案資料夾，到 ``executor`` 資料夾，選擇其中一個 executor 執行。
``keyword`` 資料夾裡的 ``keyword.json`` 檔案定義了要執行的動作。

使用純 Python
--------------

.. note::

   只能使用以下 HTTP Method：
   ``get``、``post``、``put``、``patch``、``delete``、``head``、``options``

.. code-block:: python

   from je_api_testka import execute_action

   test_api_list = [
       ["AT_test_api_method", {
           "http_method": "post",
           "test_url": "http://httpbin.org/post",
           "params": {"task": "new task"},
           "result_check_dict": {"status_code": 200}
       }],
       ["AT_test_api_method", {
           "http_method": "get",
           "test_url": "http://httpbin.org/post",
           "result_check_dict": {"status_code": 405}
       }]
   ]

   execute_action(test_api_list)
