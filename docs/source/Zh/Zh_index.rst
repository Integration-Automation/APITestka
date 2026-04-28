===========================
APITestka 中文文件
===========================

輕量級、跨平台的 Python 自動化 API 測試框架。
最初是 HTTP/HTTPS / SOAP-XML / JSON 請求執行器加上報告與 JSON 驅動的
executor;現在已擴充為一整套工具:變數鏈式 request、OpenAPI / Postman /
HAR / cURL 匯入器、record-replay proxy、安全檢測、平行 runner、給 Claude
用的 MCP server,等等。

功能特色
--------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 類別
     - 內容
   * - **後端**
     - ``requests``(同步、session)、``httpx``(同步 + 非同步、HTTP/2)、
       WebSocket、SSE、GraphQL
   * - **資料層**
     - 變數儲存、``{{var}}`` 模板、CSV/JSON 資料驅動、環境設定檔、假資料
   * - **斷言**
     - 欄位斷言、JSON Schema、JSONPath、Snapshot、結構化 diff、OpenAPI
       contract drift、回應時間 SLA
   * - **連線**
     - mTLS、Proxy、DNS override、VCR-style cassette 錄製/回放
   * - **模擬伺服器**
     - 靜態、動態、stateful、故障注入、OpenAPI 驅動、Jinja 模板、Webhook
       接收、record-replay proxy
   * - **Runner**
     - 順序 & 平行執行、Tag 過濾、Dependency-aware 排序、Retry 策略
   * - **報告**
     - HTML / JSON / XML / JUnit / Allure / Markdown / shields.io badge /
       SQLite 趨勢資料庫 / Run diff
   * - **生態整合**
     - Slack / Teams / Discord webhook、GitHub PR comment、cURL & HAR
       匯入、OpenAPI / Postman 匯入
   * - **CLI / DX**
     - 子命令式 CLI、REPL、終端摘要、Shell completion、Scaffold
   * - **安全**
     - Auth helper(Basic / Bearer / JWT / AWS SigV4)、Header / CORS /
       Rate limit / SSRF probe、pip-audit、Fuzz
   * - **Spec 反推**
     - 測試紀錄 → OpenAPI、JSON Schema 推斷、OpenAPI changelog
   * - **AI**
     - 可插拔後端,LLM 不可用時自動退回確定性 fallback
   * - **MCP**
     - 一級支援 Claude Code,將框架曝露為 MCP 工具
   * - **GUI**
     - 可選 PySide6 GUI(英 / 繁中 / 简中 / 日)+ 嵌入 Swagger UI
   * - **跨平台**
     - Windows、macOS、Linux,Python 3.10–3.14

.. toctree::
   :maxdepth: 2
   :caption: 使用者指南

   doc/installation/installation_doc
   doc/quick_start/quick_start_doc
   doc/getting_started/getting_started_doc
   doc/protocols/protocols_doc
   doc/data_layer/data_layer_doc
   doc/assertion/assertion_doc
   doc/diff/diff_doc
   doc/connection/connection_doc
   doc/runner/runner_doc
   doc/report/report_doc
   doc/mock_server/mock_server_doc
   doc/callback/callback_doc
   doc/executor/executor_doc
   doc/cli/cli_doc
   doc/integrations/integrations_doc
   doc/security_advanced/security_advanced_doc
   doc/socket_server/socket_server_doc
   doc/project/project_doc
   doc/test_record/test_record_doc
   doc/mcp/mcp_doc
