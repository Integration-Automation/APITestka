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

子命令 CLI
--------------

安裝套件後會有 ``apitestka`` 指令，把常用工作集中在一起：

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 子命令
     - 說明
   * - ``run PATH``
     - 執行一個動作 JSON 檔，或目錄裡每個 JSON 檔
   * - ``create PATH``
     - 建立專案目錄
   * - ``mock [--host] [--port] [--config]``
     - 啟動 Flask 模擬伺服器；``--config`` 另外加上 WebSocket 與 gRPC 端點（見模擬伺服器一章）
   * - ``import INPUT OUTPUT [--format openapi|postman]``
     - 把 OpenAPI 文件或 Postman collection 轉成動作 JSON
   * - ``repl``
     - 互動式 JSON 動作 REPL
   * - ``summary``
     - 在終端機印出最近一次執行的摘要
   * - ``scaffold URL OUTPUT [--method]``
     - 為一個 URL 寫出起始的動作 JSON
   * - ``completion SHELL``
     - 印出 bash、zsh、fish 或 PowerShell 的補全腳本
   * - ``mcp``
     - 以 stdio 啟動 MCP server
   * - ``openapi``
     - 從錄下的流量反推 OpenAPI 文件（見下節）
   * - ``contract record|verify|compare``
     - 產生、驗證與比對 Pact 風格消費者契約（見契約測試一章）
   * - ``generate-tests SPEC [-o OUT] [--ai noop|anthropic] [--model] [--effort]``
     - 為 OpenAPI 文件產生測試 action（見可插拔 AI 後端一章）
   * - ``load convert|run``
     - 把 APITestka 的請求轉成或跑成 LoadDensity 負載測試（見生態整合一章）
   * - ``trend record|check|report``
     - 記錄各端點延遲、檢查最近一次執行是否異常（異常時結束碼 1）、寫出 HTML 趨勢報告
   * - ``spec check SPEC``
     - 拿已提交的 OpenAPI 文件和測試比對：偏移、覆蓋率、缺少的測試（見測試即規格迴路一章）

反推 OpenAPI 文件
----------------------

``apitestka openapi`` 用成功的請求建出 OpenAPI 3.1 文件。來源可以是存下的 JSON 成功報告
（``generate_json_report`` 產生的 ``<name>_success.json``）、先執行的動作檔，或兩者都給；每個選項都可以重複。

.. code-block:: bash

   apitestka openapi --report run_success.json -o openapi.json
   apitestka openapi --run tests/ --title "Shop API" --api-version 2.0

沒有 ``-o`` 時文件印到 stdout。沒給任何來源、或 ``--run`` 的路徑不存在時結束碼是 2；
找不到任何成功紀錄時結束碼是 1，而且不寫檔。
