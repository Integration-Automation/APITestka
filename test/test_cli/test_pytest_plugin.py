"""Smoke test that the apitestka pytest plugin fixtures are importable."""
from __future__ import annotations


def test_record_fixture_clears(apitestka_record):
    apitestka_record.test_record_list.append({"x": 1})
    assert apitestka_record.test_record_list


def test_record_fixture_was_cleaned_between_tests(apitestka_record):
    """Previous test left an entry; this fixture's teardown should have wiped it."""
    assert apitestka_record.test_record_list == []


def test_clean_record_fixture(apitestka_clean_record):
    """Fixture exists and yields without raising."""
    assert apitestka_clean_record is None
