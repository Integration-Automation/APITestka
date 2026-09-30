=================
Test-as-Spec Loop
=================

The loop keeps a committed OpenAPI document and the tests in step. It takes the success records of a
test run (the current record plus saved JSON reports, or the actions ``apitestka spec check --run`` executes)
and answers four questions.

Drift
   Every recorded request is checked against the document like a contract interaction (see Contract
   Testing): the operation exists, the query parameters are declared and required ones sent, the request
   body fits its schema, the status is declared and the response body fits its schema. A request to an
   operation the document does not declare is listed as *undocumented*, under a generalized path such as
   ``GET /orders/{id}``.

Coverage
   The documented operations no test exercised. ``min_coverage`` (0 to 1) fails the loop below that share.

Missing tests
   Actions for the untested operations, from ``generate_tests_from_openapi`` on a copy of the document
   that keeps only those operations. Without an AI backend the actions are deterministic: path parameters
   and required query parameters come from the document's examples (or the schema types), a JSON request
   body from its example or schema, and the expected status is the lowest declared 2xx.

Inferred document
   The document the tests describe, with request paths grouped under the committed templates
   (``/items/7`` becomes ``/items/{id}``), path parameters added, and ``info`` and ``servers`` copied from
   the committed document. Review it, or diff it with ``openapi_changelog``, before replacing the committed one.

The loop fails on an undocumented operation, a drift problem or low coverage; the CLI then exits with 1
and ``AT_check_spec_against_tests`` raises ``APIAssertException`` carrying the report.

.. code-block:: bash

   apitestka spec check openapi.json --run tests/ --min-coverage 0.8 \
       --missing-actions tests/generated.json --inferred-spec build/openapi.inferred.json

.. code-block:: python

   from je_api_testka.spec.spec_loop import (
       check_records_against_spec, infer_spec_from_tests, missing_test_actions,
   )

   report = check_records_against_spec(records, committed_spec)
   report.coverage, report.covered, report.uncovered, report.undocumented, report.problems
   report.failures(min_coverage=0.8)
   actions = missing_test_actions(committed_spec, report)
   inferred = infer_spec_from_tests(records, committed_spec)

.. code-block:: json

   ["AT_check_spec_against_tests", {"spec_path": "openapi.json", "min_coverage": 0.8,
                                    "missing_actions_path": "tests/generated.json"}]
