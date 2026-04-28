==========
資料層
==========

資料層提供串接 request、用外部資料驅動測試,以及切換環境而不必重寫
action JSON 所需的全部工具。

VariableStore
-------------

Thread-safe 全域單例 ``variable_store``。

.. code-block:: python

   from je_api_testka import variable_store

   variable_store.set("token", "abc")
   variable_store.get("token")        # 'abc'
   variable_store.snapshot()           # {'token': 'abc'}
   variable_store.clear()

模板渲染
--------

``render_template`` 會遞迴走 dict / list / str,把 ``{{name}}`` placeholder
替換成 store 內的值。

.. code-block:: python

   from je_api_testka import render_template, variable_store

   variable_store.set("base", "http://api.invalid")
   render_template({"url": "{{base}}/v1"})
   # -> {'url': 'http://api.invalid/v1'}

加 ``strict=True`` 可在 placeholder 找不到對應值時拋例外。

串接 request
-------------

``extract_and_store`` 用 dotted path 從 response 取值並存到 store。

.. code-block:: python

   from je_api_testka import extract_and_store, variable_store

   response_payload = {"data": {"user": {"id": 7}}}
   extract_and_store(response_payload, "data.user.id", "user_id")
   variable_store.get("user_id")  # 7

資料驅動測試
------------

.. code-block:: python

   from je_api_testka import iter_csv_rows, iter_json_rows

   for row in iter_csv_rows("data/users.csv"):
       ...
   for row in iter_json_rows("data/users.json"):
       ...

假資料 helper
-------------

``fake_uuid``、``fake_email``、``fake_word`` 全 stdlib,夠應付邊界情境。
要更豐富的假資料,自行裝 ``Faker``。

環境設定檔
----------

``load_env_profile`` 讀 JSON 檔並把每個 key/value 推進 store,讓同一份
action 可以靠切 profile 對應 dev / staging / prod。

.. code-block:: python

   from je_api_testka import load_env_profile

   load_env_profile("envs/dev.json")

Executor 命令
-------------

* ``AT_set_variable``
* ``AT_get_variable``
* ``AT_clear_variables``
* ``AT_extract_and_store``
* ``AT_render_template``
* ``AT_fake_uuid``
* ``AT_fake_email``
* ``AT_fake_word``
* ``AT_load_env_profile``
