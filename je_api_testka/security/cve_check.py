"""
CVE check that shells out to the optional ``pip-audit`` tool.

We deliberately do not implement our own vulnerability database; we delegate
to the well-tested PyPA project. If pip-audit is not installed, surface a
friendly error.
"""
from __future__ import annotations

import json
import shutil
import subprocess  # noqa: S404 - intentional, see _PIP_AUDIT_NOT_FOUND below
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
    completed = subprocess.run(  # noqa: S603 - args list, no shell=True
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
