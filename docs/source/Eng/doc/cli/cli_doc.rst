=========
CLI Usage
=========

APITestka provides a full command-line interface for CI/CD integration.

Commands
--------

Execute a single JSON action file:

.. code-block:: bash

   python -m je_api_testka -e test_actions.json

Execute all JSON files in a directory:

.. code-block:: bash

   python -m je_api_testka -d path/to/json_dir

Execute a JSON string directly:

.. code-block:: bash

   python -m je_api_testka --execute_str '[["AT_test_api_method", {"http_method": "get", "test_url": "http://httpbin.org/get"}]]'

Create a new project with templates:

.. code-block:: bash

   python -m je_api_testka -c MyProject

CLI Flags
---------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Flag
     - Description
   * - ``-e``, ``--execute_file``
     - Execute a single JSON action file
   * - ``-d``, ``--execute_dir``
     - Execute all JSON files in a directory
   * - ``--execute_str``
     - Execute a JSON string directly
   * - ``-c``, ``--create_project``
     - Create a project directory with template files

Subcommand CLI
--------------

The ``apitestka`` command (installed with the package) groups the everyday tasks:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Subcommand
     - Description
   * - ``run PATH``
     - Execute an action JSON file or every JSON file in a directory
   * - ``create PATH``
     - Scaffold a project directory
   * - ``mock [--host] [--port] [--config]``
     - Start the Flask mock server; ``--config`` adds WebSocket and gRPC endpoints (see Mock Server)
   * - ``import INPUT OUTPUT [--format openapi|postman]``
     - Convert an OpenAPI document or Postman collection into action JSON
   * - ``repl``
     - Interactive JSON-action REPL
   * - ``summary``
     - Print a terminal summary of the latest run
   * - ``scaffold URL OUTPUT [--method]``
     - Write a starter action JSON for one URL
   * - ``completion SHELL``
     - Print a completion script for bash, zsh, fish or PowerShell
   * - ``mcp``
     - Run the MCP server over stdio
   * - ``openapi``
     - Infer an OpenAPI document from recorded traffic (below)
   * - ``contract record|verify|compare``
     - Record, verify and compare Pact-style consumer contracts (see Contract Testing)

Inferring an OpenAPI document
-----------------------------

``apitestka openapi`` builds an OpenAPI 3.1 document from successful requests. Give it saved
JSON success reports (the ``<name>_success.json`` file from ``generate_json_report``), action
files to run first, or both; each option can be repeated.

.. code-block:: bash

   apitestka openapi --report run_success.json -o openapi.json
   apitestka openapi --run tests/ --title "Shop API" --api-version 2.0

Without ``-o`` the document is printed to stdout. The command exits with 2 when no source is
given or a ``--run`` path does not exist, and with 1 (writing nothing) when no successful
record was found.
