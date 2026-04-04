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
     - 請求 URL
   * - ``request_body``
     - 請求內容
   * - ``start_time``
     - 請求開始時間
   * - ``end_time``
     - 請求結束時間
