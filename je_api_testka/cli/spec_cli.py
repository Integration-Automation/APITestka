"""
``apitestka spec check``: the test-as-spec loop from the command line.

    apitestka spec check openapi.json --run tests/ --min-coverage 0.8 \\
        --missing-actions tests/generated.json --inferred-spec build/openapi.inferred.json

Runs the tests (``--run``) and/or reads saved reports (``--report``), checks every recorded request
against the committed document, reports coverage, and exits with 1 on an undocumented operation, a
drift problem or coverage below ``--min-coverage``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from je_api_testka.cli.cli_common import EXIT_FAILED, EXIT_OK, EXIT_USAGE, run_action_path
from je_api_testka.contract.commands import read_openapi
from je_api_testka.spec.openapi_export import collect_records
from je_api_testka.spec.spec_loop import (
    check_records_against_spec,
    infer_spec_from_tests,
    missing_test_actions,
    write_json_document,
)
from je_api_testka.utils.exception.exceptions import APIContractException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _cmd_check(args: argparse.Namespace) -> int:
    if not args.report and not args.run:
        apitestka_logger.error("cli spec check: give at least one --run or --report")
        return EXIT_USAGE
    try:
        spec = read_openapi(args.spec)
    except APIContractException as error:
        apitestka_logger.error(f"cli spec check: {error}")
        return EXIT_USAGE
    for path in args.run:
        status = run_action_path(Path(path))
        if status:
            return status
    records = collect_records(args.report)
    report = check_records_against_spec(records, spec)
    if args.missing_actions:
        write_json_document(args.missing_actions, missing_test_actions(spec, report))
    if args.inferred_spec:
        write_json_document(args.inferred_spec, infer_spec_from_tests(records, spec))
    if args.json:
        print(json.dumps(report.to_dict(args.min_coverage), indent=2, ensure_ascii=False))
    else:
        print(report.render_text(args.min_coverage))
    return EXIT_FAILED if report.failures(args.min_coverage) else EXIT_OK


def configure_spec_parser(spec_parser: argparse.ArgumentParser) -> None:
    """Add the ``check`` action to the ``spec`` subcommand."""
    actions = spec_parser.add_subparsers(dest="spec_command", required=True)
    check = actions.add_parser("check", help="Check the committed OpenAPI document against the tests")
    check.add_argument("spec", help="Committed OpenAPI document (JSON)")
    check.add_argument("--run", action="append", default=[], metavar="PATH",
                       help="Action JSON file or directory to execute; repeatable")
    check.add_argument("--report", action="append", default=[], metavar="FILE",
                       help="Saved JSON success report to include; repeatable")
    check.add_argument("--min-coverage", type=float, default=0.0,
                       help="Fail below this share of documented operations exercised (0 to 1)")
    check.add_argument("--missing-actions", metavar="FILE", help="Write actions for the untested operations here")
    check.add_argument("--inferred-spec", metavar="FILE", help="Write the document the tests describe here")
    check.add_argument("--json", action="store_true", help="Print the report as JSON")
    check.set_defaults(func=_cmd_check)
