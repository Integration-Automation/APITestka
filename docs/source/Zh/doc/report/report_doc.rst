==========
報告產生
==========

報告從全域的 ``test_record_instance`` 產生，所有測試結果會自動記錄。

支援格式：**HTML**、**JSON**、**XML**。

HTML 報告
---------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_html_report

   test_api_method_requests("get", "http://httpbin.org/get")
   test_api_method_requests("post", "http://httpbin.org/post")

   # 產生 "my_report.html"，包含成功/失敗表格
   generate_html_report("my_report")

JSON 報告
---------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_json_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # 產生 "my_report_success.json" 和 "my_report_failure.json"
   generate_json_report("my_report")

XML 報告
--------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_xml_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # 產生 "my_report_success.xml" 和 "my_report_failure.xml"
   generate_xml_report("my_report")

搭配 Executor 使用
-------------------

.. code-block:: python

   from je_api_testka import execute_action, generate_html, generate_html_report

   test_action_list = [
       ["AT_test_api_method", {
           "http_method": "get",
           "test_url": "http://httpbin.org/get",
           "headers": {
               "x-requested-with": "XMLHttpRequest",
               "Content-Type": "application/x-www-form-urlencoded",
           }
       }],
       ["AT_test_api_method", {
           "http_method": "post",
           "test_url": "http://httpbin.org/post",
           "params": {"task": "new task"},
           "result_check_dict": {"status_code": 200}
       }]
   ]

   execute_action(test_action_list)
   generate_html()
   generate_html_report()

回應時間趨勢與異常偵測
----------------------

``record_endpoint_latencies`` 把每次執行各端點的延遲（樣本數、平均、p50、p95、最大值，單位毫秒）存進趨勢
資料庫，也就是 ``record_current_run`` 用的那個 SQLite 檔。端點是 method 加上路徑樣板：有給 ``templates``
時用路徑對到的 OpenAPI 樣板，否則把看起來像識別碼的路徑段一般化（``/items/42`` 變成 ``/items/{id}``）。
紀錄來自目前的測試紀錄加上存下的 JSON 報告；沒有計時的紀錄會被忽略。

``detect_latency_anomalies`` 拿最近一次執行的每個端點，和它先前最多 ``window`` 次（預設 20）執行的中位數與
中位數絕對偏差（MAD）比較；要有 ``min_history``（預設 5）次才開始判斷。最新值比中位數高至少
``min_increase``（20 %）與 ``min_delta_ms``（5 ms），且 robust z-score ``0.6745 * (value - median) / MAD``
超過 ``threshold``（3.5）時算異常；歷史沒有離散度時只看增幅。只標出變慢。``generate_trend_report`` 寫出
附判定結果與各端點 sparkline 的 HTML 表格。

.. code-block:: python

   from je_api_testka.utils.generate_report.latency_trends import (
       AnomalyPolicy, assert_no_latency_anomalies, detect_latency_anomalies, record_endpoint_latencies,
   )
   from je_api_testka.utils.generate_report.trend_report import generate_trend_report

   record_endpoint_latencies("trend.sqlite", run_label="build-128", templates=openapi["paths"])
   for verdict in detect_latency_anomalies("trend.sqlite", AnomalyPolicy(metric="p95_ms")):
       print(verdict.endpoint, verdict.status, verdict.latest, verdict.baseline_median)
   assert_no_latency_anomalies("trend.sqlite")          # raises APIAssertException on an anomaly
   generate_trend_report("trends.html", "trend.sqlite")

.. code-block:: bash

   apitestka trend record --report run_success.json --label build-128 --openapi openapi.json
   apitestka trend check --metric p95_ms --window 20 --min-history 5 --threshold 3.5
   apitestka trend report -o trends.html

JSON action：``AT_record_endpoint_latencies``、``AT_detect_latency_anomalies``、
``AT_assert_no_latency_anomalies``（有異常時該 action 失敗）與 ``AT_generate_trend_report``；
``policy`` 以物件傳入 ``AnomalyPolicy`` 的欄位。
