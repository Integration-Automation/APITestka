Assert Result API
----

.. code-block:: python

    def check_result(result_dict: dict, result_check_dict: dict):
        """
        :param result_dict: response result dict (get_api_response_data's return data)
        :param result_check_dict: the dict include data name and value to check result_dict is valid or not
        :return: True if no error None if check failed
        """