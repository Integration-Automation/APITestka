"""
``apitestka load``: turn APITestka requests into a LoadDensity load test.

    apitestka load convert --actions smoke.json -o load.json --users 20 --time 30
    apitestka load run --actions smoke.json --users 20 --time 30 --max-failure-rate 0.01 --max-p95-ms 500

``run`` needs ``je_load_density`` installed for the interpreter it uses (``--python``, default the
current one), prints the LoadDensity summary and exits with 1 when the run fails or breaks a threshold.
"""
from __future__ import annotations

import argparse
import json

from je_api_testka.cli.cli_common import EXIT_FAILED, EXIT_OK, EXIT_USAGE
from je_api_testka.integrations.load_density import (
    DEFAULT_LOAD_USER,
    LOAD_USERS,
    TASK_MODES,
    LoadProfile,
    build_load_test,
)
from je_api_testka.integrations.load_density_commands import load_plan, write_load_test
from je_api_testka.integrations.load_density_runner import LoadThresholds, run_load_test
from je_api_testka.utils.exception.exceptions import APITesterException
from je_api_testka.utils.logging.loggin_instance import apitestka_logger


def _profile(args: argparse.Namespace) -> dict:
    return {"user": args.user, "user_count": args.users, "spawn_rate": args.spawn_rate,
            "test_time": args.time, "mode": args.mode}


def _has_source(args: argparse.Namespace, action: str) -> bool:
    if args.actions or args.report:
        return True
    apitestka_logger.error(f"cli load {action}: give --actions or at least one --report")
    return False


def _cmd_convert(args: argparse.Namespace) -> int:
    if not _has_source(args, "convert"):
        return EXIT_USAGE
    try:
        print(write_load_test(args.output, args.actions, args.report, _profile(args)))
    except APITesterException as error:
        apitestka_logger.error(f"cli load convert: {error}")
        return EXIT_FAILED
    return EXIT_OK


def _cmd_run(args: argparse.Namespace) -> int:
    if not _has_source(args, "run"):
        return EXIT_USAGE
    thresholds = LoadThresholds(args.max_failure_rate, args.max_p95_ms, args.min_requests)
    try:
        load_test = build_load_test(load_plan(args.actions, args.report).tasks, LoadProfile(**_profile(args)))
        result = run_load_test(load_test, thresholds, python=args.python, work_dir=args.work_dir)
    except APITesterException as error:
        apitestka_logger.error(f"cli load run: {error}")
        return EXIT_FAILED
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(json.dumps(result.summary.get("totals", {}), ensure_ascii=False))
        print(json.dumps(result.summary.get("latency_overall", {}), ensure_ascii=False))
        for problem in result.problems:
            print(f"FAIL: {problem}")
    return EXIT_OK if result.ok else EXIT_FAILED


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--actions", metavar="FILE", help="APITestka action JSON file with the requests")
    parser.add_argument("--report", action="append", default=[], metavar="FILE",
                        help="Saved JSON success report to replay instead; repeatable")
    parser.add_argument("--user", choices=LOAD_USERS, default=DEFAULT_LOAD_USER, help="LoadDensity user type")
    parser.add_argument("--users", type=int, default=10, help="Concurrent users")
    parser.add_argument("--spawn-rate", type=int, default=5, help="Users started per second")
    parser.add_argument("--time", type=int, default=60, help="Test duration in seconds")
    parser.add_argument("--mode", choices=TASK_MODES, default="sequence", help="How each user walks the tasks")


def configure_load_parser(load_parser: argparse.ArgumentParser) -> None:
    """Add the ``convert`` and ``run`` actions to the ``load`` subcommand."""
    actions = load_parser.add_subparsers(dest="load_command", required=True)

    convert = actions.add_parser("convert", help="Write LoadDensity action JSON for the requests")
    _add_common(convert)
    convert.add_argument("-o", "--output", required=True, help="LoadDensity action file to write")
    convert.set_defaults(func=_cmd_convert)

    run = actions.add_parser("run", help="Run the requests as a LoadDensity load test")
    _add_common(run)
    run.add_argument("--max-failure-rate", type=float, help="Largest allowed failure rate, 0 to 1")
    run.add_argument("--max-p95-ms", type=float, help="Largest allowed p95 latency in milliseconds")
    run.add_argument("--min-requests", type=int, default=1, help="Fewest requests that must run")
    run.add_argument("--python", help="Interpreter with je_load_density installed (default: this one)")
    run.add_argument("--work-dir", help="Folder for the action file and the summary (default: a temporary one)")
    run.add_argument("--json", action="store_true", help="Print the whole result as JSON")
    run.set_defaults(func=_cmd_run)
