==========
專案腳手架
==========

產生含有關鍵字與執行器範本的專案結構：

.. code-block:: python

   from je_api_testka import create_project_dir

   create_project_dir(project_path=".", parent_name="MyAPIProject")

產生的結構
----------

.. code-block:: text

   MyAPIProject/
   +-- keyword/
   |   +-- keyword1.json          # 範例關鍵字測試（POST）
   |   +-- keyword2.json          # 範例關鍵字測試（GET）
   |   +-- bad_keyword_1.json     # 含套件載入的範例
   +-- executor/
       +-- executor_one_file.py   # 執行單一關鍵字檔案
       +-- executor_folder.py     # 執行目錄中所有關鍵字檔案
       +-- executor_bad_file.py   # 含動態套件載入的範例
