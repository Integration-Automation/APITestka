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
   # ["AT_test_api_method", {"http_method": "post", "test_url": "https://api/x",
   #                         "headers": {...}, "json": {"a": 1}}]

本頁每個匯入工具都回傳 ``[command, kwargs]`` 形式的 action，``execute_action`` 可以直接執行。
JSON 內容（物件或陣列）以 ``json`` 送出，其他內容以 ``data`` 送出。

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

用 LoadDensity 做負載測試
------------------------------

同一批請求可以在 LoadDensity（``je_load_density``，Locust）上跑負載測試。請求 action
（``AT_test_api_method``、``AT_test_api_method_httpx``）或錄到的流量會變成 LoadDensity 的 HTTP task：
URL、method、``params``、``headers``、``cookies``、``json``、``data``、``timeout``、``allow_redirects``
與 ``verify`` 原樣帶過去，``result_check_dict["status_code"]`` 變成 ``status_code`` 斷言。其他 action
與相對網址會被略過，列在 ``LoadPlan.skipped``。

.. code-block:: python

   from je_api_testka.integrations.load_density import LoadProfile, actions_to_load_plan, build_load_test
   from je_api_testka.integrations.load_density_runner import LoadThresholds, run_load_test

   plan = actions_to_load_plan(actions)
   load_test = build_load_test(plan.tasks, LoadProfile(user_count=20, spawn_rate=5, test_time=30))
   result = run_load_test(load_test, LoadThresholds(max_failure_rate=0.01, max_p95_ms=500))
   result.ok, result.problems, result.summary

``run_load_test`` 寫出 action 檔，並在獨立行程啟動 ``python -m je_load_density --execute_file``，
所以 LoadDensity 的 gevent patch 不會影響 APITestka。該直譯器（``python=``，預設是目前這個）必須裝有
``je_load_density``。LoadDensity 即使 action 失敗也以 0 結束，所以結果依它寫出的摘要判斷：沒有摘要、
請求少於 ``min_requests``、失敗率超過 ``max_failure_rate`` 或 p95 超過 ``max_p95_ms`` 都算失敗。

.. code-block:: bash

   apitestka load convert --actions smoke.json -o load.json --users 20 --time 30
   apitestka load run --actions smoke.json --time 30 --max-failure-rate 0.01 --max-p95-ms 500
   apitestka load run --report run_success.json --python /opt/ld/bin/python --json

.. code-block:: json

   ["AT_run_load_test", {"action_file": "smoke.json", "profile": {"user_count": 20, "test_time": 30},
                         "thresholds": {"max_failure_rate": 0.01, "max_p95_ms": 500}}]

Executor 命令
-------------

* ``AT_notify_via_webhook``
* ``AT_post_pr_comment``
* ``AT_curl_to_action``
* ``AT_convert_har``
* ``AT_write_load_test``
* ``AT_run_load_test``
