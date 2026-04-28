==================
MCP Server(Claude)
==================

APITestka 內建 Model Context Protocol server,Claude Code(以及其他
MCP-compatible client)能直接把這個框架當成 tool 使用。實作站在 optional
``mcp`` Python SDK 上;tool 派發跟網路層解耦,所以單元測試可以直接呼叫。

安裝
----

.. code-block:: bash

   pip install 'je_api_testka[mcp]'

啟動方式
--------

三種等價寫法:

.. code-block:: bash

   apitestka-mcp
   apitestka mcp
   python -m je_api_testka.mcp_server

伺服器走標準 MCP stdio transport,直到 client 斷線為止。

曝露的 tool
-----------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Tool
     - 用途
   * - ``apitestka_run_action``
     - 執行 executor action list
   * - ``apitestka_test_api``
     - 一次性 HTTP 請求(走 ``requests`` 後端)
   * - ``apitestka_curl_to_action``
     - cURL → action JSON
   * - ``apitestka_har_import``
     - HAR 檔 → action list
   * - ``apitestka_render_markdown``
     - 從目前測試紀錄產 Markdown 報告
   * - ``apitestka_records_to_openapi``
     - 反推 OpenAPI 3.x 文件
   * - ``apitestka_clear_records``
     - 清空測試紀錄
   * - ``apitestka_get_records``
     - 拿目前的成功 / 失敗紀錄

Claude Code 設定
----------------

加進 ``~/.claude/mcp.json``:

.. code-block:: json

   {
     "mcpServers": {
       "apitestka": {
         "command": "apitestka-mcp"
       }
     }
   }

直接呼叫 dispatch
-----------------

.. code-block:: python

   from je_api_testka.mcp_server import dispatch_tool

   dispatch_tool("apitestka_run_action", {"actions": [["AT_fake_uuid"]]})
   dispatch_tool("apitestka_render_markdown", {})
