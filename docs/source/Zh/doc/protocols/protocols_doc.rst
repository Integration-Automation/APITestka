============================
其他協定後端
============================

除了內建的 ``requests`` 與 ``httpx`` 兩個 HTTP 後端之外,APITestka 還提供
三個輕量 wrapper,涵蓋常見的現代協定。

WebSocket(可選)
-----------------

裝 optional 套件:

.. code-block:: bash

   pip install 'je_api_testka[websocket]'

Send-then-receive helper,同步 / 非同步皆可:

.. code-block:: python

   from je_api_testka import (
       test_api_method_websocket,
       test_api_method_websocket_async,
   )

   test_api_method_websocket(
       url="ws://echo.invalid",
       messages=["ping"],
       expected_replies=1,
   )

Server-Sent Events
------------------

``iter_sse_events`` 是 SSE stream 的 generator;``test_api_method_sse``
擷取最多 ``max_events`` 筆並寫進全域紀錄。

.. code-block:: python

   from je_api_testka import iter_sse_events, test_api_method_sse

   for event in iter_sse_events("http://api/stream", max_events=5):
       print(event)

   record = test_api_method_sse("http://api/stream", max_events=5)

GraphQL
-------

薄薄的 wrapper,組好 JSON body 然後丟給 httpx wrapper。

.. code-block:: python

   from je_api_testka import test_api_method_graphql, test_api_method_graphql_async

   test_api_method_graphql(
       "https://api/graphql",
       query="query Get($id: ID!) { user(id: $id) { id name } }",
       variables={"id": "42"},
   )
