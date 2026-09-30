==========
模擬伺服器
==========

APITestka 內建基於 Flask 的模擬伺服器，用於本地測試。
可以簡單的添加路由與 HTTP 方法。

基本使用
--------

.. code-block:: python

   from je_api_testka import flask_mock_server_instance, request

   # 新增自訂路由
   def my_endpoint():
       return {"message": "hello", "params": dict(request.args)}

   flask_mock_server_instance.add_router(
       {"/api/test": my_endpoint},
       methods=["GET", "POST"]
   )

   # 啟動模擬伺服器（預設：localhost:8090）
   flask_mock_server_instance.start_mock_server()

依 HTTP 方法判斷
-----------------

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

自訂 Host 與 Port
------------------

.. code-block:: python

   from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

   server = FlaskMockServer("0.0.0.0", 5000)
   server.add_router({"/health": lambda: "OK"}, methods=["GET"])
   server.start_mock_server()

WebSocket 端點
--------------

``WebSocketMockServer`` 需要 ``websocket`` extra。每條路由可以在連線時送出問候、用 ``replies``
回覆已知訊息，其他訊息交給 ``fallback``：回覆中的 ``{{message}}`` 會換成收到的訊息，所以預設
fallback 會回聲，``None`` 則不回應。``handler`` 函式可以取代兩者。伺服器在背景執行緒執行，
port 0 會挑一個空的埠。``received(path)`` 回傳該路由收到的文字 frame，未知的路徑會在握手前以
HTTP 404 拒絕。

.. code-block:: python

   from je_api_testka.utils.mock_server.websocket_mock import WebSocketMockServer, WebSocketRoute

   with WebSocketMockServer(port=0) as ws:
       ws.add_route("/chat", WebSocketRoute(greeting="hi", replies={"ping": "pong"}))
       url = f"{ws.url}/chat"
       ...
       ws.received("/chat")

gRPC 端點
---------

``GrpcStubServer`` 需要 ``grpc`` extra，不用編譯 stub，直接以完整路徑（``/package.Service/Method``）
提供方法：固定的 unary 回應、``bytes -> bytes`` 的處理函式（``register``）、server stream，
或回傳 gRPC 狀態碼的錯誤。payload 是原始 bytes：``bytes`` 原樣送出（序列化好的 protobuf 可給
產生出來的 client 用），``str`` 以 UTF-8 送出，其他 JSON 值以精簡 JSON 送出。

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

從 JSON action 使用
-------------------

同時最多各跑一個 WebSocket mock 與 gRPC mock：``AT_mock_start_websocket_server``（``routes``、
``host``、``port``；回傳 base URL）、``AT_mock_start_grpc_server``（``methods``、``host``、
``port``；回傳 ``host:port``）、``AT_mock_websocket_received`` / ``AT_mock_grpc_received``，
以及對應的 ``AT_mock_stop_*_server``。路由與方法使用下面設定檔的格式。

.. code-block:: json

   [
     ["AT_mock_start_websocket_server", {"port": 8765, "routes": {"/chat": {"replies": {"ping": "pong"}}}}],
     ["AT_test_api_method_websocket", {"url": "ws://127.0.0.1:8765/chat", "messages": ["ping"]}],
     ["AT_mock_websocket_received", {"path": "/chat"}],
     ["AT_mock_stop_websocket_server"]
   ]

設定檔
------

``apitestka mock --config mock.json`` 讀一個 JSON 檔，其中 ``http``、``websocket``、``grpc``
三段都可省略；先啟動 WebSocket 與 gRPC mock，再持續提供 HTTP 直到停止。相對路徑的 ``openapi``
以設定檔所在目錄為準。一個 gRPC 方法必須剛好給 ``response``、``response_base64``（原始 bytes，
例如序列化好的 protobuf）、``stream``、``error`` 其中之一。

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
