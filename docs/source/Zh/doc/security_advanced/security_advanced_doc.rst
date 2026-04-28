==========
安全套件
==========

APITestka 提供一組精簡但實用的 helper 處理身分驗證、Header 加固與主動探測。
重的密碼學 / 雲 SDK 都走 optional ``[security]`` extras。

Auth helper
-----------

.. code-block:: python

   from je_api_testka.security import (
       basic_auth_header, bearer_token_header, build_jwt, aws_sigv4_headers,
   )

   basic_auth_header("alice", "s3cret")
   bearer_token_header("abc.def.ghi")
   build_jwt({"sub": "alice"}, "secret")            # 需要 PyJWT
   aws_sigv4_headers("GET", url, "us-east-1", "s3", access_key, secret_key)

Header scan
-----------

被動掃描 response 是否帶齊加固 header(HSTS、CSP、nosniff…)。

.. code-block:: python

   from je_api_testka.security import scan_security_headers

   findings = scan_security_headers(response.headers)
   for finding in findings:
       print(finding.header, finding.severity, finding.message)

CORS preflight
--------------

.. code-block:: python

   from je_api_testka.security import cors_preflight

   findings = cors_preflight("https://api/x", origin="https://app", method="GET")

Rate-limit 探測
---------------

發一小串連續 request(預設 20 次),回報第一個 ``429`` 的位置與
``Retry-After``。**這是探測,不是壓測。**

.. code-block:: python

   from je_api_testka.security import probe_rate_limit

   result = probe_rate_limit("https://api/x", burst=20)
   result.triggered, result.triggered_at_attempt, result.retry_after

SSRF 探測
---------

把 loopback / link-local / 雲 metadata URL 塞進指定欄位,回報任何
非錯誤回應。

.. code-block:: python

   from je_api_testka.security import probe_ssrf

   probe_ssrf("https://api/fetch", parameter="url")

CVE 掃描
--------

包 ``pip-audit`` 取得相依套件的弱點 JSON。沒裝 binary 時會 raise。

.. code-block:: python

   from je_api_testka.security import run_pip_audit

   for dep in run_pip_audit():
       ...

Fuzz seed
---------

.. code-block:: python

   from je_api_testka.security import fuzz_string_inputs, fuzz_value_pool

   fuzz_string_inputs(limit=50)
   for mutated in fuzz_value_pool({"name": "alice", "age": 30}, fields=["name"]):
       ...

Executor 命令
-------------

* ``AT_cors_preflight``
* ``AT_probe_rate_limit``
* ``AT_probe_ssrf``
