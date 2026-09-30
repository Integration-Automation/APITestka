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
    mcp         Run the MCP server over stdio.
    openapi     Infer an OpenAPI document from recorded traffic.
    contract    Record, verify and compare Pact-style consumer contracts.
    generate-tests  Write test actions for an OpenAPI document (AI backend or deterministic).
    load        Convert or run APITestka requests as a LoadDensity load test.
    trend       Record per-endpoint latencies, check for anomalies, write the trend report.
    spec        Check the committed OpenAPI document against the tests (test-as-spec loop).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

from je_api_testka.ai.backend import BACKEND_NAMES, select_ai_backend
from je_api_testka.ai.test_generator import generate_tests_from_openapi
from je_api_testka.cli.cli_common import run_action_path
from je_api_testka.cli.contract_cli import configure_contract_parser
from je_api_testka.cli.load_cli import configure_load_parser
from je_api_testka.cli.spec_cli import configure_spec_parser
from je_api_testka.cli.trend_cli import configure_trend_parser
from je_api_testka.contract.commands import read_openapi
from je_api_testka.spec.openapi_export import build_openapi
from je_api_testka.spec.records_to_openapi import DEFAULT_SPEC_TITLE, DEFAULT_SPEC_VERSION
from je_api_testka.utils.exception.exceptions import APIAIBackendException, APIContractException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger
from je_api_testka.utils.project.create_project_structure import create_project_dir

DEFAULT_MOCK_HOST: str = "127.0.0.1"
DEFAULT_MOCK_PORT: int = 8090


def _cmd_run(args: argparse.Namespace) -> int:
    return run_action_path(Path(args.path))


def _cmd_create(args: argparse.Namespace) -> int:
    create_project_dir(args.path)
    return 0


def _cmd_mock(args: argparse.Namespace) -> int:
    from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer
    from je_api_testka.utils.mock_server.mock_config import apply_mock_config, read_mock_config, stop_protocol_mocks

    server = FlaskMockServer(args.host, args.port)
    if args.config:
        endpoints = apply_mock_config(read_mock_config(args.config), server,
                                      base_dir=str(Path(args.config).resolve().parent))
        for kind, address in endpoints.items():
            apitestka_logger.info(f"cli mock: {kind} mock at {address}")
    try:
        server.start_mock_server()
    finally:
        stop_protocol_mocks()
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


def _cmd_mcp(_args: argparse.Namespace) -> int:
    from je_api_testka.mcp_server.server import main as mcp_main

    return mcp_main()


def _cmd_openapi(args: argparse.Namespace) -> int:
    if not args.report and not args.run:
        apitestka_logger.error("cli openapi: give at least one --report or --run")
        return 2
    for path in args.run:
        status = run_action_path(Path(path))
        if status:
            return status
    spec = build_openapi(args.report, title=args.title, version=args.api_version)
    if not spec["paths"]:
        apitestka_logger.error("cli openapi: no successful records to infer from")
        return 1
    text = json.dumps(spec, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _cmd_generate_tests(args: argparse.Namespace) -> int:
    try:
        spec = read_openapi(args.spec)
        if args.ai:
            select_ai_backend(args.ai, model=args.model, effort=args.effort)
    except (APIContractException, APIAIBackendException) as error:
        apitestka_logger.error(f"cli generate-tests: {error}")
        return 2
    text = json.dumps(generate_tests_from_openapi(spec), indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _configure_generate_tests_parser(generate_parser: argparse.ArgumentParser) -> None:
    generate_parser.add_argument("spec", help="OpenAPI document (JSON)")
    generate_parser.add_argument("-o", "--output", help="Destination action JSON file (default: stdout)")
    generate_parser.add_argument("--ai", choices=BACKEND_NAMES,
                                 help="AI backend to use (default: APITESTKA_AI_BACKEND, else noop)")
    generate_parser.add_argument("--model", help="Model for the anthropic backend")
    generate_parser.add_argument("--effort", choices=("low", "medium", "high", "xhigh", "max"),
                                 help="Effort for the anthropic backend")
    generate_parser.set_defaults(func=_cmd_generate_tests)


def _configure_openapi_parser(openapi_parser: argparse.ArgumentParser) -> None:
    openapi_parser.add_argument("--report", action="append", default=[], metavar="FILE",
                                help="Saved JSON success report (<name>_success.json); repeatable")
    openapi_parser.add_argument("--run", action="append", default=[], metavar="PATH",
                                help="Action JSON file or directory to execute first; repeatable")
    openapi_parser.add_argument("-o", "--output", help="Destination file (default: stdout)")
    openapi_parser.add_argument("--title", default=DEFAULT_SPEC_TITLE)
    openapi_parser.add_argument("--api-version", default=DEFAULT_SPEC_VERSION, help="info.version of the spec")
    openapi_parser.set_defaults(func=_cmd_openapi)


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
    mock_parser.add_argument("--config", help="JSON file with http, websocket and grpc mock endpoints")
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

    mcp_parser = sub.add_parser("mcp", help="Run the APITestka MCP server (stdio transport)")
    mcp_parser.set_defaults(func=_cmd_mcp)

    _configure_openapi_parser(sub.add_parser("openapi", help="Infer an OpenAPI document from recorded traffic"))
    configure_contract_parser(sub.add_parser("contract", help="Record, verify and compare consumer contracts"))
    _configure_generate_tests_parser(
        sub.add_parser("generate-tests", help="Write test actions for an OpenAPI document"))
    configure_load_parser(sub.add_parser("load", help="Convert or run requests as a LoadDensity load test"))
    configure_trend_parser(sub.add_parser("trend", help="Per-endpoint latency history and anomaly checks"))
    configure_spec_parser(sub.add_parser("spec", help="Check the OpenAPI document against the tests"))
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
