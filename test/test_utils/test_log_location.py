"""Where APITestka's log goes, and that importing the package writes nothing (workspace item X-6)."""
import logging
import os
import subprocess  # nosec B404 - the import is exercised in a fresh interpreter
import sys
import warnings
from pathlib import Path

from je_api_testka.utils.logging.loggin_instance import (
    LOG_FILE_ENV,
    APITestkaLoggingHandler,
    apitestka_logger,
    default_log_file,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _log(handler: logging.Handler, message: str) -> None:
    log = logging.getLogger(f"test_log_location.{id(handler)}")
    log.propagate = False
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    try:
        log.warning(message)
    finally:
        log.removeHandler(handler)
        handler.close()


def test_default_is_under_the_home_directory(monkeypatch, tmp_path):
    monkeypatch.delenv(LOG_FILE_ENV, raising=False)
    monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
    assert default_log_file() == tmp_path / ".je_api_testka" / "logs" / "APITestka.log"


def test_environment_variable_overrides_the_location(monkeypatch, tmp_path):
    monkeypatch.setenv(LOG_FILE_ENV, str(tmp_path / "custom.log"))
    assert default_log_file() == tmp_path / "custom.log"


def test_importing_the_package_writes_nothing_and_leaves_root_alone(tmp_path):
    target = tmp_path / "home" / "APITestka.log"
    env = {key: value for key, value in os.environ.items() if key != LOG_FILE_ENV}
    env[LOG_FILE_ENV] = str(target)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")]))
    code = "import logging, os, je_api_testka; print(sorted(os.listdir('.')), logging.getLogger().level)"
    result = subprocess.run(  # nosec B603 - fixed interpreter, test-controlled arguments
        [sys.executable, "-c", code], cwd=tmp_path, env=env,
        capture_output=True, text=True, timeout=120, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"[] {logging.WARNING}"
    assert not target.parent.exists()


def test_the_package_logger_keeps_debug_on_its_own_level():
    assert apitestka_logger.level == logging.DEBUG


def test_first_record_creates_the_directory_and_later_handlers_append(tmp_path):
    target = tmp_path / "nested" / "APITestka.log"
    _log(APITestkaLoggingHandler(str(target)), "first")
    _log(APITestkaLoggingHandler(str(target)), "second 中文 ⠐ \udcff")
    text = target.read_text(encoding="utf-8")
    assert "first" in text and "second 中文 ⠐" in text and "\\udcff" in text


def test_an_unopenable_path_only_warns(tmp_path):
    blocker = tmp_path / "a_file"
    blocker.write_text("x", encoding="utf-8")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _log(APITestkaLoggingHandler(str(blocker / "APITestka.log")), "goes nowhere")
    assert any(issubclass(item.category, RuntimeWarning) for item in caught)
