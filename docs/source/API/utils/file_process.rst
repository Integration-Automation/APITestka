============
File Process
============

.. code-block:: python

   def get_dir_files_as_list(
       dir_path: str | None = None,
       default_search_file_extension: str = ".json"
   ) -> list[str]:

Get files from a directory matching a file extension, as absolute paths (je_action_core's
``get_dir_files_as_list``).

:param dir_path: directory to search (default: the current working directory when called)
:param default_search_file_extension: file extension filter (default: ``.json``)
:return: list of matching file paths, or empty list if none found
