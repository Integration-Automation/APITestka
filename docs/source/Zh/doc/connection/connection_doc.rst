==========
連線層
==========

ConnectionOptions
-----------------

把 mTLS、proxy、SSL 相關設定集中起來,可以套到 ``requests`` 或 ``httpx``
任一個 wrapper 的 kwargs 上,不必每個 wrapper 都認識所有 knob。

.. code-block:: python

   from je_api_testka.connection import (
       ConnectionOptions, apply_to_requests_kwargs,
   )

   options = ConnectionOptions(
       cert=("client.crt", "client.key"),     # mTLS
       proxies={"https": "http://proxy:8080"},
       verify="/etc/ssl/ca.pem",
   )
   merged = apply_to_requests_kwargs(options, {"timeout": 5})

DNS override
------------

Context manager,在 with block 內 patch ``socket.getaddrinfo``,讓特定
hostname 解析到指定 IP。適合「對 staging URL,但實際打 prod IP」的測試,
不需改 ``/etc/hosts``。

.. code-block:: python

   from je_api_testka.connection import dns_override

   with dns_override({"api.example.invalid": "127.0.0.1"}):
       test_api_method_requests("get", "https://api.example.invalid/health")

VCR-style cassette
------------------

把 request/response 對寫進 JSON 檔,後續 run 直接重播,讓測試離線可重現。

.. code-block:: python

   from je_api_testka.connection import Cassette, CassetteRecord, replay_or_record

   cassette = Cassette("tape.json")

   def perform_request():
       return live_response

   def extract(live):
       return CassetteRecord(
           method="GET", url="https://x.invalid", request_body="",
           response_status=live.status_code, response_body=live.text,
       )

   replay_or_record(cassette, "GET", "https://x.invalid", "", perform_request, extract)

Executor 命令
-------------

* ``AT_cassette_lookup``
* ``AT_cassette_record``
