================
Result Assertion
================

Pass a ``result_check_dict`` to automatically assert response fields:

.. code-block:: python

   from je_api_testka import test_api_method_requests

   # This will raise APIAssertException if status_code is not 200
   test_api_method_requests(
       "get",
       "http://httpbin.org/get",
       result_check_dict={"status_code": 200}
   )

Assertable Fields
-----------------

You can assert on any field in the response data:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Field
     - Description
   * - ``status_code``
     - HTTP status code
   * - ``text``
     - Response body as text
   * - ``content``
     - Response body as bytes
   * - ``headers``
     - Response headers
   * - ``cookies``
     - Response cookies
   * - ``encoding``
     - Response encoding
   * - ``elapsed``
     - Time elapsed for the request
   * - ``request_time_sec``
     - Request duration in seconds
   * - ``request_method``
     - HTTP method used
   * - ``request_url``
     - Request URL
   * - ``request_body``
     - Request body sent
   * - ``start_time``
     - Request start time
   * - ``end_time``
     - Request end time
