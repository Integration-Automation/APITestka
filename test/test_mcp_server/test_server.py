"""Tests for the MCP server entry point.

We don't spin up the actual stdio transport here; we only verify that the
'mcp' optional-dependency error path surfaces a friendly message, and that
build_server() can be invoked when 'mcp' is available.
"""
from __future__ import annotations

import builtins
import os
import sys
from pathlib import Path

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


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_mcp_extra_stays_below_2():
    """mcp 2.x removed the decorators ``build_server`` uses; the server then crashed on start."""
    tomllib = pytest.importorskip("tomllib")
    from packaging.requirements import Requirement

    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        specs = tomllib.load(handle)["project"]["optional-dependencies"]["mcp"]
    requirement = Requirement(specs[0])
    assert requirement.name == "mcp"
    assert not requirement.specifier.contains("2.0.0")
    assert not requirement.specifier.contains("1.28.0")  # HTTP / WebSocket transport advisories
    assert requirement.specifier.contains("1.30.0")


async def test_stdio_round_trip_with_the_official_client(tmp_path):
    """Start ``apitestka-mcp``'s module over stdio and drive it the way an MCP host does."""
    pytest.importorskip("mcp")
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(REPO_ROOT), env.get("PYTHONPATH")]))
    params = StdioServerParameters(
        command=sys.executable, args=["-m", "je_api_testka.mcp_server.server"], env=env, cwd=str(tmp_path))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert {tool.name for tool in tools.tools} == {spec.name for spec in server.APITESTKA_TOOLS}
            result = await session.call_tool("no_such_tool", {})
    assert "unknown MCP tool" in result.content[0].text
