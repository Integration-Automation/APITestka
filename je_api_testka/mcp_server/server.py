"""
MCP server entry point.

Exposes the APITestka tool catalogue over the standard input/output transport
defined by the Model Context Protocol. Requires the optional ``mcp`` package; both
SDK lines work: 1.x registers handlers with the ``list_tools`` / ``call_tool``
decorators, 2.x takes ``on_list_tools`` / ``on_call_tool`` in the constructor.

Run via:
    python -m je_api_testka.mcp_server
or:
    apitestka-mcp
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, List

from je_api_testka.mcp_server.tool_definitions import APITESTKA_TOOLS, dispatch_tool
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

MCP_NOT_INSTALLED: str = (
    "The 'mcp' package is required for the APITestka MCP server. "
    "Install with `pip install mcp`."
)


@dataclass
class _MCPSymbols:
    """Lazily-imported MCP class references and the stdio transport factory."""

    server_cls: Any
    stdio_server: Any
    tool_cls: Any
    text_content_cls: Any
    list_tools_result_cls: Any
    call_tool_result_cls: Any


def _import_mcp() -> _MCPSymbols:
    try:
        from mcp.server import Server  # type: ignore
        from mcp.server.stdio import stdio_server  # type: ignore
        from mcp.types import CallToolResult, ListToolsResult, TextContent, Tool  # type: ignore
    except ImportError as error:
        apitestka_logger.error(f"mcp_server import mcp failed: {repr(error)}")
        raise APITesterException(MCP_NOT_INSTALLED) from error
    return _MCPSymbols(
        server_cls=Server,
        stdio_server=stdio_server,
        tool_cls=Tool,
        text_content_cls=TextContent,
        list_tools_result_cls=ListToolsResult,
        call_tool_result_cls=CallToolResult,
    )


def _tools(symbols: _MCPSymbols) -> List[Any]:
    return [
        symbols.tool_cls(name=spec.name, description=spec.description, inputSchema=spec.input_schema)
        for spec in APITESTKA_TOOLS
    ]


def _call(symbols: _MCPSymbols, name: str, arguments: dict | None) -> tuple[List[Any], bool]:
    """Run one tool; returns its text content and whether it failed.

    A failure is reported to the client as ``error: ...`` text rather than raised.
    """
    text_content_cls = symbols.text_content_cls
    try:
        result = dispatch_tool(name, arguments or {})
    except Exception as error:  # noqa: BLE001 - propagate to MCP client
        apitestka_logger.error(f"mcp_server dispatch_tool failed: {repr(error)}")
        return [text_content_cls(type="text", text=f"error: {error!r}")], True
    if isinstance(result, str):
        return [text_content_cls(type="text", text=result)], False
    return [text_content_cls(
        type="text",
        text=json.dumps(result, ensure_ascii=False, default=str),
    )], False


def build_server():
    """Build and return a configured ``mcp.server.Server`` instance for the installed SDK line."""
    symbols = _import_mcp()
    if hasattr(symbols.server_cls, "list_tools"):
        return _build_decorated_server(symbols)
    return _build_handler_server(symbols)


def _build_decorated_server(symbols: _MCPSymbols):
    """1.x SDK: handlers registered with decorators; the SDK wraps returned content."""
    server = symbols.server_cls("apitestka")

    @server.list_tools()
    async def _list_tools() -> List[Any]:
        return _tools(symbols)

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> List[Any]:
        return _call(symbols, name, arguments)[0]

    return server


def _build_handler_server(symbols: _MCPSymbols):
    """2.x SDK: handlers passed to the constructor, returning full result objects."""

    async def on_list_tools(_ctx: Any, _params: Any) -> Any:
        return symbols.list_tools_result_cls(tools=_tools(symbols))

    async def on_call_tool(_ctx: Any, params: Any) -> Any:
        content, failed = _call(symbols, params.name, params.arguments)
        return symbols.call_tool_result_cls(content=content, isError=failed)

    return symbols.server_cls("apitestka", on_list_tools=on_list_tools, on_call_tool=on_call_tool)


async def serve_stdio() -> None:
    """Run the server over stdio until the client disconnects."""
    symbols = _import_mcp()
    server = build_server()
    async with symbols.stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> int:
    asyncio.run(serve_stdio())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
