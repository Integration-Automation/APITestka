"""
Minimal REPL for APITestka.

Reads a JSON action per line from stdin, executes it, prints the result, and
loops. Exit with ``exit`` / ``quit`` or EOF. Designed for piping in scripts as
well as interactive use.
"""
from __future__ import annotations

import json
import sys
from typing import Iterable, TextIO

from je_api_testka.utils.executor.action_executor import execute_action

PROMPT: str = "apitestka> "
EXIT_TOKENS = ("exit", "quit")


def repl_loop(input_stream: TextIO = None, output_stream: TextIO = None,
              show_prompt: bool = True) -> int:
    """Run the REPL until EOF; return the number of commands processed."""
    inp = input_stream or sys.stdin
    out = output_stream or sys.stdout
    processed = 0
    for line in _iter_lines(inp, out, show_prompt):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower() in EXIT_TOKENS:
            break
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError as error:
            print(f"invalid JSON: {error}", file=out)
            continue
        try:
            result = execute_action(payload if isinstance(payload, list) else [payload])
            print(json.dumps(_jsonable(result), default=str, ensure_ascii=False), file=out)
            processed += 1
        except Exception as error:
            print(f"error: {error!r}", file=out)
    return processed


def _iter_lines(inp: TextIO, out: TextIO, show_prompt: bool) -> Iterable[str]:
    while True:
        if show_prompt:
            out.write(PROMPT)
            out.flush()
        line = inp.readline()
        if not line:
            return
        yield line


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonable(v) for v in value]
    if hasattr(value, "__dict__"):
        return _jsonable(value.__dict__)
    return value
