====================
Pluggable AI Backend
====================

Three helpers in ``je_api_testka.ai`` can ask a language model:

* ``generate_tests_from_openapi(spec)``: executor actions for every operation. A reply is used only when
  it is a non-empty JSON list of ``["AT_...", {...}]`` actions.
* ``generate_fake_payload(schema)``: a JSON value that satisfies a JSON Schema.
* ``classify_failures(error_records)``: rules label each failure (``network``, ``auth``,
  ``validation``, ``server``, ``other``); the ones left as ``other`` go to the model in one request.

The default backend, ``NoOpAIBackend``, never calls a network, and every helper then uses its
deterministic fallback. It does the same when a reply is empty or unusable. A reply wrapped in one
Markdown code fence is accepted.

Anthropic reference backend
---------------------------

``AnthropicAIBackend`` needs the ``ai`` extra (``pip install 'je_api_testka[ai]'``). It sends each request
to the Anthropic Messages API and returns the reply text.

* Credentials come from the environment the ``anthropic`` SDK reads (``ANTHROPIC_API_KEY``,
  ``ANTHROPIC_AUTH_TOKEN`` or an ``ant auth login`` profile). The backend never takes or stores a key.
* The default model is ``claude-opus-5-5``. Its thinking is always on, so depth is set with ``effort``
  (``low`` to ``max``); the backend sends ``medium`` explicitly.
* Server-side refusal fallbacks are on (``fallbacks="default"``): when a safety classifier declines,
  the API re-runs the request on the fallback model recommended for that refusal category. Pass
  ``fallbacks=None`` to turn it off.
* A refusal, a reply cut off at ``max_tokens``, a rate limit, a server error or a network failure
  returns an empty reply (the SDK has already retried the transient ones), so the helper uses its
  fallback. A rejected request (bad key, unknown model, invalid parameter) raises
  ``APIAIBackendException``.

.. code-block:: python

   from je_api_testka.ai import AnthropicAIBackend, set_ai_backend

   set_ai_backend(AnthropicAIBackend())
   set_ai_backend(AnthropicAIBackend(model="claude-sonnet-5-5", effort="low", timeout=60))

Selecting a backend
-------------------

* ``set_ai_backend(backend)`` or ``select_ai_backend("anthropic", model=..., effort=...)``;
* the ``AT_select_ai_backend`` action: ``["AT_select_ai_backend", {"name": "anthropic"}]``;
* the environment: without a selection, the first use reads ``APITESTKA_AI_BACKEND`` (``noop`` or
  ``anthropic``), ``APITESTKA_AI_MODEL`` and ``APITESTKA_AI_EFFORT``, so the CLI, the MCP server and the
  socket server use a model without code changes;
* ``apitestka generate-tests openapi.json -o actions.json --ai anthropic [--model M] [--effort E]``.

Other providers plug in by subclassing ``AIBackend`` and implementing ``complete(prompt, *, context)``;
return an empty string for "no answer".
