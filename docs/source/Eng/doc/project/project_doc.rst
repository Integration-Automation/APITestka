====================
Project Scaffolding
====================

Generate a project structure with keyword and executor templates:

.. code-block:: python

   from je_api_testka import create_project_dir

   create_project_dir(project_path=".", parent_name="MyAPIProject")

Generated Structure
-------------------

.. code-block:: text

   MyAPIProject/
   +-- keyword/
   |   +-- keyword1.json          # Example keyword test (POST)
   |   +-- keyword2.json          # Example keyword test (GET)
   |   +-- bad_keyword_1.json     # Example with package loading
   +-- executor/
       +-- executor_one_file.py   # Execute a single keyword file
       +-- executor_folder.py     # Execute all keyword files in directory
       +-- executor_bad_file.py   # Example with dynamic package loading
