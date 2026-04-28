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
