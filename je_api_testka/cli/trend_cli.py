"""
``apitestka trend``: per-endpoint response-time history and anomaly checks.

    apitestka trend record --report run_success.json --label build-128 [--openapi openapi.json]
    apitestka trend check [--metric p95_ms] [--threshold 3.5] [--json]
    apitestka trend report -o trends.html

``check`` exits with 1 when an endpoint of the latest run is an anomaly, so it can gate CI.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from je_api_testka.cli.cli_common import EXIT_FAILED, EXIT_OK, EXIT_USAGE, run_action_path
from je_api_testka.contract.commands import read_openapi
from je_api_testka.utils.exception.exceptions import APIContractException, APITesterException
from je_api_testka.utils.generate_report.latency_trends import (
    METRICS,
    STATUS_ANOMALY,
    AnomalyPolicy,
    detect_latency_anomalies,
    record_endpoint_latencies,
)
from je_api_testka.utils.generate_report.trend_report import DEFAULT_TREND_REPORT, generate_trend_report
from je_api_testka.utils.generate_report.trend_store import DEFAULT_TREND_DB
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _policy(args: argparse.Namespace) -> AnomalyPolicy:
    return AnomalyPolicy(metric=args.metric, window=args.window, min_history=args.min_history,
                         threshold=args.threshold, min_increase=args.min_increase, min_delta_ms=args.min_delta_ms)


def _cmd_record(args: argparse.Namespace) -> int:
    if not args.report and not args.run:
        apitestka_logger.error("cli trend record: give at least one --report or --run")
        return EXIT_USAGE
    for path in args.run:
        status = run_action_path(Path(path))
        if status:
            return status
    try:
        templates = list((read_openapi(args.openapi).get("paths") or {})) if args.openapi else []
    except APIContractException as error:
        apitestka_logger.error(f"cli trend record: {error}")
        return EXIT_USAGE
    print(json.dumps(record_endpoint_latencies(args.db, args.label, args.report, templates)))
    return EXIT_OK


def _cmd_check(args: argparse.Namespace) -> int:
    try:
        verdicts = detect_latency_anomalies(args.db, _policy(args))
    except APITesterException as error:
        apitestka_logger.error(f"cli trend check: {error}")
        return EXIT_USAGE
    if args.json:
        print(json.dumps([verdict.to_dict() for verdict in verdicts], indent=2, ensure_ascii=False))
    else:
        for verdict in verdicts:
            baseline = "-" if verdict.baseline_median is None else f"{verdict.baseline_median:.1f}"
            print(f"[{verdict.status}] {verdict.endpoint}: {verdict.latest:.1f} ms (baseline {baseline} ms)")
    return EXIT_FAILED if any(verdict.status == STATUS_ANOMALY for verdict in verdicts) else EXIT_OK


def _cmd_report(args: argparse.Namespace) -> int:
    try:
        print(generate_trend_report(args.output, args.db, _policy(args), args.limit_runs))
    except APITesterException as error:
        apitestka_logger.error(f"cli trend report: {error}")
        return EXIT_USAGE
    return EXIT_OK


def _add_policy(parser: argparse.ArgumentParser) -> None:
    defaults = AnomalyPolicy()
    parser.add_argument("--metric", choices=METRICS, default=defaults.metric)
    parser.add_argument("--window", type=int, default=defaults.window, help="Previous runs in the baseline")
    parser.add_argument("--min-history", type=int, default=defaults.min_history,
                        help="Previous runs needed before judging")
    parser.add_argument("--threshold", type=float, default=defaults.threshold, help="Robust z-score limit")
    parser.add_argument("--min-increase", type=float, default=defaults.min_increase,
                        help="Smallest relative slowdown that counts, e.g. 0.2 for 20%%")
    parser.add_argument("--min-delta-ms", type=float, default=defaults.min_delta_ms,
                        help="Smallest absolute slowdown that counts")


def configure_trend_parser(trend_parser: argparse.ArgumentParser) -> None:
    """Add the ``record``, ``check`` and ``report`` actions to the ``trend`` subcommand."""
    trend_parser.add_argument("--db", default=DEFAULT_TREND_DB, help="Trend SQLite database")
    actions = trend_parser.add_subparsers(dest="trend_command", required=True)

    record = actions.add_parser("record", help="Store this run's per-endpoint latencies")
    record.add_argument("--report", action="append", default=[], metavar="FILE",
                        help="Saved JSON success report; repeatable")
    record.add_argument("--run", action="append", default=[], metavar="PATH",
                        help="Action JSON file or directory to execute first; repeatable")
    record.add_argument("--label", default="", help="Run label, e.g. a build number or commit")
    record.add_argument("--openapi", help="OpenAPI document whose path templates name the endpoints")
    record.set_defaults(func=_cmd_record)

    check = actions.add_parser("check", help="Judge the latest run; exit 1 on an anomaly")
    _add_policy(check)
    check.add_argument("--json", action="store_true", help="Print the verdicts as JSON")
    check.set_defaults(func=_cmd_check)

    report = actions.add_parser("report", help="Write the HTML trend report")
    _add_policy(report)
    report.add_argument("-o", "--output", default=DEFAULT_TREND_REPORT)
    report.add_argument("--limit-runs", type=int, default=30, help="Runs shown in each sparkline")
    report.set_defaults(func=_cmd_report)
