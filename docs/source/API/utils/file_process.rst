============
File Process
============

.. code-block:: python

   def get_dir_files_as_list(
       dir_path: str = getcwd(),
       default_search_file_extension: str = ".json"
   ) -> list:

Get files from a directory matching a file extension.

:param dir_path: directory to search
:param default_search_file_extension: file extension filter (default: ``.json``)
:return: list of matching file paths, or empty list if none found
