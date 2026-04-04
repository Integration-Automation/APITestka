===========================
APITestka 中文文件
===========================

輕量級、跨平台的自動化 API 測試框架。
支援 HTTP/HTTPS、SOAP/XML 和 JSON，具備高效能的請求執行、
詳細的報告產生功能，以及靈活的 CLI 腳本支援。

功能特色
--------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - 類別
     - 說明
   * - **HTTP 用戶端**
     - ``requests`` （同步、支援 Session）與 ``httpx`` （同步 + 非同步、HTTP/2）
   * - **協定**
     - HTTP、HTTPS、SOAP/XML、JSON
   * - **報告格式**
     - HTML、JSON、XML
   * - **腳本化**
     - 透過 Executor 進行 JSON 關鍵字驅動測試執行
   * - **模擬伺服器**
     - 內建基於 Flask 的模擬伺服器，用於本地測試
   * - **遠端自動化**
     - TCP Socket 伺服器，支援遠端命令執行
   * - **斷言**
     - 內建回應欄位斷言（狀態碼、標頭、內容等）
   * - **回呼系統**
     - API 呼叫完成後執行回呼函式
   * - **CLI**
     - 完整的命令列介面，支援 CI/CD 整合
   * - **專案腳手架**
     - 自動產生專案結構與範本
   * - **GUI**
     - 選用的 PySide6 GUI（透過 ``pip install je_api_testka[gui]`` 安裝）
   * - **跨平台**
     - Windows、macOS、Linux

.. toctree::
   :maxdepth: 2
   :caption: 使用者指南

   doc/installation/installation_doc
   doc/quick_start/quick_start_doc
   doc/getting_started/getting_started_doc
   doc/assertion/assertion_doc
   doc/report/report_doc
   doc/mock_server/mock_server_doc
   doc/callback/callback_doc
   doc/executor/executor_doc
   doc/cli/cli_doc
   doc/socket_server/socket_server_doc
   doc/project/project_doc
   doc/test_record/test_record_doc
