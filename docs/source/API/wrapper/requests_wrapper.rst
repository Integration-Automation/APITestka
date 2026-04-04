================
Requests Wrapper
================

get_http_method
---------------

.. code-block:: python

   def get_http_method(http_method: str):

Get the corresponding HTTP method function.

:param http_method: HTTP method name (e.g., ``"get"``, ``"post"``, ``"session_get"``)
:return: one of the method functions from ``http_method_dict``
:raises: exception if method not found

Supported methods: ``get``, ``post``, ``put``, ``patch``, ``delete``, ``head``, ``options``,
``session_get``, ``session_post``, ``session_put``, ``session_patch``,
``session_delete``, ``session_head``, ``session_options``

api_tester_method
-----------------

.. code-block:: python

   def api_tester_method(
       http_method: str,
       test_url: str,
       verify: bool = False,
       timeout: int = 5,
       allow_redirects: bool = False,
       **kwargs
   ) -> requests.Response:

Execute an HTTP request.

:param http_method: HTTP method to use
:param test_url: target URL
:param verify: SSL verification
:param timeout: timeout in seconds
:param allow_redirects: allow redirects
:param kwargs: additional request parameters
:return: requests Response object
