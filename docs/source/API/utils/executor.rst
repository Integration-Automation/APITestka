========
Executor
========

Executor Class
--------------

The ``Executor`` class provides JSON keyword-driven test execution.

.. code-block:: python

   class Executor:

       def execute_action(self, action_list: [list, dict]) -> dict:
           """
           Execute a list of actions.

           :param action_list: action list structure:
               [["method_name", {"param": value}], ...]
               or dict with "api_testka" key
           :return: dict of execution records and responses
           """

       def execute_files(self, execute_files_list: list):
           """
           Execute actions from multiple JSON files.

           :param execute_files_list: list of file paths
           :return: list of execution details
           """

Module Functions
----------------

.. code-block:: python

   def add_command_to_executor(command_dict: dict):

Add custom commands to the executor.

:param command_dict: dict of ``{"command_name": function}``
:raises: ``APIAddCommandException`` if value is not a function

.. code-block:: python

   def execute_action(action_list: list):

Execute an action list using the global executor instance.

.. code-block:: python

   def execute_files(execute_files_list: list):

Execute actions from multiple files using the global executor instance.
