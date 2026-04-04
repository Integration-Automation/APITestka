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
