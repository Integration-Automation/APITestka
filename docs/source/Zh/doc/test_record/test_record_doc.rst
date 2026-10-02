==========
測試紀錄
==========

所有 API 測試結果會自動儲存在全域的 ``test_record_instance`` 中：

.. code-block:: python

   from je_api_testka import test_api_method_requests, test_record_instance

   test_api_method_requests("get", "http://httpbin.org/get")
   test_api_method_requests("get", "http://invalid-url")

   # 取得成功的測試紀錄
   print(len(test_record_instance.test_record_list))

   # 取得錯誤紀錄
   print(len(test_record_instance.error_record_list))

   # 清除所有紀錄
   test_record_instance.clean_record()

紀錄欄位
--------

每筆成功紀錄包含以下欄位：

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - 欄位
     - 說明
   * - ``status_code``
     - HTTP 狀態碼
   * - ``text``
     - 回應內容（文字）
   * - ``content``
     - 回應內容（位元組）
   * - ``headers``
     - 回應標頭
   * - ``history``
     - 重導向歷史
   * - ``encoding``
     - 回應編碼
   * - ``cookies``
     - 回應 Cookies
   * - ``elapsed``
     - 請求耗時
   * - ``request_time_sec``
     - 請求持續時間（秒）
   * - ``request_method``
     - 使用的 HTTP 方法
   * - ``request_url``
     - 請求 URL（每個後端都記成文字）
   * - ``request_body``
     - 請求內容
   * - ``start_time``
     - 請求開始時間
   * - ``end_time``
     - 請求結束時間

共用請求紀錄
------------------

ActionCore 支援 request context 後，HTTP 包裝器可在明確的執行作用域內同步記錄 RequestRecord v1。原生回應和舊報告格式保持相容。HTTP 與斷言失敗保留實際狀態碼，傳輸失敗的未知測量值使用 null。`record_request_info=False` 排除成功紀錄，失敗仍會記錄。預設不保存本文和標頭；`from_legacy_record(..., capture_payload=True)` 可匯入本文並遮蔽敏感標頭。各 context 獨立保存紀錄，`clean_record()` 只清除舊的全域紀錄。

.. code-block:: python

   from je_api_testka import test_api_method_requests
   from je_api_testka.utils.test_record.run_context import RunContext, use_run_context

   run = RunContext(source="apitestka", phase="functional", engine="requests")
   with use_run_context(run):
       test_api_method_requests("get", "http://localhost:8091/get")
   records_json = run.to_json()

Canonical 結束時間由開始時間加單調時鐘耗時計算，系統時間校正不會使區間倒退。Runner／設定錯誤與連線及其他傳輸錯誤分開記錄。
