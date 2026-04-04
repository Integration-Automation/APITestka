===============
Package Manager
===============

PackageManager Class
--------------------

.. code-block:: python

   class PackageManager:

       def check_package(self, package: str):
           """
           Check if a package exists and import it.

           :param package: package name to check
           :return: imported package or None
           """

       def add_package_to_executor(self, package: str):
           """
           Add a package's functions to the executor.

           :param package: package name
           """

       def add_package_to_callback_executor(self, package: str):
           """
           Add a package's functions to the callback executor.

           :param package: package name
           """
