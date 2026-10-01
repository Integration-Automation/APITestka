import warnings
from importlib import import_module
from importlib.util import find_spec
from inspect import getmembers, isbuiltin, isclass, isfunction
from typing import Optional, Set, Union

from je_api_testka.utils.exception.exceptions import APITesterExecuteException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class PackageManager:
    """Imports packages for ``AT_add_package_to_executor`` behind a package gate."""

    def __init__(self):
        """
        初始化套件管理器
        Initialize package manager
        """
        # 已安裝套件字典，用來快取已載入的套件
        # Dictionary to cache installed packages
        self.installed_package_dict = {}
        # 執行器與回呼執行器
        # Executor and callback executor
        self.executor = None
        self.callback_executor = None
        # 套件閘門：None 表示未設定（任何套件仍會載入，但發出 DeprecationWarning）
        # Package gate. None = not configured: any package still loads, with a
        # DeprecationWarning. False = only ``allowed_packages``; True = any package, silently.
        self.allow_arbitrary_packages: Optional[bool] = None
        self.allowed_packages: Set[str] = set()

    def set_allow_arbitrary_packages(self, enabled: bool) -> None:
        """
        設定是否允許載入允許清單以外的套件
        Allow (True) or refuse (False) packages outside :attr:`allowed_packages`.
        Deliberately not an ``AT_*`` command: an action file must not open its own gate.
        """
        self.allow_arbitrary_packages = bool(enabled)

    def allow_packages(self, *packages: str) -> None:
        """
        把套件加入允許清單（連同其子模組）
        Add packages to the allowlist; a listed package also allows its submodules.
        """
        self.allowed_packages.update(packages)

    def _is_allowlisted(self, package: str) -> bool:
        return any(package == allowed or package.startswith(allowed + ".") for allowed in self.allowed_packages)

    def _check_allowed(self, package: object) -> None:
        """Refuse ``package`` before it is imported, unless the gate lets it through."""
        if isinstance(package, str) and self._is_allowlisted(package):
            return
        if self.allow_arbitrary_packages is True:
            return
        if self.allow_arbitrary_packages is False:
            raise APITesterExecuteException(
                f"package {package!r} is not allowed; the host must call "
                "executor.allow_packages(...) or executor.set_allow_arbitrary_packages(True)"
            )
        warnings.warn(
            f"loading package {package!r} that is not on the allowlist; a future release will refuse "
            "it by default. Call executor.allow_packages(...) for the packages you load, or "
            "executor.set_allow_arbitrary_packages(True) to keep loading any package.",
            DeprecationWarning,
            stacklevel=3,
        )

    def check_package(self, package: str) -> Union[str, None]:
        """
        檢查套件是否存在並載入
        Check if package exists and import it

        :param package: 要檢查的套件名稱 / Package name to check
        :return: 套件物件若找到，否則 None / Package object if found, else None
        """
        apitestka_logger.info(f"PackageManager check_package package: {package}")
        if self.installed_package_dict.get(package, None) is None:
            found_spec = find_spec(package)
            if found_spec is not None:
                try:
                    # Plugin loader: package name resolved through importlib.find_spec first,
                    # so import_module receives a verified spec.name, not raw user input.
                    installed_package = import_module(found_spec.name)  # nosemgrep
                    self.installed_package_dict.update({found_spec.name: installed_package})
                except ModuleNotFoundError as error:
                    apitestka_logger.error(repr(error))
        return self.installed_package_dict.get(package, None)

    def add_package_to_executor(self, package: str) -> None:
        """
        將套件的函式加入 executor
        Add package functions to executor

        :param package: 套件名稱 / Package name
        :raises APITesterExecuteException: when the package gate refuses ``package`` (nothing is imported).
        """
        apitestka_logger.info(f"PackageManager add_package_to_executor package: {package}")
        self._check_allowed(package)
        self.add_package_to_target(package=package, target=self.executor)

    def add_package_to_callback_executor(self, package: str) -> None:
        """
        將套件的函式加入 callback_executor
        Add package functions to callback executor

        :param package: 套件名稱 / Package name
        :raises APITesterExecuteException: when the package gate refuses ``package`` (nothing is imported).
        """
        apitestka_logger.info(f"PackageManager add_package_to_callback_executor package: {package}")
        self._check_allowed(package)
        self.add_package_to_target(package=package, target=self.callback_executor)

    def get_member(self, package, predicate, target) -> None:
        """
        取得套件成員並加入指定的 event_dict
        Get package members and add to target's event_dict

        :param package: 套件名稱 / Package name
        :param predicate: 過濾條件 (函式、內建、類別) / Predicate (function, builtin, class)
        :param target: 要加入的目標物件 / Target object to add members
        """
        apitestka_logger.info(
            f"PackageManager add_package_to_callback_executor package: {package} "
            f"predicate: {predicate} target: {target}"
        )
        installed_package = self.check_package(package)
        if installed_package is not None and target is not None:
            for member in getmembers(installed_package, predicate):
                # 將成員加入 event_dict，命名方式為 package_memberName
                # Add member to event_dict with naming convention package_memberName
                target.event_dict.update({str(package) + "_" + str(member[0]): member[1]})
        elif installed_package is None:
            apitestka_logger.error(repr(ModuleNotFoundError(f"Can't find package {package}")))
        else:
            apitestka_logger.error(f"Executor error {self.executor}")

    def add_package_to_target(self, package, target) -> None:
        """
        將套件的函式、內建方法、類別加入目標
        Add package functions, builtins, and classes to target

        :param package: 套件名稱 / Package name
        :param target: 要加入的目標物件 / Target object
        """
        try:
            self.get_member(package=package, predicate=isfunction, target=target)
            self.get_member(package=package, predicate=isbuiltin, target=target)
            self.get_member(package=package, predicate=isclass, target=target)
        except Exception as error:
            apitestka_logger.error(repr(error))


# 建立全域套件管理器實例
# Create global package manager instance
package_manager = PackageManager()
