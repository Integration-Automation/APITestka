======
Runner
======

三個正交的工具,專門處理大型 action list。它們都吃 ``execute_action`` 同樣
的 action 格式,並會在呼叫底層 ``AT_`` 函式前自動拿掉 runner 專用的
metadata(``id``、``depends_on``、``tags``)。

平行 Runner
-----------

.. code-block:: python

   from je_api_testka.runner import run_actions_parallel

   actions = [["AT_test_api_method_requests", {"http_method": "get",
                                                "test_url": f"http://x.invalid/{i}"}]
              for i in range(20)]
   results = run_actions_parallel(actions, max_workers=8)

Tag 過濾
--------

每個 action 可以在 kwargs 內帶 ``tags`` list。``filter_actions_by_tag`` 只保
留 tag 跟需求集合有交集的 action。

.. code-block:: python

   from je_api_testka.runner import filter_actions_by_tag

   smoke_only = filter_actions_by_tag(actions, {"smoke"})
   smoke_plus_untagged = filter_actions_by_tag(actions, {"smoke"}, include_untagged=True)

Dependency-aware 排序
---------------------

``order_actions`` 用 ``id`` / ``depends_on`` 做拓樸排序,有循環就 raise。

.. code-block:: python

   from je_api_testka.runner import order_actions

   ordered = order_actions([
       ["AT_login",  {"id": "login"}],
       ["AT_query",  {"id": "query", "depends_on": ["login"]}],
   ])
