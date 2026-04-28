==================
Connection Layer
==================

ConnectionOptions
-----------------

Centralised mTLS, proxies, and SSL knobs that can be merged into either the
``requests`` or ``httpx`` kwargs without each wrapper having to know about
every option.

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

A context manager that patches ``socket.getaddrinfo`` so specific hostnames
resolve to a chosen IP for the duration of the block. Useful for hitting
staging endpoints with prod IPs without editing ``/etc/hosts``.

.. code-block:: python

   from je_api_testka.connection import dns_override

   with dns_override({"api.example.invalid": "127.0.0.1"}):
       test_api_method_requests("get", "https://api.example.invalid/health")

VCR-style cassette
------------------

Record HTTP request/response pairs to a JSON file, then replay them on
later runs to make tests offline-deterministic.

.. code-block:: python

   from je_api_testka.connection import Cassette, CassetteRecord, replay_or_record

   cassette = Cassette("tape.json")

   def perform_request():
       return live_response

   def extract(live):
       return CassetteRecord(
           method="GET", url="http://x.invalid", request_body="",
           response_status=live.status_code, response_body=live.text,
       )

   replay_or_record(cassette, "GET", "http://x.invalid", "", perform_request, extract)

Executor commands
-----------------

* ``AT_cassette_lookup``
* ``AT_cassette_record``
