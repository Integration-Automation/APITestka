"""Tests for the MCP server entry point.

We don't spin up the actual stdio transport here; we only verify that the
'mcp' optional-dependency error path surfaces a friendly message, and that
build_server() can be invoked when 'mcp' is available.
"""
from __future__ import annotations

import builtins

import pytest

from je_api_testka.mcp_server import server
from je_api_testka.utils.exception.exceptions import APITesterException


def test_import_mcp_raises_when_dep_missing(monkeypatch):
    real_import = builtins.__import__

    def _fake_import(name, *args, **kwargs):
        if name.startswith("mcp"):
            raise ImportError("simulated")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    with pytest.raises(APITesterException) as excinfo:
        server._import_mcp()
    assert "mcp" in str(excinfo.value).lower()


def test_build_server_runs_when_dep_available():
    """Skip when 'mcp' is not installed."""
    pytest.importorskip("mcp")
    instance = server.build_server()
    assert instance is not None
