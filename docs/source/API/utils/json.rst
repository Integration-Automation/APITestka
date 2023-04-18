JSON API
----

.. code-block:: python

    def read_action_json(json_file_path: str):
        """
        read the action json
        :param json_file_path json file's path to read
        """

.. code-block:: python

    def write_action_json(json_save_path: str, action_json: list):
        """
        write action json
        :param json_save_path  json save path
        :param action_json the json str include action to write
        """

.. code-block:: python

    def reformat_json(json_string: str, **kwargs):
        """
        :param json_string: valid json string
        :param kwargs: indent, sort_keys or another args
        :return: None
        """