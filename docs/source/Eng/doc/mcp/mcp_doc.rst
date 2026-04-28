=================
MCP Server (Claude)
=================

APITestka ships a Model Context Protocol server so Claude Code (or any other
MCP-compatible client) can drive the framework as a tool. The implementation
sits on top of the optional ``mcp`` Python SDK; tool dispatch is decoupled
from the network layer so unit tests can call the tools directly.

Installation
------------

.. code-block:: bash

   pip install 'je_api_testka[mcp]'

Running the server
------------------

Three equivalent invocations:

.. code-block:: bash

   apitestka-mcp
   apitestka mcp
   python -m je_api_testka.mcp_server

The server uses the standard MCP stdio transport and stays running until the
client disconnects.

Tools exposed
-------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Tool
     - Purpose
   * - ``apitestka_run_action``
     - Execute an executor action list
   * - ``apitestka_test_api``
     - One-shot HTTP request via the ``requests`` backend
   * - ``apitestka_curl_to_action``
     - Convert a curl command into an action dict
   * - ``apitestka_har_import``
     - Convert a HAR file into a list of actions
   * - ``apitestka_render_markdown``
     - Markdown report of the current test record
   * - ``apitestka_records_to_openapi``
     - Reconstruct an OpenAPI 3.x document
   * - ``apitestka_clear_records``
     - Wipe success / failure records
   * - ``apitestka_get_records``
     - Return current success / failure records

Claude Code configuration
-------------------------

Add the server to ``~/.claude/mcp.json``:

.. code-block:: json

   {
     "mcpServers": {
       "apitestka": {
         "command": "apitestka-mcp"
       }
     }
   }

Tool dispatch in code
---------------------

.. code-block:: python

   from je_api_testka.mcp_server import dispatch_tool

   dispatch_tool("apitestka_run_action", {"actions": [["AT_fake_uuid"]]})
   dispatch_tool("apitestka_render_markdown", {})
