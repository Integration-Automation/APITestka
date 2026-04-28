==========
生態整合
==========

通知
----

``notify_via_webhook`` POST 一份 markdown 摘要到 Slack / Microsoft Teams /
Discord 的 incoming webhook,自動套用各平台的 schema。

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

支援 ``-X``、``-H``、``-d`` / ``--data`` 等常用 flag,bash quote 安全。

.. code-block:: python

   from je_api_testka.integrations import curl_to_action

   action = curl_to_action(
       "curl -X POST https://api/x -H 'Content-Type: application/json' -d '{\"a\":1}'"
   )

HAR 匯入
--------

把瀏覽器 DevTools / Charles / mitmproxy 錄的 HAR 直接轉成 action list。

.. code-block:: python

   from je_api_testka.integrations import convert_har

   actions = convert_har("traffic.har")

OpenAPI / Postman 匯入
----------------------

.. code-block:: python

   from je_api_testka.cli.import_specs import convert_spec_file

   convert_spec_file("openapi.json", spec_format="openapi")
   convert_spec_file("collection.json", spec_format="postman")

也可以直接用 ``apitestka import`` CLI 子命令。

Executor 命令
-------------

* ``AT_notify_via_webhook``
* ``AT_post_pr_comment``
* ``AT_curl_to_action``
* ``AT_convert_har``
