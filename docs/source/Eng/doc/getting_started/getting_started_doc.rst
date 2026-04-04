===============
Getting Started
===============

Create a Project
----------------

In APITestka, you can create a project which will automatically generate sample files.
These sample files include a Python executor file and a ``keyword.json`` file.

.. code-block:: python

   from je_api_testka import create_project_dir

   # Create in current working directory
   create_project_dir()

   # Create at a specific path
   create_project_dir("project_path")

   # Create with a custom project name
   create_project_dir("project_path", "My First Project")

Or using CLI:

.. code-block:: bash

   python -m je_api_testka --create_project project_path

Run the Executor
----------------

Enter the project folder, navigate to the ``executor`` folder, and run one of the executors.
The ``keyword.json`` files in the ``keyword`` folder define the actions to be executed.

Using Pure Python
-----------------

.. note::

   Only the following HTTP methods are supported:
   ``get``, ``post``, ``put``, ``patch``, ``delete``, ``head``, ``options``

.. code-block:: python

   from je_api_testka import execute_action

   test_api_list = [
       ["AT_test_api_method", {
           "http_method": "post",
           "test_url": "http://httpbin.org/post",
           "params": {"task": "new task"},
           "result_check_dict": {"status_code": 200}
       }],
       ["AT_test_api_method", {
           "http_method": "get",
           "test_url": "http://httpbin.org/post",
           "result_check_dict": {"status_code": 405}
       }]
   ]

   execute_action(test_api_list)
