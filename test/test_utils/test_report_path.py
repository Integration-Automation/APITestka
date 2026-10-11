"""Under TestPioneer a report asked for under a relative name goes below ``TEST_PIONEER_ARTIFACT_DIR``."""
from pathlib import Path

import pytest

from je_api_testka.utils.generate_report.allure_report import generate_allure_report
from je_api_testka.utils.generate_report.badge import generate_badge
from je_api_testka.utils.generate_report.html_report_generate import generate_html_report
from je_api_testka.utils.generate_report.json_report import generate_json_report
from je_api_testka.utils.generate_report.junit_report import generate_junit_report
from je_api_testka.utils.generate_report.markdown_report import generate_markdown_report
from je_api_testka.utils.generate_report.report_path import ARTIFACT_DIR_VARIABLE, report_path
from je_api_testka.utils.generate_report.xml_report import generate_xml_report
from je_api_testka.utils.test_record.test_record_class import test_record_instance


def _record():
    return {
        "status_code": 200, "text": "ok", "content": b"ok", "headers": {}, "history": [], "encoding": "utf-8",
        "cookies": {}, "elapsed": 0.1, "request_time_sec": 0.1, "request_method": "GET",
        "request_url": "https://example.test/", "request_body": None, "start_time": "s", "end_time": "e",
    }


@pytest.fixture
def artifact_dir(tmp_path, monkeypatch):
    """A TestPioneer run: the variable is set, and the working directory is somewhere else."""
    directory = tmp_path / "artifacts" / "run-1" / "runners" / "api-runner" / "01-api"
    work = tmp_path / "work"
    work.mkdir()
    monkeypatch.chdir(work)
    monkeypatch.setenv(ARTIFACT_DIR_VARIABLE, str(directory))
    return directory


def test_a_name_is_returned_as_given_outside_testpioneer(monkeypatch):
    monkeypatch.delenv(ARTIFACT_DIR_VARIABLE, raising=False)
    assert report_path("reports/api") == "reports/api"


def test_an_empty_variable_counts_as_unset(monkeypatch):
    monkeypatch.setenv(ARTIFACT_DIR_VARIABLE, "  ")
    assert report_path("reports/api") == "reports/api"


def test_a_relative_name_goes_below_the_artifact_directory(artifact_dir):
    target = Path(report_path("reports/api_success.json"))
    assert target == artifact_dir.resolve() / "reports" / "api_success.json"
    assert target.parent.is_dir()


def test_an_absolute_name_is_left_alone(artifact_dir, tmp_path):
    name = str(tmp_path / "elsewhere" / "api.json")
    assert report_path(name) == name
    assert not artifact_dir.exists()


def test_a_name_that_leaves_the_directory_is_left_alone(artifact_dir):
    assert report_path("../outside.json") == "../outside.json"
    assert not artifact_dir.exists()


def test_a_directory_that_cannot_be_created_falls_back_to_the_name(tmp_path, monkeypatch):
    not_a_directory = tmp_path / "file"
    not_a_directory.write_text("x", encoding="utf-8")
    monkeypatch.setenv(ARTIFACT_DIR_VARIABLE, str(not_a_directory))
    assert report_path("reports/api.json") == "reports/api.json"


@pytest.mark.parametrize("generate, name, written", [
    (generate_json_report, "reports/api", ["reports/api_success.json", "reports/api_failure.json"]),
    (generate_xml_report, "reports/api", ["reports/api_success.xml", "reports/api_failure.xml"]),
    (generate_html_report, "reports/api", ["reports/api.html"]),
    (generate_junit_report, "reports/junit.xml", ["reports/junit.xml"]),
    (generate_markdown_report, "reports/api.md", ["reports/api.md"]),
    (generate_badge, "reports/badge.json", ["reports/badge.json"]),
], ids=["json", "xml", "html", "junit", "markdown", "badge"])
def test_every_report_is_written_below_the_artifact_directory(artifact_dir, generate, name, written):
    test_record_instance.test_record_list.append(_record())
    generate(name)
    assert [(artifact_dir / path).is_file() for path in written] == [True] * len(written)
    # Nothing is left in the working directory, where the name used to point.
    assert not Path("reports").exists()


def test_the_allure_results_are_written_below_the_artifact_directory(artifact_dir):
    test_record_instance.test_record_list.append(_record())
    results = generate_allure_report("allure-results")
    assert [result.parent for result in results] == [artifact_dir.resolve() / "allure-results"]
    assert not Path("allure-results").exists()


def test_outside_testpioneer_a_report_stays_in_the_working_directory(tmp_path, monkeypatch):
    monkeypatch.delenv(ARTIFACT_DIR_VARIABLE, raising=False)
    monkeypatch.chdir(tmp_path)
    test_record_instance.test_record_list.append(_record())
    generate_json_report("api")
    assert (tmp_path / "api_success.json").is_file()
