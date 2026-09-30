=================
Report Generation
=================

Reports are generated from the global ``test_record_instance``,
which automatically records all test results.

Supported formats: **HTML**, **JSON**, **XML**.

HTML Report
-----------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_html_report

   test_api_method_requests("get", "http://httpbin.org/get")
   test_api_method_requests("post", "http://httpbin.org/post")

   # Generates "my_report.html" with success/failure tables
   generate_html_report("my_report")

JSON Report
-----------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_json_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # Generates "my_report_success.json" and "my_report_failure.json"
   generate_json_report("my_report")

XML Report
----------

.. code-block:: python

   from je_api_testka import test_api_method_requests, generate_xml_report

   test_api_method_requests("get", "http://httpbin.org/get")

   # Generates "my_report_success.xml" and "my_report_failure.xml"
   generate_xml_report("my_report")

Using with Executor
-------------------

Reports can also be generated within keyword-driven testing:

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

Response-time trends and anomalies
----------------------------------

``record_endpoint_latencies`` stores each run's per-endpoint latency (sample count, mean, p50, p95 and max
in milliseconds) in the trend database, the SQLite file ``record_current_run`` also uses. An endpoint is
the method plus the path template: the OpenAPI template the path matches when ``templates`` are given,
otherwise the path with identifier-like segments generalized (``/items/42`` becomes ``/items/{id}``).
Records come from the current test record plus saved JSON reports; records without a timing are ignored.

``detect_latency_anomalies`` judges every endpoint of the latest run against the median and the median
absolute deviation (MAD) of up to ``window`` previous runs (default 20; ``min_history``, default 5, are
needed before judging). The latest value is an anomaly when it is at least ``min_increase`` (20 %) and
``min_delta_ms`` (5 ms) above the median and its robust z-score ``0.6745 * (value - median) / MAD`` is
above ``threshold`` (3.5). A history with no spread needs only the increase. Only slowdowns are flagged.
``generate_trend_report`` writes an HTML table with the verdicts and a sparkline per endpoint.

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

JSON actions: ``AT_record_endpoint_latencies``, ``AT_detect_latency_anomalies``,
``AT_assert_no_latency_anomalies`` (fails the action on an anomaly) and ``AT_generate_trend_report``;
``policy`` takes the ``AnomalyPolicy`` fields as an object.
