"""
``apitestka contract``: Pact-style consumer contracts from the command line.

    apitestka contract record --report run_success.json --consumer web --provider shop -o pacts/web-shop.json
    apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000
    apitestka contract compare pacts/web-shop.json openapi.json

``verify`` and ``compare`` print a report and exit with 1 when the contract does not hold.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Union

from je_api_testka.cli.cli_common import EXIT_FAILED, EXIT_OK, EXIT_USAGE, run_action_path
from je_api_testka.contract.commands import read_openapi, write_contract
from je_api_testka.contract.openapi_compat import CompatibilityReport, check_pact_against_openapi
from je_api_testka.contract.pact import BODY_RULE_EQUALITY, BODY_RULE_TYPE, read_pact
from je_api_testka.contract.verifier import (
    DEFAULT_VERIFY_TIMEOUT_SECONDS,
    ProviderTarget,
    VerificationReport,
    verify_pact,
)
from je_api_testka.utils.exception.exceptions import APIContractException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _print_report(report: Union[VerificationReport, CompatibilityReport], as_json: bool) -> int:
    print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False) if as_json else report.render_text())
    return EXIT_OK if report.ok else EXIT_FAILED


def _cmd_record(args: argparse.Namespace) -> int:
    if not args.report and not args.run:
        apitestka_logger.error("cli contract record: give at least one --report or --run")
        return EXIT_USAGE
    for path in args.run:
        status = run_action_path(Path(path))
        if status:
            return status
    try:
        written = write_contract(args.output, args.consumer, args.provider, args.report,
                                 base_path=args.base_path, body_rule=args.body_rule)
    except APIContractException as error:
        apitestka_logger.error(f"cli contract record: {error}")
        return EXIT_FAILED
    print(written)
    return EXIT_OK


def _cmd_verify(args: argparse.Namespace) -> int:
    try:
        pact = read_pact(args.contract)
    except APIContractException as error:
        apitestka_logger.error(f"cli contract verify: {error}")
        return EXIT_USAGE
    target = ProviderTarget(args.base_url, provider_states_url=args.provider_states_url, timeout=args.timeout)
    return _print_report(verify_pact(pact, target), args.json)


def _cmd_compare(args: argparse.Namespace) -> int:
    try:
        pact = read_pact(args.contract)
        spec = read_openapi(args.openapi)
    except APIContractException as error:
        apitestka_logger.error(f"cli contract compare: {error}")
        return EXIT_USAGE
    return _print_report(check_pact_against_openapi(pact, spec), args.json)


def _add_record_parser(actions) -> None:
    record = actions.add_parser("record", help="Record a consumer contract from test records")
    record.add_argument("--report", action="append", default=[], metavar="FILE",
                        help="Saved JSON success report (<name>_success.json); repeatable")
    record.add_argument("--run", action="append", default=[], metavar="PATH",
                        help="Action JSON file or directory to execute first; repeatable")
    record.add_argument("--consumer", required=True)
    record.add_argument("--provider", required=True)
    record.add_argument("--base-path", default="", help="Prefix to drop from request paths, e.g. /api/v1")
    record.add_argument("--body-rule", choices=(BODY_RULE_TYPE, BODY_RULE_EQUALITY), default=BODY_RULE_TYPE,
                        help="Match response bodies by type (default) or by exact value")
    record.add_argument("-o", "--output", required=True, help="Contract file to write")
    record.set_defaults(func=_cmd_record)


def configure_contract_parser(contract_parser: argparse.ArgumentParser) -> None:
    """Add the ``record``, ``verify`` and ``compare`` actions to the ``contract`` subcommand."""
    actions = contract_parser.add_subparsers(dest="contract_command", required=True)
    _add_record_parser(actions)

    verify = actions.add_parser("verify", help="Replay a contract against a running provider")
    verify.add_argument("contract", help="Contract file")
    verify.add_argument("--base-url", required=True, help="Provider base URL")
    verify.add_argument("--provider-states-url", help="URL that receives provider-state setup POSTs")
    verify.add_argument("--timeout", type=float, default=DEFAULT_VERIFY_TIMEOUT_SECONDS)
    verify.add_argument("--json", action="store_true", help="Print the report as JSON")
    verify.set_defaults(func=_cmd_verify)

    compare = actions.add_parser("compare", help="Check a contract against the provider's OpenAPI document")
    compare.add_argument("contract", help="Contract file")
    compare.add_argument("openapi", help="Provider OpenAPI document (JSON)")
    compare.add_argument("--json", action="store_true", help="Print the report as JSON")
    compare.set_defaults(func=_cmd_compare)
