"""
Importing the fixtures directly avoids the duplicate-plugin-registration
collision that ``pytest_plugins = [...]`` would cause when the package's
``pytest11`` entry point (set in ``pyproject.toml``) is also active.
"""
from je_api_testka.pytest_plugin.plugin import (  # noqa: F401 - re-exported as fixtures
    apitestka_clean_record,
    apitestka_record,
)
