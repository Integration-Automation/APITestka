"""Tests for the pip-audit wrapper."""
from __future__ import annotations

import pytest

from je_api_testka.security import cve_check
from je_api_testka.utils.exception.exceptions import APITesterException


def test_run_pip_audit_raises_when_binary_missing(monkeypatch):
    monkeypatch.setattr(cve_check.shutil, "which", lambda _name: None)
    with pytest.raises(APITesterException):
        cve_check.run_pip_audit()


def test_run_pip_audit_parses_dependency_array(monkeypatch):
    class _Result:
        stdout = '{"dependencies": [{"name": "requests", "vulns": []}]}'
        stderr = ""

    monkeypatch.setattr(cve_check.shutil, "which", lambda _name: "/usr/bin/pip-audit")
    monkeypatch.setattr(cve_check.subprocess, "run", lambda *a, **k: _Result())
    deps = cve_check.run_pip_audit()
    assert deps == [{"name": "requests", "vulns": []}]


def test_run_pip_audit_handles_empty_output(monkeypatch):
    class _Result:
        stdout = ""
        stderr = ""

    monkeypatch.setattr(cve_check.shutil, "which", lambda _name: "/usr/bin/pip-audit")
    monkeypatch.setattr(cve_check.subprocess, "run", lambda *a, **k: _Result())
    assert cve_check.run_pip_audit() == []
