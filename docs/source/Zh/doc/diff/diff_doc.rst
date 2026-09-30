==============================
Response Diff、Contract 與 SLA
==============================

三層次的檢查,讓你不必手寫一條一條 assertion 也能抓回歸。

diff_payloads
-------------

兩個 JSON-like payload 的結構化 diff。

.. code-block:: python

   from je_api_testka import diff_payloads

   diff = diff_payloads({"a": 1, "b": 2}, {"a": 1, "b": 3})
   diff.changed   # {'b': (2, 3)}
   diff.added     # {}
   diff.removed   # {}
   diff.is_empty  # False

加 ``ignore_paths`` 跳過會變動的欄位:

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
   drift.schema_changes  # 以 'METHOD /path' 為 key

要直接出 markdown changelog:

.. code-block:: python

   from je_api_testka.spec import openapi_changelog

   print(openapi_changelog(prev_spec, current_spec))

從錄下的流量反推 OpenAPI
------------------------------

``records_to_openapi`` 把測試紀錄轉成 OpenAPI 3.1 文件。同一個 method 與路徑的紀錄會合併成一個
operation：每個出現過的狀態碼各有一筆 response，查詢參數名稱變成 ``in: query`` 參數，JSON 或文字
內容變成回應與請求內容的 schema。``build_openapi`` 再加上從存下的 JSON 報告讀回的紀錄，
``export_openapi`` 把結果寫成 UTF-8 JSON。

.. code-block:: python

   from je_api_testka.spec import build_openapi, export_openapi, load_report_records

   records = load_report_records("run_success.json")      # generate_json_report 的輸出
   spec = build_openapi(["run_success.json"], title="Shop API")
   export_openapi("openapi.json", ["run_success.json"])

回應時間 SLA
------------

``ResponseSLA`` 帶 ``max_ms`` 與 ``p95_ms`` 兩個門檻;``assert_sla`` 走過
records,超過就丟 ``APIAssertException``。

.. code-block:: python

   from je_api_testka.diff.sla_check import ResponseSLA, assert_sla

   sla = ResponseSLA(max_ms=2000, p95_ms=1500)
   assert_sla(records, sla)

Executor 命令
-------------

* ``AT_diff_payloads``
* ``AT_diff_openapi_specs``
* ``AT_assert_sla``
* ``AT_openapi_changelog``
* ``AT_records_to_openapi``
* ``AT_export_openapi``
