===========
Mock Server
===========

APITestka includes a built-in Flask-based mock server for local testing.
It allows easy addition of routes and HTTP methods.

Basic Usage
-----------

.. code-block:: python

   from je_api_testka import flask_mock_server_instance, request

   # Add custom routes
   def my_endpoint():
       return {"message": "hello", "params": dict(request.args)}

   flask_mock_server_instance.add_router(
       {"/api/test": my_endpoint},
       methods=["GET", "POST"]
   )

   # Start the mock server (default: localhost:8090)
   flask_mock_server_instance.start_mock_server()

Route with Method Detection
---------------------------

.. code-block:: python

   from je_api_testka import flask_mock_server_instance, request

   def test_function():
       if request.method == "GET":
           return "GET"
       if request.method == "POST":
           return "POST"

   flask_mock_server_instance.add_router(
       {"/test": test_function},
       methods=["GET", "POST"]
   )
   flask_mock_server_instance.start_mock_server()

Custom Host and Port
--------------------

.. code-block:: python

   from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

   server = FlaskMockServer("0.0.0.0", 5000)
   server.add_router({"/health": lambda: "OK"}, methods=["GET"])
   server.start_mock_server()

WebSocket endpoints
-------------------

``WebSocketMockServer`` needs the ``websocket`` extra. Each route can greet a new
connection, answer known messages from ``replies`` and handle the rest with ``fallback``:
``{{message}}`` in a reply is replaced by the incoming message, so the default fallback
echoes, and ``None`` sends nothing. A ``handler`` callable can replace both. The server runs
in a background thread; port 0 picks a free port. ``received(path)`` returns the text frames
a route got, and an unknown path is refused with HTTP 404 before the handshake.

.. code-block:: python

   from je_api_testka.utils.mock_server.websocket_mock import WebSocketMockServer, WebSocketRoute

   with WebSocketMockServer(port=0) as ws:
       ws.add_route("/chat", WebSocketRoute(greeting="hi", replies={"ping": "pong"}))
       url = f"{ws.url}/chat"
       ...
       ws.received("/chat")

gRPC endpoints
--------------

``GrpcStubServer`` needs the ``grpc`` extra and serves methods by full path
(``/package.Service/Method``) without compiled stubs: a fixed unary response, a
``bytes -> bytes`` handler (``register``), a server stream, or an error with a gRPC status
code. Payloads are raw bytes: ``bytes`` pass through (serialized protobuf works with
generated clients), ``str`` is UTF-8 and other JSON values are compact JSON.

.. code-block:: python

   import grpc
   from je_api_testka.utils.mock_server.grpc_stub import GrpcStubServer

   with GrpcStubServer(port=0) as mock:
       mock.add_unary_response("/shop.Catalog/Get", {"id": 1})
       mock.add_stream_responses("/shop.Catalog/List", [{"id": 1}, {"id": 2}])
       mock.add_error("/shop.Catalog/Delete", "PERMISSION_DENIED", "read only")
       with grpc.insecure_channel(mock.address) as channel:
           channel.unary_unary("/shop.Catalog/Get")(b"{}")   # b'{"id":1}'
       mock.received("/shop.Catalog/Get")                     # [b'{}']

From JSON actions
-----------------

One WebSocket mock and one gRPC mock can run at a time:
``AT_mock_start_websocket_server`` (``routes``, ``host``, ``port``; returns the base URL),
``AT_mock_start_grpc_server`` (``methods``, ``host``, ``port``; returns ``host:port``),
``AT_mock_websocket_received`` / ``AT_mock_grpc_received`` and the matching
``AT_mock_stop_*_server`` commands. Routes and methods use the config form below.

.. code-block:: json

   [
     ["AT_mock_start_websocket_server", {"port": 8765, "routes": {"/chat": {"replies": {"ping": "pong"}}}}],
     ["AT_test_api_method_websocket", {"url": "ws://127.0.0.1:8765/chat", "messages": ["ping"]}],
     ["AT_mock_websocket_received", {"path": "/chat"}],
     ["AT_mock_stop_websocket_server"]
   ]

Config file
-----------

``apitestka mock --config mock.json`` reads one JSON file with optional ``http``,
``websocket`` and ``grpc`` sections, starts the WebSocket and gRPC mocks, then serves HTTP
until stopped. A relative ``openapi`` path is resolved against the config file. A gRPC
method takes exactly one of ``response``, ``response_base64`` (raw bytes such as a
serialized protobuf), ``stream`` or ``error``.

.. code-block:: json

   {
     "http": {"routes": [{"rule": "/health", "body": {"ok": true}}], "openapi": "spec.json"},
     "websocket": {"port": 8765, "routes": {"/chat": {"greeting": "hi", "replies": {"ping": "pong"}}}},
     "grpc": {"port": 50051, "methods": {
       "/shop.Catalog/Get": {"response": {"id": 1}},
       "/shop.Catalog/List": {"stream": [{"id": 1}, {"id": 2}]},
       "/shop.Catalog/Delete": {"error": {"code": "PERMISSION_DENIED", "details": "read only"}}
     }}
   }
