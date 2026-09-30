================
可插拔 AI 後端
================

``je_api_testka.ai`` 裡有三個工具會詢問語言模型：

* ``generate_tests_from_openapi(spec)``：為每個 operation 產生 executor action。只有回覆是非空的
  ``["AT_...", {...}]`` JSON list 時才採用。
* ``generate_fake_payload(schema)``：產生符合 JSON Schema 的 JSON 值。
* ``classify_failures(error_records)``：先用規則替失敗貼標籤（``network``、``auth``、``validation``、
  ``server``、``other``），留在 ``other`` 的再一次送給模型。

預設的 ``NoOpAIBackend`` 不會碰網路，各工具會改用確定性的 fallback；回覆是空的或無法使用時也一樣。
回覆外面包了一層 Markdown code fence 也可以接受。

Anthropic 參考實作
------------------

``AnthropicAIBackend`` 需要 ``ai`` extra（``pip install 'je_api_testka[ai]'``），把每個請求送到
Anthropic Messages API 並回傳回覆文字。

* 憑證取自 ``anthropic`` SDK 讀的環境（``ANTHROPIC_API_KEY``、``ANTHROPIC_AUTH_TOKEN`` 或
  ``ant auth login`` 設定檔），backend 不接收也不保存金鑰。
* 預設模型是 ``claude-opus-5-5``。它的 thinking 一律開啟，深度用 ``effort``（``low`` 到 ``max``）控制；
  backend 會明確送出 ``medium``。
* 伺服器端的拒答 fallback 預設開啟（``fallbacks="default"``）：安全分類器拒答時，API 會改用針對該拒答類別
  建議的 fallback 模型重跑。傳 ``fallbacks=None`` 可關閉。
* 拒答、回覆在 ``max_tokens`` 被截斷、速率限制、伺服器錯誤或網路失敗時回傳空字串（暫時性錯誤 SDK 已經重試過），
  工具就改用 fallback。請求被拒（金鑰錯誤、未知模型、參數不合法）則丟出 ``APIAIBackendException``。

.. code-block:: python

   from je_api_testka.ai import AnthropicAIBackend, set_ai_backend

   set_ai_backend(AnthropicAIBackend())
   set_ai_backend(AnthropicAIBackend(model="claude-sonnet-5-5", effort="low", timeout=60))

選擇 backend
------------

* ``set_ai_backend(backend)`` 或 ``select_ai_backend("anthropic", model=..., effort=...)``；
* ``AT_select_ai_backend`` action：``["AT_select_ai_backend", {"name": "anthropic"}]``；
* 環境變數：沒有明確選擇時，第一次使用會讀 ``APITESTKA_AI_BACKEND``（``noop`` 或 ``anthropic``）、
  ``APITESTKA_AI_MODEL`` 與 ``APITESTKA_AI_EFFORT``，所以 CLI、MCP server 與 socket server 不用改程式就能用模型；
* ``apitestka generate-tests openapi.json -o actions.json --ai anthropic [--model M] [--effort E]``。

其他 provider 可繼承 ``AIBackend`` 並實作 ``complete(prompt, *, context)`` 接上；沒有答案時回傳空字串。
