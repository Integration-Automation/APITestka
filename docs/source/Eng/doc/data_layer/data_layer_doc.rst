==========
Data Layer
==========

The data layer covers everything needed to chain requests, drive tests with
external data, and switch environments without rewriting your action JSON.

VariableStore
-------------

A thread-safe key/value singleton (``variable_store``).

.. code-block:: python

   from je_api_testka import variable_store

   variable_store.set("token", "abc")
   variable_store.get("token")        # 'abc'
   variable_store.snapshot()           # {'token': 'abc'}
   variable_store.clear()

Templating
----------

``render_template`` walks dicts, lists, and strings recursively, replacing
``{{name}}`` placeholders with values from the store.

.. code-block:: python

   from je_api_testka import render_template, variable_store

   variable_store.set("base", "https://api.invalid")
   render_template({"url": "{{base}}/v1"})
   # -> {'url': 'https://api.invalid/v1'}

Pass ``strict=True`` to raise when a placeholder has no matching variable.

Chaining requests
-----------------

``extract_and_store`` pulls a value from a response payload via a dotted path
and persists it for the next request.

.. code-block:: python

   from je_api_testka import extract_and_store, variable_store

   response_payload = {"data": {"user": {"id": 7}}}
   extract_and_store(response_payload, "data.user.id", "user_id")
   variable_store.get("user_id")  # 7

Data-driven tests
-----------------

.. code-block:: python

   from je_api_testka import iter_csv_rows, iter_json_rows

   for row in iter_csv_rows("data/users.csv"):
       ...
   for row in iter_json_rows("data/users.json"):
       ...

Fake data helpers
-----------------

``fake_uuid``, ``fake_email``, and ``fake_word`` are stdlib-only helpers good
enough for boundary cases. For richer data sets, install ``Faker`` separately.

Environment profiles
--------------------

``load_env_profile`` reads a JSON file and pushes every key/value pair into
the variable store, so the same actions can target dev / staging / prod by
swapping profiles.

.. code-block:: python

   from je_api_testka import load_env_profile

   load_env_profile("envs/dev.json")

Executor commands
-----------------

* ``AT_set_variable``
* ``AT_get_variable``
* ``AT_clear_variables``
* ``AT_extract_and_store``
* ``AT_render_template``
* ``AT_fake_uuid``
* ``AT_fake_email``
* ``AT_fake_word``
* ``AT_load_env_profile``
