"""`dev.toml` builds the `je_api_testka_dev` package from the same code as `pyproject.toml`.

It had fallen behind: no console scripts, no `pytest11` entry point and only the `gui` extra, so the
dev package installed without `apitestka`, `apitestka-mcp` or the pytest plugin (progress.md #5).
Everything but the name and the version has to match.
"""
from pathlib import Path

import pytest

tomllib = pytest.importorskip("tomllib")  # stdlib from 3.11; CI also runs 3.10

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(name: str) -> dict:
    with (REPO_ROOT / name).open("rb") as handle:
        return tomllib.load(handle)


STABLE = _load("pyproject.toml")
DEV = _load("dev.toml")


def test_names_differ():
    assert STABLE["project"]["name"] == "je_api_testka"
    assert DEV["project"]["name"] == "je_api_testka_dev"


@pytest.mark.parametrize("key", [
    "dependencies", "requires-python", "optional-dependencies", "scripts", "entry-points",
])
def test_project_tables_match(key):
    assert DEV["project"].get(key) == STABLE["project"].get(key)


def test_tool_settings_match():
    assert DEV.get("tool") == STABLE.get("tool")
