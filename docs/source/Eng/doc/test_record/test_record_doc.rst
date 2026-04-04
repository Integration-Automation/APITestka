===========
Test Record
===========

All API test results are automatically stored in a global ``test_record_instance``:

.. code-block:: python

   from je_api_testka import test_api_method_requests, test_record_instance

   test_api_method_requests("get", "http://httpbin.org/get")
   test_api_method_requests("get", "http://invalid-url")

   # Access successful test records
   print(len(test_record_instance.test_record_list))

   # Access error records
   print(len(test_record_instance.error_record_list))

   # Clean all records
   test_record_instance.clean_record()

Record Fields
-------------

Each successful record contains the following fields:

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
   * - ``history``
     - Redirect history
   * - ``encoding``
     - Response encoding
   * - ``cookies``
     - Response cookies
   * - ``elapsed``
     - Time elapsed
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
