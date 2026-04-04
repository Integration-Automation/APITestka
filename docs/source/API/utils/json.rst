====
JSON
====

.. code-block:: python

   def read_action_json(json_file_path: str):

Read an action JSON file.

:param json_file_path: path to the JSON file

.. code-block:: python

   def write_action_json(json_save_path: str, action_json: list):

Write an action JSON file.

:param json_save_path: path to save the JSON file
:param action_json: action list to write

.. code-block:: python

   def reformat_json(json_string: str, **kwargs):

Reformat a JSON string.

:param json_string: valid JSON string
:param kwargs: ``indent``, ``sort_keys``, or other ``json.dumps`` arguments
