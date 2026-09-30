========
契約測試
========

Pact 風格的雙向消費者契約放在 ``je_api_testka.contract``。

消費者契約
----------

消費端的測試執行會變成 Pact 規格 v2 檔案格式的契約，檔案可以直接送到 Pact Broker 或 Pactflow。
method、路徑、查詢字串與狀態碼都相同的紀錄會合成一個互動。回應內容預設在 ``$.body`` 帶 ``type``
比對規則，所以提供端必須回傳相同的結構與值的型別，而不是相同的值；要比對確切的值就傳
``body_rule="equality"``。``base_path`` 會從請求路徑拿掉 ``/api/v1`` 這類前綴。

.. code-block:: python

   from je_api_testka.contract import add_interaction, new_pact, write_contract, write_pact

   write_contract("pacts/web-shop.json", consumer="web", provider="shop",
                  report_paths=["run_success.json"], base_path="/api/v1")

   pact = new_pact("web", "shop")        # 也可以手寫互動
   add_interaction(pact, "get item 1", {"method": "GET", "path": "/items/1"},
                   {"status": 200, "body": {"id": 1, "name": "a"}},
                   provider_state="item 1 exists",
                   matching_rules={"$.body": {"match": "type"}})
   write_pact(pact, "pacts/web-shop.json")

比對規則
--------

沒有規則時值必須相同。規則作用在自己的路徑以及底下所有節點，最具體的規則優先；``[*]`` 與 ``.*``
可比對任何索引或鍵。

* ``{"match": "type"}``：JSON 型別相同。實際陣列的每個元素都必須符合預期的第一個元素；``"min"``
  設定最少元素數。
* ``{"match": "regex", "regex": "..."}``：值的文字必須完全符合。

物件可以多帶契約沒提到的鍵。header 名稱不分大小寫，``Content-Type`` 只比 media type。

提供端驗證
----------

``verify_pact`` 把每個互動重播到執行中的提供端。會先建立提供端狀態，方法是呼叫 Python 函式，或對
設定 URL 送出內容為 ``{"consumer": ..., "state": ...}`` 的 JSON POST。

.. code-block:: python

   from je_api_testka.contract import ProviderTarget, read_pact, verify_pact

   target = ProviderTarget("http://localhost:8000", state_handler=seed_database, timeout=10)
   report = verify_pact(read_pact("pacts/web-shop.json"), target)
   print(report.render_text())           # report.ok、report.to_dict()

雙向檢查
--------

``check_pact_against_openapi`` 不用啟動提供端，直接把契約和提供端的 OpenAPI 文件比對。每個互動都檢查：
operation 存在（``/items/{id}`` 這類路徑樣板可比對，第一個 server URL 的路徑會被忽略）、查詢參數
有宣告且必填的有送、請求內容符合 schema、狀態碼有宣告（完全相同、``2XX`` 或 ``default``）、回應內容
符合 schema。schema 可以用本地 ``$ref``、``allOf`` / ``anyOf`` / ``oneOf``、``nullable``、``enum``、
``required`` 與 ``additionalProperties: false``。提供端用自己的測試執行維持文件正確，例如用
``apitestka openapi``。

.. code-block:: python

   from je_api_testka.contract import check_contract_against_openapi

   check_contract_against_openapi("pacts/web-shop.json", "openapi.json")   # 有問題就丟例外

命令列與 JSON action
--------------------

.. code-block:: bash

   apitestka contract record --report run_success.json --consumer web --provider shop -o pacts/web-shop.json
   apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000 [--provider-states-url URL]
   apitestka contract compare pacts/web-shop.json openapi.json

``verify`` 與 ``compare`` 會印出報告（``--json`` 輸出 JSON），契約不成立時結束碼為 1，檔案讀不到時為 2。
executor 指令是 ``AT_write_contract``、``AT_verify_contract`` 與 ``AT_check_contract_against_openapi``；
後兩者會丟出帶著報告的 ``APIContractException``，讓該 action 失敗。
