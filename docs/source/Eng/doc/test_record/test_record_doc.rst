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
     - Request URL, as text for every backend
   * - ``request_body``
     - Request body sent
   * - ``start_time``
     - Request start time
   * - ``end_time``
     - Request end time

Shared Request Records
----------------------

With ActionCore request-context support, HTTP wrappers can also capture RequestRecord v1 in an explicit run scope. Native responses and legacy reports keep their existing formats. HTTP and assertion failures retain the actual status; transport failures use null for unknown measurements. Successful calls with `record_request_info=False` are excluded; failures remain recorded. Bodies and headers are omitted by default. `from_legacy_record(..., capture_payload=True)` enables payload import and masks sensitive headers. Each context has independent records; `clean_record()` only clears the legacy singleton.

.. code-block:: python

   from je_api_testka import test_api_method_requests
   from je_api_testka.utils.test_record.run_context import RunContext, use_run_context

   run = RunContext(source="apitestka", phase="functional", engine="requests")
   with use_run_context(run):
       test_api_method_requests("get", "http://localhost:8091/get")
   records_json = run.to_json()

Canonical end times use the start timestamp plus monotonic elapsed time, so wall clock corrections cannot reverse the interval. Runner/configuration failures are distinct from connection and other transport errors.
