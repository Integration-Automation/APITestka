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
