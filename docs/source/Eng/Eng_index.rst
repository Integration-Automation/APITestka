===========================
APITestka Documentation
===========================

A lightweight, cross-platform framework for automated API testing.
What started as an HTTP/HTTPS / SOAP-XML / JSON request runner now ships
with variable chaining, OpenAPI / Postman / HAR / cURL importers, a
record-replay proxy, security probes, parallel runners, an MCP server for
Claude, and more.

Features
--------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Category
     - Details
   * - **Backends**
     - ``requests`` (sync, sessions), ``httpx`` (sync + async, HTTP/2),
       WebSocket, SSE, GraphQL
   * - **Data layer**
     - Variable store, ``{{var}}`` templating, CSV/JSON data-driven loops,
       env profiles, fake data
   * - **Assertions**
     - Field assertions, JSON Schema, JSONPath, snapshot, structural diffs,
       OpenAPI contract drift, response-time SLAs
   * - **Connection**
     - mTLS, proxies, DNS override, VCR-style cassette record/replay
   * - **Mock server**
     - Static, dynamic, stateful, fault injection, OpenAPI-driven, Jinja
       templating, webhook receiver, record-replay proxy
   * - **Runner**
     - Sequential & parallel execution, tag filters, dependency-aware
       ordering, retry policies
   * - **Reports**
     - HTML / JSON / XML / JUnit / Allure / Markdown / shields.io badge /
       SQLite trend store / run diff
   * - **Integrations**
     - Slack / Teams / Discord webhook, GitHub PR comment, cURL & HAR
       importers, OpenAPI / Postman importer
   * - **CLI / DX**
     - Subcommand CLI, REPL, terminal summary, shell completion, scaffold
   * - **Security**
     - Auth helpers (Basic / Bearer / JWT / AWS SigV4), header / CORS /
       rate-limit / SSRF probes, pip-audit wrapper, fuzz inputs
   * - **Spec inference**
     - Test record → OpenAPI, JSON Schema inference, OpenAPI changelog
   * - **AI**
     - Pluggable backend with deterministic fallback for test generation,
       fake data, failure classification
   * - **MCP**
     - First-class Claude Code / MCP server exposing the framework as tools
   * - **GUI**
     - Optional PySide6 GUI (English / 繁中 / 简中 / 日本語) plus Swagger UI embed
   * - **Cross-Platform**
     - Windows, macOS, Linux. Python 3.10–3.14

.. toctree::
   :maxdepth: 2
   :caption: User Guide

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
