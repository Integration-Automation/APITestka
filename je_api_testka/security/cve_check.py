"""
CVE check that shells out to the optional ``pip-audit`` tool.

We deliberately do not implement our own vulnerability database; we delegate
to the well-tested PyPA project. If pip-audit is not installed, surface a
friendly error.
"""
from __future__ import annotations

import json
import shutil
# We deliberately delegate to the optional pip-audit binary; argv is built
# from a list (no shell=True) and the path is resolved via shutil.which.
import subprocess  # noqa: S404
from typing import List

from je_api_testka.utils.exception.exceptions import APITesterException

PIP_AUDIT_NOT_FOUND: str = (
    "pip-audit binary not found. Install with `pip install pip-audit`."
)
PIP_AUDIT_TIMEOUT_SECONDS: int = 120


def run_pip_audit() -> List[dict]:
    """Run ``pip-audit --format json`` and return the parsed dependency list."""
    binary = shutil.which("pip-audit")
    if binary is None:
        raise APITesterException(PIP_AUDIT_NOT_FOUND)
    # binary path is resolved via shutil.which and arguments are a static list;
    # no untrusted input flows here.
    # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-audit.dangerous-subprocess-use-audit
    completed = subprocess.run(  # noqa: S603
        [binary, "--format", "json"],
        check=False,
        capture_output=True,
        text=True,
        timeout=PIP_AUDIT_TIMEOUT_SECONDS,
    )
    if not completed.stdout.strip():
        return []
    payload = json.loads(completed.stdout)
    if isinstance(payload, dict):
        return list(payload.get("dependencies") or [])
    if isinstance(payload, list):
        return payload
    return []
