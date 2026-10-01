"""
The CI workflow must be able to run the Qt widget tests on every OS.

Regression: the Ubuntu runners have no libEGL.so.1, so importing PySide6.QtWidgets failed and the
widget tests could only be skipped there. The workflow now installs Qt's system libraries on Linux
and sets APITESTKA_REQUIRE_QT, which makes a failed Qt import an error instead of a skip.
"""
from __future__ import annotations

import re
from pathlib import Path

CI_WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "ci.yml"
# The DT_NEEDED libraries of QtGui, QtWidgets and the offscreen plugin outside the base system.
QT_PACKAGES = ("libegl1", "libgl1", "libx11-6", "libxkbcommon0", "libfontconfig1", "libfreetype6")


def _steps() -> list:
    text = CI_WORKFLOW.read_text(encoding="utf-8")
    return re.split(r"\n      - ", text.split("\n    steps:\n", 1)[1])


def _step(name: str) -> str:
    step = next((step for step in _steps() if f"name: {name}" in step), "")
    assert step, f"ci.yml has no step named {name!r}"
    return step


def test_linux_installs_qt_system_libraries_before_the_tests():
    names = [re.search(r"name: (.+)", step).group(1) for step in _steps() if "name: " in step]
    install = _step("Install Qt runtime libraries (Linux)")
    assert names.index("Install Qt runtime libraries (Linux)") < names.index("Run tests")
    assert "if: runner.os == 'Linux'" in install
    for package in QT_PACKAGES:
        assert re.search(rf"\b{re.escape(package)}\b", install), package


def test_ci_requires_qt_for_the_widget_tests():
    assert re.search(r'APITESTKA_REQUIRE_QT: "1"', _step("Run tests"))
