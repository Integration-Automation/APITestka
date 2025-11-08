from typing import Union
from importlib import import_module
from importlib.util import find_spec
from inspect import getmembers, isfunction, isbuiltin, isclass
from sys import stderr

from je_api_testka.utils.logging.loggin_instance import apitestka_logger


class PackageManager(object):

    def __init__(self):
        """
        初始化套件管理器
        Initialize package manager
        """
        apitestka_logger.info("Init PackageManager")
        # 已安裝套件字典，用來快取已載入的套件
        # Dictionary to cache installed packages
        self.installed_package_dict = {}
        # 執行器與回呼執行器
        # Executor and callback executor
        self.executor = None
        self.callback_executor = None

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
                    installed_package = import_module(found_spec.name)
                    self.installed_package_dict.update({found_spec.name: installed_package})
                except ModuleNotFoundError as error:
                    print(repr(error), file=stderr)
        return self.installed_package_dict.get(package, None)

    def add_package_to_executor(self, package):
        """
        將套件的函式加入 executor
        Add package functions to executor

        :param package: 套件名稱 / Package name
        """
        apitestka_logger.info(f"PackageManager add_package_to_executor package: {package}")
        self.add_package_to_target(package=package, target=self.executor)

    def add_package_to_callback_executor(self, package) -> None:
        """
        將套件的函式加入 callback_executor
        Add package functions to callback executor

        :param package: 套件名稱 / Package name
        """
        apitestka_logger.info(f"PackageManager add_package_to_callback_executor package: {package}")
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
            print(repr(ModuleNotFoundError(f"Can't find package {package}")), file=stderr)
        else:
            print(f"Executor error {self.executor}", file=stderr)

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
            self.get_member(package=package, predicate=isfunction, target=target)
            self.get_member(package=package, predicate=isclass, target=target)
        except Exception as error:
            print(repr(error), file=stderr)


# 建立全域套件管理器實例
# Create global package manager instance
package_manager = PackageManager()