"""
MCP server entry point.

Exposes the APITestka tool catalogue over the standard input/output transport
defined by the Model Context Protocol. Requires the optional ``mcp`` package.

Run via:
    python -m je_api_testka.mcp_server
or:
    apitestka-mcp
"""
from __future__ import annotations

import asyncio
import json
from typing import Any, List

from je_api_testka.mcp_server.tool_definitions import APITESTKA_TOOLS, dispatch_tool
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger

MCP_NOT_INSTALLED: str = (
    "The 'mcp' package is required for the APITestka MCP server. "
    "Install with `pip install mcp`."
)


def _import_mcp():
    try:
        from mcp.server import Server  # type: ignore
        from mcp.server.stdio import stdio_server  # type: ignore
        from mcp.types import TextContent, Tool  # type: ignore
        return Server, stdio_server, Tool, TextContent
    except ImportError as error:
        apitestka_logger.error(f"mcp_server import mcp failed: {repr(error)}")
        raise APITesterException(MCP_NOT_INSTALLED) from error


def build_server():
    """Build and return a configured ``mcp.server.Server`` instance."""
    Server, _stdio_server, Tool, TextContent = _import_mcp()
    server = Server("apitestka")

    @server.list_tools()
    async def _list_tools() -> List[Any]:
        return [
            Tool(name=spec.name, description=spec.description, inputSchema=spec.input_schema)
            for spec in APITESTKA_TOOLS
        ]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict) -> List[Any]:
        try:
            result = dispatch_tool(name, arguments or {})
        except Exception as error:  # noqa: BLE001 - propagate to MCP client
            apitestka_logger.error(f"mcp_server dispatch_tool failed: {repr(error)}")
            return [TextContent(type="text", text=f"error: {error!r}")]
        if isinstance(result, str):
            return [TextContent(type="text", text=result)]
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, default=str))]

    return server


async def serve_stdio() -> None:
    """Run the server over stdio until the client disconnects."""
    Server, stdio_server, _Tool, _TextContent = _import_mcp()
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> int:
    asyncio.run(serve_stdio())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
