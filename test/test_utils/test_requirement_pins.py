"""Versions pinned with ``==`` in the requirements files match the ones the package pins.

``requirements.txt`` and ``dev_requirements.txt`` set up a working copy, while
``pyproject.toml`` is what users install. The two drifted: ``dev_requirements.txt``
kept an older PySide6 after ``pyproject.toml`` moved to 6.11.2, so a developer
tested against a different Qt than the release ships. For example
``_pins(["PySide6==6.11.2"])`` is ``{"pyside6": "6.11.2"}``.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

tomllib = pytest.importorskip("tomllib")  # stdlib from 3.11; CI also runs 3.10

REPO_ROOT = Path(__file__).resolve().parents[2]
_PIN = re.compile(r"^\s*([A-Za-z0-9._-]+)\s*==\s*([^\s;#,]+)")


def _normalise(name: str) -> str:
    """Return the PEP 503 form of a distribution name (``Pyside6`` and ``PySide6`` are one)."""
    return re.sub(r"[-_.]+", "-", name).lower()


def _pins(requirements: list[str]) -> dict[str, str]:
    """Map each ``name==version`` requirement to its version, keyed by normalised name."""
    return {_normalise(match.group(1)): match.group(2)
            for match in (_PIN.match(line) for line in requirements) if match}


def _package_requirements() -> list[str]:
    """Return the dependencies and every optional-dependency group of ``pyproject.toml``."""
    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    requirements = list(project.get("dependencies", []))
    for group in project.get("optional-dependencies", {}).values():
        requirements.extend(group)
    return requirements


@pytest.mark.parametrize("name", ["requirements.txt", "dev_requirements.txt"])
def test_requirements_file_pins_what_the_package_pins(name):
    path = REPO_ROOT / name
    if not path.is_file():
        pytest.skip(f"{name} does not exist")
    local = _pins(path.read_text(encoding="utf-8").splitlines())
    package = _pins(_package_requirements())
    assert {dist: (local[dist], package[dist]) for dist in local.keys() & package.keys()
            if local[dist] != package[dist]} == {}
