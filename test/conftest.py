import pytest

from je_api_testka.utils.test_record.test_record_class import test_record_instance


@pytest.fixture(autouse=True)
def clean_test_records():
    """Clean test records before each test to avoid cross-test pollution."""
    test_record_instance.clean_record()
    yield
    test_record_instance.clean_record()
