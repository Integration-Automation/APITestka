Mock Server
----

* Mock Server 是用來假造一個伺服器來測試運行 APITestka 腳本的環境。
* Mock Server 可以簡單的添加路由與方法。

.. code-block:: python

    from je_api_testka import flask_mock_server_instance, request

    # 觸發的方法 可以由 request.method 判斷是哪種請求
    def test_function():
        if request.method == "GET":
            return "GET"
        if request.method == "POST":
            return "POST"

    # 設置 router rule(path) 與他要觸發的 function 及接受的 HTTP methods.
    flask_mock_server_instance.add_router({"/test": test_function}, methods=["GET", "POST"])
    # 開始運行 Mock Server
    flask_mock_server_instance.start_mock_server()