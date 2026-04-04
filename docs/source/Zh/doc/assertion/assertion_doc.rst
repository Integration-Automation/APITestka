==========
結果斷言
==========

傳入 ``result_check_dict`` 可自動斷言回應欄位：

.. code-block:: python

   from je_api_testka import test_api_method_requests

   # 若 status_code 不是 200，將拋出 APIAssertException
   test_api_method_requests(
       "get",
       "http://httpbin.org/get",
       result_check_dict={"status_code": 200}
   )

可斷言的欄位
-------------

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
   * - ``cookies``
     - 回應 Cookies
   * - ``encoding``
     - 回應編碼
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
