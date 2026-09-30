==============================
Response Diff, Contract & SLA
==============================

Three layered checks for catching regressions without writing assertions
case by case.

diff_payloads
-------------

Structural diff between two JSON-like payloads.

.. code-block:: python

   from je_api_testka import diff_payloads

   diff = diff_payloads({"a": 1, "b": 2}, {"a": 1, "b": 3})
   diff.changed   # {'b': (2, 3)}
   diff.added     # {}
   diff.removed   # {}
   diff.is_empty  # False

Pass ``ignore_paths`` to skip volatile fields:

.. code-block:: python

   diff_payloads(left, right, ignore_paths=["timestamp", "request_id"])

OpenAPI contract drift
----------------------

.. code-block:: python

   from je_api_testka import diff_openapi_specs

   drift = diff_openapi_specs(prev_spec, current_spec)
   drift.added_paths
   drift.removed_paths
   drift.added_operations
   drift.removed_operations
   drift.schema_changes  # dict keyed by 'METHOD /path'

Render the same drift as a markdown changelog:

.. code-block:: python

   from je_api_testka.spec import openapi_changelog

   print(openapi_changelog(prev_spec, current_spec))

Inferring OpenAPI from recorded traffic
---------------------------------------

``records_to_openapi`` turns test records into an OpenAPI 3.1 document. Records with the same
method and path merge into one operation: every status code seen gets a response entry, query
parameter names become ``in: query`` parameters, and JSON or text bodies become response and
request-body schemas. ``build_openapi`` adds records read back from saved JSON reports, and
``export_openapi`` writes the result as UTF-8 JSON.

.. code-block:: python

   from je_api_testka.spec import build_openapi, export_openapi, load_report_records

   records = load_report_records("run_success.json")      # from generate_json_report
   spec = build_openapi(["run_success.json"], title="Shop API")
   export_openapi("openapi.json", ["run_success.json"])

Response time SLA
-----------------

``ResponseSLA`` carries ``max_ms`` and ``p95_ms`` thresholds; ``assert_sla``
walks a list of records and raises ``APIAssertException`` on breach.

.. code-block:: python

   from je_api_testka.diff.sla_check import ResponseSLA, assert_sla

   sla = ResponseSLA(max_ms=2000, p95_ms=1500)
   assert_sla(records, sla)

Executor commands
-----------------

* ``AT_diff_payloads``
* ``AT_diff_openapi_specs``
* ``AT_assert_sla``
* ``AT_openapi_changelog``
* ``AT_records_to_openapi``
* ``AT_export_openapi``
