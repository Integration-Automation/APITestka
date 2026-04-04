========================
Scripting with Executor
========================

The Executor enables JSON keyword-driven testing, where test actions are defined
as JSON arrays and executed programmatically.

JSON Keyword-Driven Testing
----------------------------

Create a JSON file (e.g., ``test_actions.json``):

.. code-block:: json

   {
       "api_testka": [
           ["AT_test_api_method", {
               "http_method": "get",
               "test_url": "http://httpbin.org/get",
               "result_check_dict": {"status_code": 200}
           }],
           ["AT_test_api_method", {
               "http_method": "post",
               "test_url": "http://httpbin.org/post",
               "params": {"task": "new task"},
               "result_check_dict": {"status_code": 200}
           }]
       ]
   }

Executing JSON Files via Python
-------------------------------

.. code-block:: python

   from je_api_testka import execute_action, read_action_json

   execute_action(read_action_json("test_actions.json"))

Executing a Directory of JSON Files
------------------------------------

.. code-block:: python

   from je_api_testka import execute_files, get_dir_files_as_list

   execute_files(get_dir_files_as_list("path/to/json_dir"))

Adding Custom Commands
----------------------

.. code-block:: python

   from je_api_testka import add_command_to_executor, execute_action

   def my_custom_function(url):
       print(f"Custom test on: {url}")

   add_command_to_executor({"my_test": my_custom_function})

   execute_action([
       ["my_test", ["http://example.com"]]
   ])

Built-in Executor Commands
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Command
     - Description
   * - ``AT_test_api_method``
     - Test API with requests backend
   * - ``AT_test_api_method_httpx``
     - Test API with httpx sync backend
   * - ``AT_delegate_async_httpx``
     - Test API with httpx async backend (run synchronously)
   * - ``AT_generate_html``
     - Generate HTML report data
   * - ``AT_generate_html_report``
     - Generate HTML report file
   * - ``AT_generate_json``
     - Generate JSON report data
   * - ``AT_generate_json_report``
     - Generate JSON report file
   * - ``AT_generate_xml``
     - Generate XML report data
   * - ``AT_generate_xml_report``
     - Generate XML report file
   * - ``AT_execute_action``
     - Execute nested action list
   * - ``AT_execute_files``
     - Execute actions from multiple files
   * - ``AT_add_package_to_executor``
     - Dynamically load a package into executor
   * - ``AT_add_package_to_callback_executor``
     - Dynamically load a package into callback executor
   * - ``AT_flask_mock_server_add_router``
     - Add route to mock server
   * - ``AT_start_flask_mock_server``
     - Start mock server
