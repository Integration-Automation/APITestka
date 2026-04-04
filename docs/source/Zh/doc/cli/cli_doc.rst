=============
命令列介面
=============

APITestka 提供完整的 CLI 介面，支援 CI/CD 整合。

命令
----

執行單一 JSON 動作檔案：

.. code-block:: bash

   python -m je_api_testka -e test_actions.json

執行目錄中所有 JSON 檔案：

.. code-block:: bash

   python -m je_api_testka -d path/to/json_dir

直接執行 JSON 字串：

.. code-block:: bash

   python -m je_api_testka --execute_str '[["AT_test_api_method", {"http_method": "get", "test_url": "http://httpbin.org/get"}]]'

建立新專案（含範本）：

.. code-block:: bash

   python -m je_api_testka -c MyProject

CLI 參數
--------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 參數
     - 說明
   * - ``-e``, ``--execute_file``
     - 執行單一 JSON 動作檔案
   * - ``-d``, ``--execute_dir``
     - 執行目錄中所有 JSON 檔案
   * - ``--execute_str``
     - 直接執行 JSON 字串
   * - ``-c``, ``--create_project``
     - 建立專案目錄及範本檔案
