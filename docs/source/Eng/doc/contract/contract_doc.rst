================
Contract Testing
================

Pact-style, bidirectional consumer contracts live in ``je_api_testka.contract``.

Consumer contracts
------------------

The consumer's test run becomes a contract in the Pact specification v2 file format, so the file
can go to a Pact Broker or Pactflow as it is. Records with the same method, path, query and status
become one interaction. Response bodies get a ``type`` matching rule on ``$.body`` by default, so
the provider must return the same structure and value types, not the same values; pass
``body_rule="equality"`` for exact values. ``base_path`` drops a prefix such as ``/api/v1`` from
request paths.

.. code-block:: python

   from je_api_testka.contract import add_interaction, new_pact, write_contract, write_pact

   write_contract("pacts/web-shop.json", consumer="web", provider="shop",
                  report_paths=["run_success.json"], base_path="/api/v1")

   pact = new_pact("web", "shop")        # or write interactions by hand
   add_interaction(pact, "get item 1", {"method": "GET", "path": "/items/1"},
                   {"status": 200, "body": {"id": 1, "name": "a"}},
                   provider_state="item 1 exists",
                   matching_rules={"$.body": {"match": "type"}})
   write_pact(pact, "pacts/web-shop.json")

Matching rules
--------------

Without a rule, values must be equal. A rule applies to its path and everything below it, and the
most specific rule wins; ``[*]`` and ``.*`` match any index or key.

* ``{"match": "type"}``: same JSON type. Every element of an actual array must match the first
  expected element; ``"min"`` sets the minimum length.
* ``{"match": "regex", "regex": "..."}``: the value's text must fully match.

Objects may carry keys the contract does not mention. Headers compare by name case-insensitively,
and ``Content-Type`` compares the media type only.

Provider verification
---------------------

``verify_pact`` replays each interaction against a running provider. Provider states are set up
first, through a Python callable or a setup URL that receives ``{"consumer": ..., "state": ...}``
as a JSON POST.

.. code-block:: python

   from je_api_testka.contract import ProviderTarget, read_pact, verify_pact

   target = ProviderTarget("http://localhost:8000", state_handler=seed_database, timeout=10)
   report = verify_pact(read_pact("pacts/web-shop.json"), target)
   print(report.render_text())           # report.ok, report.to_dict()

Bidirectional check
-------------------

``check_pact_against_openapi`` compares the contract with the provider's OpenAPI document without
running the provider. For every interaction it checks that the operation exists (path templates
such as ``/items/{id}`` match, and the path of the first server URL is ignored), that query
parameters are declared and required ones sent, that the request body fits its schema, that the
status is declared (exactly, as ``2XX`` or as ``default``) and that the response body fits its
schema. Schemas may use local ``$ref``, ``allOf`` / ``anyOf`` / ``oneOf``, ``nullable``, ``enum``,
``required`` and ``additionalProperties: false``. The provider keeps its document honest from its
own test run, for example with ``apitestka openapi``.

.. code-block:: python

   from je_api_testka.contract import check_contract_against_openapi

   check_contract_against_openapi("pacts/web-shop.json", "openapi.json")   # raises on a problem

Command line and JSON actions
-----------------------------

.. code-block:: bash

   apitestka contract record --report run_success.json --consumer web --provider shop -o pacts/web-shop.json
   apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000 [--provider-states-url URL]
   apitestka contract compare pacts/web-shop.json openapi.json

``verify`` and ``compare`` print a report (``--json`` for JSON) and exit with 1 when the contract does
not hold, and with 2 when a file cannot be read. The executor commands are ``AT_write_contract``,
``AT_verify_contract`` and ``AT_check_contract_against_openapi``; the last two raise
``APIContractException`` carrying the report, so the action fails.
