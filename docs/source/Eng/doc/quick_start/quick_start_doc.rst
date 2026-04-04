===========
Quick Start
===========

Using the requests Backend
--------------------------

.. code-block:: python

   from je_api_testka import test_api_method_requests

   # GET request
   result = test_api_method_requests("get", "http://httpbin.org/get")
   print(result["response_data"]["status_code"])  # 200

   # POST request with parameters
   result = test_api_method_requests(
       "post",
       "http://httpbin.org/post",
       params={"task": "new task"}
   )
   print(result["response_data"]["status_code"])  # 200

Using the httpx Backend (Sync)
------------------------------

.. code-block:: python

   from je_api_testka import test_api_method_httpx

   result = test_api_method_httpx("get", "http://httpbin.org/get")
   print(result["response_data"]["status_code"])  # 200

Using the httpx Backend (Async)
-------------------------------

.. code-block:: python

   import asyncio
   from je_api_testka import test_api_method_httpx_async

   async def main():
       result = await test_api_method_httpx_async("get", "http://httpbin.org/get")
       print(result["response_data"]["status_code"])  # 200

   asyncio.run(main())

HTTP/2 Support
--------------

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

SOAP/XML Request
----------------

.. code-block:: python

   from je_api_testka import test_api_method_requests

   result = test_api_method_requests(
       "post",
       "http://example.com/soap-endpoint",
       soap=True,
       data='<soap:Envelope>...</soap:Envelope>'
   )

When ``soap=True``, the ``Content-Type`` header is automatically set to ``application/soap+xml``.

Session-Based Requests
----------------------

The ``requests`` backend supports session-based methods for persistent connections (cookies, auth, etc.):

.. code-block:: python

   from je_api_testka import test_api_method_requests

   # Use session_get, session_post, session_put, session_patch,
   # session_delete, session_head, session_options
   result = test_api_method_requests("session_get", "http://httpbin.org/get")
