===========================
APITestka Documentation
===========================

A lightweight, cross-platform framework for automated API testing.
Supports HTTP/HTTPS, SOAP/XML, and JSON with high-performance request execution,
detailed reporting, and flexible CLI scripting.

Features
--------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Category
     - Details
   * - **HTTP Clients**
     - ``requests`` (sync, session support) and ``httpx`` (sync + async, HTTP/2)
   * - **Protocols**
     - HTTP, HTTPS, SOAP/XML, JSON
   * - **Report Formats**
     - HTML, JSON, XML
   * - **Scripting**
     - JSON keyword-driven test execution via Executor
   * - **Mock Server**
     - Built-in Flask-based mock server for local testing
   * - **Remote Automation**
     - TCP socket server for remote command execution
   * - **Assertions**
     - Built-in response field assertion (status code, headers, body, etc.)
   * - **Callback System**
     - Execute callback functions after API calls
   * - **CLI**
     - Full command-line interface for CI/CD integration
   * - **Project Scaffolding**
     - Auto-generate project structure with templates
   * - **GUI**
     - Optional PySide6 GUI (install with ``pip install je_api_testka[gui]``)
   * - **Cross-Platform**
     - Windows, macOS, Linux

.. toctree::
   :maxdepth: 2
   :caption: User Guide

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
