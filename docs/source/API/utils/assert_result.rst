=============
Assert Result
=============

.. code-block:: python

   def check_result(result_dict: dict, result_check_dict: dict):

Check if the API response matches expected values.

:param result_dict: response result dict (from ``get_api_response_data``)
:param result_check_dict: dict with field names and expected values to validate
:return: ``True`` if all checks pass
:raises: ``APIAssertException`` if any check fails
