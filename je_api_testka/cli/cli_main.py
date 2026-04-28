"""
Subcommand-style CLI for APITestka.

Subcommands:
    run         Execute an action JSON file or directory.
    create      Scaffold a new project.
    mock        Start the bundled Flask mock server.
    import      Convert OpenAPI/Postman documents into action JSON.
    repl        Interactive JSON-action REPL.
    summary     Print a terminal summary of the latest run.
    scaffold    Generate a starter action JSON for a URL.
    completion  Print a shell completion script.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from je_api_testka.utils.executor.action_executor import execute_action, execute_files
from je_api_testka.utils.file_process.get_dir_file_list import get_dir_files_as_list
from je_api_testka.utils.json.json_file.json_file import read_action_json
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.project.create_project_structure import create_project_dir

DEFAULT_MOCK_HOST: str = "127.0.0.1"
DEFAULT_MOCK_PORT: int = 8090


def _cmd_run(args: argparse.Namespace) -> int:
    target = Path(args.path)
    if target.is_dir():
        execute_files(get_dir_files_as_list(str(target)))
    elif target.is_file():
        execute_action(read_action_json(str(target)))
    else:
        apitestka_logger.error(f"cli run: path not found: {target}")
        return 2
    return 0


def _cmd_create(args: argparse.Namespace) -> int:
    create_project_dir(args.path)
    return 0


def _cmd_mock(args: argparse.Namespace) -> int:
    from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

    server = FlaskMockServer(args.host, args.port)
    server.start_mock_server()
    return 0


def _cmd_import(args: argparse.Namespace) -> int:
    from je_api_testka.cli.import_specs import convert_spec_file

    actions = convert_spec_file(args.input, args.format)
    output = Path(args.output)
    output.write_text(json.dumps(actions, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


def _cmd_repl(_args: argparse.Namespace) -> int:
    from je_api_testka.cli.repl import repl_loop

    repl_loop()
    return 0


def _cmd_summary(_args: argparse.Namespace) -> int:
    from je_api_testka.cli.tui_summary import print_terminal_summary

    print_terminal_summary()
    return 0


def _cmd_scaffold(args: argparse.Namespace) -> int:
    from je_api_testka.cli.scaffold_test import write_scaffold

    write_scaffold(args.output, args.url, method=args.method)
    return 0


def _cmd_completion(args: argparse.Namespace) -> int:
    from je_api_testka.cli.completion import generate_completion_script

    print(generate_completion_script(args.shell))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="apitestka", description="APITestka command line")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Execute action JSON file or directory")
    run_parser.add_argument("path", help="JSON file or directory of JSON files")
    run_parser.set_defaults(func=_cmd_run)

    create_parser = sub.add_parser("create", help="Scaffold a project directory")
    create_parser.add_argument("path", help="Target directory for the new project")
    create_parser.set_defaults(func=_cmd_create)

    mock_parser = sub.add_parser("mock", help="Start the Flask mock server")
    mock_parser.add_argument("--host", default=DEFAULT_MOCK_HOST)
    mock_parser.add_argument("--port", type=int, default=DEFAULT_MOCK_PORT)
    mock_parser.set_defaults(func=_cmd_mock)

    import_parser = sub.add_parser("import", help="Convert specs to action JSON")
    import_parser.add_argument("input", help="OpenAPI / Postman collection file")
    import_parser.add_argument("output", help="Destination JSON file")
    import_parser.add_argument(
        "--format",
        choices=("openapi", "postman"),
        default="openapi",
        help="Source spec format",
    )
    import_parser.set_defaults(func=_cmd_import)

    repl_parser = sub.add_parser("repl", help="Interactive JSON-action REPL")
    repl_parser.set_defaults(func=_cmd_repl)

    summary_parser = sub.add_parser("summary", help="Print terminal summary of latest run")
    summary_parser.set_defaults(func=_cmd_summary)

    scaffold_parser = sub.add_parser("scaffold", help="Generate starter action JSON for a URL")
    scaffold_parser.add_argument("url", help="Target URL")
    scaffold_parser.add_argument("output", help="Destination JSON file")
    scaffold_parser.add_argument("--method", default="GET")
    scaffold_parser.set_defaults(func=_cmd_scaffold)

    completion_parser = sub.add_parser("completion", help="Print shell completion script")
    completion_parser.add_argument("shell", choices=("bash", "zsh", "fish", "powershell"))
    completion_parser.set_defaults(func=_cmd_completion)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
