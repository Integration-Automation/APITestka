======
安裝
======

從 PyPI 安裝
-------------

.. code-block:: bash

   pip install je_api_testka

安裝 GUI 支援
--------------

.. code-block:: bash

   pip install je_api_testka[gui]

系統需求
--------

- **Python** 3.10 或更高版本
- **依賴套件：** ``requests``、``Flask``、``httpx``
- **選用（GUI）：** ``PySide6==6.11.0``、``qt-material``

開發環境設定
------------

.. code-block:: bash

   # 複製儲存庫
   git clone https://github.com/Intergration-Automation-Testing/APITestka.git
   cd APITestka

   # 安裝開發依賴
   pip install -r dev_requirements.txt

   # 執行測試
   pytest
