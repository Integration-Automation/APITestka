============
Installation
============

Install from PyPI
-----------------

.. code-block:: bash

   pip install je_api_testka

Install with GUI support
------------------------

.. code-block:: bash

   pip install je_api_testka[gui]

Requirements
------------

- **Python** 3.10 or later
- **Dependencies:** ``requests``, ``Flask``, ``httpx``
- **Optional (GUI):** ``PySide6==6.11.0``, ``qt-material``

Development Setup
-----------------

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Intergration-Automation-Testing/APITestka.git
   cd APITestka

   # Install development dependencies
   pip install -r dev_requirements.txt

   # Run tests
   pytest
