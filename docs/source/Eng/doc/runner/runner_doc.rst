======
Runner
======

Three orthogonal helpers for organising large action lists. They all expect
the same action-list shape used by ``execute_action`` and strip
runner-specific metadata (``id``, ``depends_on``, ``tags``) before invoking
the underlying ``AT_`` function.

Parallel runner
---------------

.. code-block:: python

   from je_api_testka.runner import run_actions_parallel

   actions = [["AT_test_api_method_requests", {"http_method": "get",
                                                "test_url": f"http://x.invalid/{i}"}]
              for i in range(20)]
   results = run_actions_parallel(actions, max_workers=8)

Tag filtering
-------------

Each action can carry a ``tags`` list inside its kwargs dict. ``filter_actions_by_tag``
keeps only those whose tags intersect the requested set.

.. code-block:: python

   from je_api_testka.runner import filter_actions_by_tag

   smoke_only = filter_actions_by_tag(actions, {"smoke"})
   smoke_plus_untagged = filter_actions_by_tag(actions, {"smoke"}, include_untagged=True)

Dependency-aware ordering
-------------------------

``order_actions`` performs a topological sort using ``id`` and ``depends_on``
keys; cycles raise an exception.

.. code-block:: python

   from je_api_testka.runner import order_actions

   ordered = order_actions([
       ["AT_login",  {"id": "login"}],
       ["AT_query",  {"id": "query", "depends_on": ["login"]}],
   ])
