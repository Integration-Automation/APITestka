"""
Turn APITestka requests into a LoadDensity load test.

LoadDensity (``je_load_density``, a sibling project on Locust) runs load tests
from its own action JSON. This module converts APITestka request actions
(``AT_test_api_method`` / ``AT_test_api_method_httpx``) or recorded traffic
into LoadDensity HTTP tasks and wraps them in an ``LD_start_test`` action:

* ``http_method`` / ``test_url`` become ``method`` / ``request_url``;
* ``params``, ``headers``, ``cookies``, ``json``, ``data``, ``timeout``,
  ``allow_redirects`` and ``verify`` are copied as they are (LoadDensity passes
  the same names to its HTTP client);
* ``result_check_dict["status_code"]`` becomes a ``status_code`` assertion;
* every other action, and any request whose URL is not absolute ``http(s)``
  (LoadDensity's HTTP users have no base host), is left out and reported in
  :attr:`LoadPlan.skipped`.

Running the result is :mod:`je_api_testka.integrations.load_density_runner`'s job.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Mapping, Sequence, Union
from urllib.parse import urlparse

from je_api_testka.spec.records_to_openapi import decode_body
from je_api_testka.utils.exception.exceptions import APITesterException

REQUEST_COMMANDS = ("AT_test_api_method", "AT_test_api_method_httpx")
COPIED_KEYS = ("params", "headers", "cookies", "json", "data", "timeout", "allow_redirects", "verify")
LOAD_DENSITY_KEY: str = "load_density"
DEFAULT_LOAD_USER: str = "fast_http_user"
LOAD_USERS = ("fast_http_user", "http_user")
TASK_MODES = ("sequence", "weighted")  # LoadDensity runs any other mode as a sequence


@dataclass
class LoadProfile:
    """How hard and how long LoadDensity drives the tasks."""

    user: str = DEFAULT_LOAD_USER
    user_count: int = 10
    spawn_rate: int = 5
    test_time: int = 60
    mode: str = "sequence"

    def __post_init__(self) -> None:
        if self.user not in LOAD_USERS:
            raise APITesterException(f"load user must be one of {LOAD_USERS}, not {self.user!r}")
        if self.mode not in TASK_MODES:
            raise APITesterException(f"task mode must be one of {TASK_MODES}, not {self.mode!r}")
        if min(self.user_count, self.spawn_rate, self.test_time) < 1:
            raise APITesterException("user_count, spawn_rate and test_time must be at least 1")


@dataclass
class LoadPlan:
    """LoadDensity tasks plus the actions that could not become one."""

    tasks: List[dict] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)


def _task_name(method: str, url: str) -> str:
    return f"{method.upper()} {urlparse(url).path or '/'}"


def _task_from_kwargs(kwargs: Mapping[str, object]) -> dict:
    method = str(kwargs["http_method"]).lower()
    url = str(kwargs["test_url"])
    task: dict = {"method": method, "request_url": url, "name": _task_name(method, url)}
    task.update({key: kwargs[key] for key in COPIED_KEYS if kwargs.get(key) is not None})
    checks = kwargs.get("result_check_dict")
    if isinstance(checks, Mapping) and "status_code" in checks:
        task["assertions"] = [{"type": "status_code", "value": int(str(checks["status_code"]))}]
    return task


def _add_task(plan: LoadPlan, kwargs: Mapping[str, object]) -> None:
    if urlparse(str(kwargs["test_url"])).scheme not in ("http", "https"):
        plan.skipped.append(f"{kwargs['test_url']}: LoadDensity needs an absolute http(s) URL")
        return
    plan.tasks.append(_task_from_kwargs(kwargs))


def _action_list(actions: Union[Sequence[object], Mapping[str, object]]) -> Sequence[object]:
    if isinstance(actions, Mapping):
        return actions.get("api_testka") or []
    return actions


def actions_to_load_plan(actions: Union[Sequence[object], Mapping[str, object]]) -> LoadPlan:
    """Convert an APITestka action list (or ``{"api_testka": [...]}``) into LoadDensity tasks."""
    plan = LoadPlan()
    for action in _action_list(actions):
        if not isinstance(action, list) or not action:
            plan.skipped.append(f"not an action: {action!r}")
            continue
        kwargs = action[1] if len(action) > 1 else None
        if action[0] not in REQUEST_COMMANDS:
            plan.skipped.append(f"{action[0]}: not a request")
        elif not isinstance(kwargs, Mapping) or "http_method" not in kwargs or "test_url" not in kwargs:
            plan.skipped.append(f"{action[0]}: needs keyword arguments with http_method and test_url")
        else:
            _add_task(plan, kwargs)
    return plan


def records_to_load_plan(records: Iterable[Mapping[str, object]]) -> LoadPlan:
    """Convert recorded requests (test records or saved JSON reports) into LoadDensity tasks."""
    plan = LoadPlan()
    for record in records:
        if not record.get("request_url"):
            plan.skipped.append("record without request_url")
            continue
        kwargs: dict = {"http_method": record.get("request_method") or "GET", "test_url": record["request_url"],
                        "result_check_dict": {"status_code": record.get("status_code", 200)}}
        body = decode_body(record.get("request_body"))
        if body is not None:
            kwargs["json" if body[0] == "application/json" else "data"] = body[1]
        _add_task(plan, kwargs)
    return plan


def build_load_test(tasks: Sequence[Mapping[str, object]], profile: LoadProfile) -> dict:
    """
    Return LoadDensity action JSON that runs ``tasks`` under ``profile``.

    :raises APITesterException: when there is no task to run.
    """
    if not tasks:
        raise APITesterException("no request to load test")
    return {LOAD_DENSITY_KEY: [["LD_start_test", {
        "user_detail_dict": {"user": profile.user},
        "tasks": {"mode": profile.mode, "tasks": [dict(task) for task in tasks]},
        "user_count": profile.user_count,
        "spawn_rate": profile.spawn_rate,
        "test_time": profile.test_time,
    }]]}
