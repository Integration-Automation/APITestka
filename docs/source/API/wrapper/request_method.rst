==============
Request Method
==============

get_response
------------

.. code-block:: python

   def get_response(
       response: requests.Response,
       start_time: [str, float, int],
       end_time: [str, float, int]
   ) -> dict:

Use requests response to create data dict.

:param response: requests response
:param start_time: test start time
:param end_time: test end time
:return: data dict including ``status_code``, ``text``, ``content``, ``headers``,
   ``history``, ``encoding``, ``cookies``, ``elapsed``, ``request_time_sec``,
   ``request_method``, ``request_url``, ``request_body``, ``start_time``, ``end_time``

test_api_method
---------------

.. code-block:: python

   def test_api_method(
       http_method: str,
       test_url: str,
       soap: bool = False,
       record_request_info: bool = True,
       clean_record: bool = False,
       result_check_dict: dict = None,
       verify: bool = False,
       timeout: int = 5,
       allow_redirects: bool = False,
       **kwargs
   ) -> (requests.Response, dict):

Set requests HTTP method, URL, headers and record response.

:param http_method: HTTP method to use
:param test_url: target URL
:param soap: enable SOAP mode (auto-set Content-Type)
:param record_request_info: whether to record request info
:param clean_record: whether to clean previous records
:param result_check_dict: dict for asserting response fields
:param verify: SSL verification
:param timeout: timeout in seconds
:param allow_redirects: allow redirects
:param kwargs: additional request parameters
