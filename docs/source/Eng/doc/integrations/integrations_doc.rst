============
Integrations
============

Notifications
-------------

``notify_via_webhook`` POSTs a markdown summary to Slack, Microsoft Teams,
or Discord using each platform's incoming-webhook schema.

.. code-block:: python

   from je_api_testka.integrations import notify_via_webhook

   notify_via_webhook("https://hooks.slack.invalid/...", summary="...", platform="slack")
   notify_via_webhook("https://teams.invalid/...", summary="...", platform="teams")
   notify_via_webhook("https://discord.invalid/...", summary="...", platform="discord")

GitHub PR comment
-----------------

.. code-block:: python

   from je_api_testka.integrations import build_pr_comment_body, post_pr_comment

   post_pr_comment(
       repo="acme/widget",
       pr_number=42,
       token="<gha-token>",
       body=build_pr_comment_body(title="run #99"),
   )

cURL → action
-------------

Shell-quote-aware parser for ``-X``, ``-H``, ``-d`` / ``--data``.

.. code-block:: python

   from je_api_testka.integrations import curl_to_action

   action = curl_to_action(
       "curl -X POST https://api/x -H 'Content-Type: application/json' -d '{\"a\":1}'"
   )
   # ["AT_test_api_method", {"http_method": "post", "test_url": "https://api/x",
   #                         "headers": {...}, "json": {"a": 1}}]

Every importer on this page returns actions in the ``[command, kwargs]`` form, so
``execute_action`` runs the result as it is. A JSON body (object or array) is sent as
``json``; any other body as ``data``.

HAR import
----------

Convert a browser HAR archive (DevTools / Charles / mitmproxy) into an
action list ready for the executor.

.. code-block:: python

   from je_api_testka.integrations import convert_har

   actions = convert_har("traffic.har")

OpenAPI / Postman import
------------------------

.. code-block:: python

   from je_api_testka.cli.import_specs import convert_spec_file

   convert_spec_file("openapi.json", spec_format="openapi")
   convert_spec_file("collection.json", spec_format="postman")

The ``apitestka import`` CLI subcommand wraps this for shell users.

Load testing with LoadDensity
-----------------------------

The same requests can run as a load test on LoadDensity (``je_load_density``, Locust). Request actions
(``AT_test_api_method``, ``AT_test_api_method_httpx``) or recorded traffic become LoadDensity HTTP tasks:
URL, method, ``params``, ``headers``, ``cookies``, ``json``, ``data``, ``timeout``, ``allow_redirects``
and ``verify`` carry over, and ``result_check_dict["status_code"]`` becomes a ``status_code`` assertion.
Other actions and relative URLs are left out and listed in ``LoadPlan.skipped``.

.. code-block:: python

   from je_api_testka.integrations.load_density import LoadProfile, actions_to_load_plan, build_load_test
   from je_api_testka.integrations.load_density_runner import LoadThresholds, run_load_test

   plan = actions_to_load_plan(actions)
   load_test = build_load_test(plan.tasks, LoadProfile(user_count=20, spawn_rate=5, test_time=30))
   result = run_load_test(load_test, LoadThresholds(max_failure_rate=0.01, max_p95_ms=500))
   result.ok, result.problems, result.summary

``run_load_test`` writes the action file and starts ``python -m je_load_density --execute_file`` in its own
process, so LoadDensity's gevent patching never reaches APITestka. ``je_load_density`` must be installed for
that interpreter (``python=``, the current one by default). LoadDensity exits with 0 even when an action
fails, so the run is judged from the summary it writes: no summary, fewer than ``min_requests`` requests,
a failure rate above ``max_failure_rate`` or a p95 above ``max_p95_ms`` fails it.

.. code-block:: bash

   apitestka load convert --actions smoke.json -o load.json --users 20 --time 30
   apitestka load run --actions smoke.json --time 30 --max-failure-rate 0.01 --max-p95-ms 500
   apitestka load run --report run_success.json --python /opt/ld/bin/python --json

.. code-block:: json

   ["AT_run_load_test", {"action_file": "smoke.json", "profile": {"user_count": 20, "test_time": 30},
                         "thresholds": {"max_failure_rate": 0.01, "max_p95_ms": 500}}]

Executor commands
-----------------

* ``AT_notify_via_webhook``
* ``AT_post_pr_comment``
* ``AT_curl_to_action``
* ``AT_convert_har``
* ``AT_write_load_test``
* ``AT_run_load_test``
