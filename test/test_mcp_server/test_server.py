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


def test_mcp_extra_allows_both_sdk_lines():
    """``build_server`` supports the 1.x decorators and the 2.x constructor handlers."""
    tomllib = pytest.importorskip("tomllib")
    from packaging.requirements import Requirement

    with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
        specs = tomllib.load(handle)["project"]["optional-dependencies"]["mcp"]
    requirement = Requirement(specs[0])
    assert requirement.name == "mcp"
    assert not requirement.specifier.contains("1.28.0")  # HTTP / WebSocket transport advisories
    assert requirement.specifier.contains("1.30.0")
    assert requirement.specifier.contains("2.2.0")
    assert not requirement.specifier.contains("3.0.0")


class _Text:
    def __init__(self, type, text):  # noqa: A002 - mirrors mcp.types.TextContent
        self.type, self.text = type, text


class _Record:
    def __init__(self, **fields):
        self.__dict__.update(fields)


def _symbols(server_cls):
    return server._MCPSymbols(server_cls=server_cls, stdio_server=None, tool_cls=_Record, text_content_cls=_Text,
                              list_tools_result_cls=_Record, call_tool_result_cls=_Record)


class _DecoratedServer:
    """Stands in for the 1.x low-level Server: handlers come in through decorators."""

    def __init__(self, name):
        self.name, self.handlers = name, {}

    def list_tools(self):
        return lambda fn: self.handlers.setdefault("list", fn)

    def call_tool(self):
        return lambda fn: self.handlers.setdefault("call", fn)


class _HandlerServer:
    """Stands in for the 2.x low-level Server: handlers are constructor arguments."""

    def __init__(self, name, on_list_tools, on_call_tool):
        self.name, self.handlers = name, {"list": on_list_tools, "call": on_call_tool}


async def test_decorated_server_for_the_1x_sdk(monkeypatch):
    monkeypatch.setattr(server, "_import_mcp", lambda: _symbols(_DecoratedServer))
    instance = server.build_server()
    tools = await instance.handlers["list"]()
    content = await instance.handlers["call"]("no_such_tool", {})
    assert [tool.name for tool in tools] == [spec.name for spec in server.APITESTKA_TOOLS]
    assert "unknown MCP tool" in content[0].text


async def test_handler_server_for_the_2x_sdk(monkeypatch):
    monkeypatch.setattr(server, "_import_mcp", lambda: _symbols(_HandlerServer))
    instance = server.build_server()
    listed = await instance.handlers["list"](None, None)
    failed = await instance.handlers["call"](None, _Record(name="no_such_tool", arguments=None))
    assert [tool.name for tool in listed.tools] == [spec.name for spec in server.APITESTKA_TOOLS]
    assert failed.isError is True
    assert "unknown MCP tool" in failed.content[0].text


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
