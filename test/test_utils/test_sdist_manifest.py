"""The source distribution carries no test suite.

setuptools adds ``test/test*.py`` to an sdist by default, so ``je_api_testka_dev`` 0.0.130 shipped two
loose test modules without ``test/conftest.py`` or the test packages beside them. ``MANIFEST.in`` prunes
the directory instead. Its commands run in order, so ``prune test`` only holds while no later command
adds files again. The file is read as text: nothing is built at test time.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TEST_DIRECTORY = "test"
ADDING_COMMANDS = {"include", "recursive-include", "global-include", "graft"}


def _commands(text: str) -> list[list[str]]:
    """Split ``MANIFEST.in`` text into ``[command, argument, ...]`` lists, without comments."""
    lines = (line.split("#", 1)[0].split() for line in text.splitlines())
    return [words for words in lines if words]


def _prunes_tests_for_good(commands: list[list[str]]) -> bool:
    """Tell whether ``prune test`` is there and no command after it can add files."""
    prune = ["prune", TEST_DIRECTORY]
    if prune not in commands:
        return False
    last = len(commands) - 1 - commands[::-1].index(prune)
    return not any(words[0] in ADDING_COMMANDS for words in commands[last + 1:])


def test_the_test_directory_is_the_one_pytest_collects():
    assert (REPO_ROOT / TEST_DIRECTORY / "conftest.py").is_file()


def test_manifest_prunes_the_test_directory_and_nothing_brings_it_back():
    text = (REPO_ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert _prunes_tests_for_good(_commands(text))


def test_the_check_sees_a_missing_prune_and_a_later_include():
    assert _prunes_tests_for_good(_commands("graft docs\nprune test  # no tests\n"))
    assert not _prunes_tests_for_good(_commands("# prune test\n"))
    assert not _prunes_tests_for_good(_commands("prune tests\n"))
    assert not _prunes_tests_for_good(_commands("prune test\nrecursive-include test *.py\n"))
    assert not _prunes_tests_for_good(_commands("prune test\nglobal-include *.py\n"))
