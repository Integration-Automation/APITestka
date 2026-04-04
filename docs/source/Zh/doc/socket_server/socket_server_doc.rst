=============================
遠端自動化（Socket 伺服器）
=============================

APITestka 內建 TCP Socket 伺服器，用於遠端命令執行。

啟動伺服器
----------

.. code-block:: python

   from je_api_testka import start_apitestka_socket_server

   # 啟動 Socket 伺服器（預設：localhost:9939）
   server = start_apitestka_socket_server(host="localhost", port=9939)

用戶端可透過 TCP 傳送 JSON 格式的動作列表，伺服器會執行並回傳結果。
傳送 ``quit_server`` 可關閉伺服器。

CLI 用法
--------

.. code-block:: bash

   python -m je_api_testka.utils.socket_server.api_testka_socket_server localhost 9939
