==============
測試即規格迴路
==============

這個迴路讓已提交的 OpenAPI 文件與測試保持一致。它拿一次測試執行的成功紀錄（目前的紀錄加上存下的 JSON 報告，
或 ``apitestka spec check --run`` 執行的 action），回答四個問題。

偏移
   每個錄下的請求都像契約互動一樣和文件比對（見契約測試一章）：operation 存在、查詢參數有宣告且必填的有送、
   請求內容符合 schema、狀態碼有宣告、回應內容符合 schema。打到文件沒宣告的 operation 會以一般化的路徑
   （例如 ``GET /orders/{id}``）列為 *未文件化*。

覆蓋率
   沒有任何測試碰到的已文件化 operation。``min_coverage``\ （0 到 1）低於該比例時迴路失敗。

缺少的測試
   對只保留這些 operation 的文件副本呼叫 ``generate_tests_from_openapi``，替沒測到的 operation 產生 action。
   沒有 AI backend 時產生的是確定性的 action：路徑參數與必填查詢參數取自文件的範例（或 schema 型別），JSON 請求
   內容取自它的範例或 schema，預期狀態碼是宣告中最小的 2xx。

推導出的文件
   測試描述出來的文件：請求路徑歸到已提交的樣板底下（``/items/7`` 變成 ``/items/{id}``），補上路徑參數，
   ``info`` 與 ``servers`` 沿用已提交的文件。取代已提交的文件前先檢查，或用 ``openapi_changelog`` 比對。

有未文件化的 operation、偏移問題或覆蓋率不足時迴路失敗：CLI 結束碼為 1，``AT_check_spec_against_tests``
會丟出帶著報告的 ``APIAssertException``。

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
