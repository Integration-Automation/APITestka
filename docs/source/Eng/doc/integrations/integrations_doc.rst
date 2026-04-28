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

Executor commands
-----------------

* ``AT_notify_via_webhook``
* ``AT_post_pr_comment``
* ``AT_curl_to_action``
* ``AT_convert_har``
