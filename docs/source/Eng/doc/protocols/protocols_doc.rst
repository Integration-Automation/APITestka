============================
Extra Protocol Backends
============================

In addition to the stock ``requests`` and ``httpx`` HTTP backends, APITestka
ships three lightweight wrappers for common modern protocols.

WebSocket (optional)
---------------------

Install the optional dependency:

.. code-block:: bash

   pip install 'je_api_testka[websocket]'

Send-then-receive helper, sync or async:

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

``iter_sse_events`` is a generator over an SSE stream. ``test_api_method_sse``
captures up to ``max_events`` events and stores the result into the global
record.

.. code-block:: python

   from je_api_testka import iter_sse_events, test_api_method_sse

   for event in iter_sse_events("http://api/stream", max_events=5):
       print(event)

   record = test_api_method_sse("http://api/stream", max_events=5)

GraphQL
-------

Thin wrapper that builds the JSON body and forwards to the httpx wrappers.

.. code-block:: python

   from je_api_testka import test_api_method_graphql, test_api_method_graphql_async

   test_api_method_graphql(
       "https://api/graphql",
       query="query Get($id: ID!) { user(id: $id) { id name } }",
       variables={"id": "42"},
   )
