=================
Callback Executor
=================

Execute a callback function after an API test completes:

.. code-block:: python

   from je_api_testka import callback_executor

   def my_callback(message):
       print(f"Callback: {message}")

   callback_executor.callback_function(
       trigger_function_name="AT_test_api_method",
       callback_function=my_callback,
       callback_function_param={"message": "Test done!"},
       callback_param_method="kwargs",
       http_method="get",
       test_url="http://httpbin.org/get"
   )

Parameters
----------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Parameter
     - Description
   * - ``trigger_function_name``
     - Function to trigger (must be in the executor's ``event_dict``)
   * - ``callback_function``
     - Function to call after trigger completes
   * - ``callback_function_param``
     - Parameters for the callback function (dict)
   * - ``callback_param_method``
     - Parameter passing method: ``"kwargs"`` or ``"args"``
   * - ``**kwargs``
     - Parameters passed to the trigger function
