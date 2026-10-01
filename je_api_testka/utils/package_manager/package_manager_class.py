"""
``AT_add_package_to_executor`` / ``AT_add_package_to_callback_executor``: je_action_core's package manager with
APITestka's settings (members named ``<package>_<member>``, the package gate on, errors logged).
"""
from je_action_core import PackageManager as _CorePackageManager
from je_action_core import PackageManagerSettings

from je_api_testka.utils.exception.exceptions import APITesterExecuteException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

_SETTINGS = PackageManagerSettings(
    handled=(Exception,),  # loading a package's members logs what goes wrong instead of failing the action
    refused=APITesterExecuteException,
    log_info=apitestka_logger.info,
    log_error=apitestka_logger.error,
)


class PackageManager(_CorePackageManager):
    """Imports packages for ``AT_add_package_to_executor`` behind the package gate (see je_action_core)."""

    def __init__(self) -> None:
        super().__init__(_SETTINGS)


# 建立全域套件管理器實例
# Create global package manager instance
package_manager = PackageManager()
