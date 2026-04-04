==========
快速開始
==========

使用 requests 後端
-------------------

.. code-block:: python

   from je_api_testka import test_api_method_requests

   # GET 請求
   result = test_api_method_requests("get", "http://httpbin.org/get")
   print(result["response_data"]["status_code"])  # 200

   # POST 請求，帶參數
   result = test_api_method_requests(
       "post",
       "http://httpbin.org/post",
       params={"task": "new task"}
   )
   print(result["response_data"]["status_code"])  # 200

使用 httpx 後端（同步）
------------------------

.. code-block:: python

   from je_api_testka import test_api_method_httpx

   result = test_api_method_httpx("get", "http://httpbin.org/get")
   print(result["response_data"]["status_code"])  # 200

使用 httpx 後端（非同步）
--------------------------

.. code-block:: python

   import asyncio
   from je_api_testka import test_api_method_httpx_async

   async def main():
       result = await test_api_method_httpx_async("get", "http://httpbin.org/get")
       print(result["response_data"]["status_code"])  # 200

   asyncio.run(main())

HTTP/2 支援
-----------

.. code-block:: python

   import asyncio
   from je_api_testka import test_api_method_httpx_async

   async def main():
       result = await test_api_method_httpx_async(
           "get",
           "https://httpbin.org/get",
           http2=True
       )
       print(result["response_data"]["status_code"])

   asyncio.run(main())

SOAP/XML 請求
--------------

.. code-block:: python

   from je_api_testka import test_api_method_requests

   result = test_api_method_requests(
       "post",
       "http://example.com/soap-endpoint",
       soap=True,
       data='<soap:Envelope>...</soap:Envelope>'
   )

當 ``soap=True`` 時，``Content-Type`` 標頭會自動設定為 ``application/soap+xml``。

Session 持久化請求
-------------------

``requests`` 後端支援 Session 方法，用於持久化連線（cookies、驗證等）：

.. code-block:: python

   from je_api_testka import test_api_method_requests

   # 可用方法：session_get, session_post, session_put, session_patch,
   # session_delete, session_head, session_options
   result = test_api_method_requests("session_get", "http://httpbin.org/get")
