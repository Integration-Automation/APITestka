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

       def set_allow_arbitrary_packages(self, enabled: bool) -> None:
           """
           Allow (True) or refuse (False) packages outside the allowlist.
           Until it is called, any package loads with a DeprecationWarning.
           """

       def allow_packages(self, *packages: str) -> None:
           """
           Add packages, and their submodules, to the allowlist.
           """

       def add_package_to_executor(self, package: str) -> None:
           """
           Add a package's functions to the executor.

           :param package: package name
           :raises APITesterExecuteException: when the package gate refuses the package
           """

       def add_package_to_callback_executor(self, package: str) -> None:
           """
           Add a package's functions to the callback executor.

           :param package: package name
           :raises APITesterExecuteException: when the package gate refuses the package
           """

The package gate checks the name before anything is imported. ``Executor`` exposes the same two
switches as static methods (``executor.allow_packages(...)``,
``executor.set_allow_arbitrary_packages(...)``); neither is an ``AT_*`` command.
