================
GET API Data
================

.. code-block:: python

   def get_api_response_data(
       response: Response,
       start_time: [str, float, int],
       end_time: [str, float, int]
   ) -> dict:

Create a data dict from a requests response.

:param response: requests Response object
:param start_time: test start time
:param end_time: test end time
:return: dict with keys: ``status_code``, ``text``, ``content``, ``headers``,
   ``history``, ``encoding``, ``cookies``, ``elapsed``, ``request_time_sec``,
   ``request_method``, ``request_url``, ``request_body``, ``start_time``, ``end_time``
