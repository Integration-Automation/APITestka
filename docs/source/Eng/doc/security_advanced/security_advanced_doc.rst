==============
Security Suite
==============

APITestka bundles a small but useful set of helpers for authentication,
header hardening, and active probes. Heavy crypto / cloud SDKs are gated
through optional ``[security]`` extras.

Auth helpers
------------

.. code-block:: python

   from je_api_testka.security import (
       basic_auth_header, bearer_token_header, build_jwt, aws_sigv4_headers,
   )

   basic_auth_header("alice", "s3cret")
   bearer_token_header("abc.def.ghi")
   build_jwt({"sub": "alice"}, "secret")            # requires PyJWT
   aws_sigv4_headers("GET", url, "us-east-1", "s3", access_key, secret_key)

Header scan
-----------

Passive scan of a response's hardening headers (HSTS, CSP, nosniff, etc).

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

Rate-limit probe
----------------

Sends a small bounded burst (default 20) and reports the first ``429``,
including the ``Retry-After`` header. *Detector*, not a load generator.

.. code-block:: python

   from je_api_testka.security import probe_rate_limit

   result = probe_rate_limit("https://api/x", burst=20)
   result.triggered, result.triggered_at_attempt, result.retry_after

SSRF probe
----------

Submits loopback / link-local / cloud-metadata URLs into a chosen parameter
and reports any non-error response.

.. code-block:: python

   from je_api_testka.security import probe_ssrf

   probe_ssrf("https://api/fetch", parameter="url")

CVE scan
--------

Wraps ``pip-audit`` to fetch dependency-vulnerability JSON. Raises if the
binary is missing.

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

Executor commands
-----------------

* ``AT_cors_preflight``
* ``AT_probe_rate_limit``
* ``AT_probe_ssrf``
