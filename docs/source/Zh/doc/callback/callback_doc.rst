==========
回呼執行器
==========

在 API 測試完成後執行回呼函式：

.. code-block:: python

   from je_api_testka import callback_executor

   def my_callback(message):
       print(f"回呼：{message}")

   callback_executor.callback_function(
       trigger_function_name="AT_test_api_method",
       callback_function=my_callback,
       callback_function_param={"message": "測試完成！"},
       callback_param_method="kwargs",
       http_method="get",
       test_url="http://httpbin.org/get"
   )

參數說明
--------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 參數
     - 說明
   * - ``trigger_function_name``
     - 要觸發的函式（必須在執行器的 ``event_dict`` 中）
   * - ``callback_function``
     - 觸發完成後要呼叫的函式
   * - ``callback_function_param``
     - 回呼函式的參數（dict）
   * - ``callback_param_method``
     - 參數傳遞方式：``"kwargs"`` 或 ``"args"``
   * - ``**kwargs``
     - 傳遞給觸發函式的參數
