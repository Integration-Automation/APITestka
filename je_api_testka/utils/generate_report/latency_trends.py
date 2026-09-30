"""
Per-endpoint response-time history and anomaly detection.

Each run adds one row per endpoint to ``trend_endpoint_samples`` in the trend
database (the same SQLite file as :mod:`trend_store`): sample count and the
mean, p50, p95 and max latency in milliseconds. An endpoint is the method plus
the path template: the OpenAPI template the path matches when templates are
given, otherwise the path with identifier-like segments generalized
(``/items/42`` → ``/items/{id}``).

:func:`detect_latency_anomalies` judges every endpoint of the latest run
against a robust baseline of its previous runs: the median and the median
absolute deviation (MAD) of the chosen metric. The latest value is an anomaly
when it is at least ``min_increase`` (relative) and ``min_delta_ms`` (absolute)
above the median, and its robust z-score ``0.6745 * (value - median) / MAD`` is
above ``threshold``; a history with no spread (MAD 0) needs only the increase.
Only slowdowns are flagged.
"""
from __future__ import annotations

import sqlite3
import statistics
import uuid
from contextlib import closing
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Union
from urllib.parse import urlparse

from je_api_testka.diff.sla_check import percentile, record_latency_ms
from je_api_testka.spec.openapi_export import collect_records
from je_api_testka.spec.path_templates import generalize_path, match_path_template
from je_api_testka.utils.exception.exceptions import APIAssertException, APITesterException
from je_api_testka.utils.generate_report.trend_store import DEFAULT_TREND_DB

METRICS = ("mean_ms", "p50_ms", "p95_ms", "max_ms")
STATUS_ANOMALY: str = "anomaly"
STATUS_OK: str = "ok"
STATUS_INSUFFICIENT: str = "insufficient_history"
_MAD_TO_Z: float = 0.6745
ENDPOINT_SCHEMA_SQL: str = """
CREATE TABLE IF NOT EXISTS trend_endpoint_samples (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL,
    run_label TEXT NOT NULL,
    captured_at TEXT NOT NULL,
    endpoint TEXT NOT NULL,
    sample_count INTEGER NOT NULL,
    mean_ms REAL NOT NULL,
    p50_ms REAL NOT NULL,
    p95_ms REAL NOT NULL,
    max_ms REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS trend_endpoint_samples_endpoint ON trend_endpoint_samples (endpoint, id);
"""


@dataclass
class EndpointStats:
    """Latency statistics of one endpoint in one run."""

    endpoint: str
    sample_count: int
    mean_ms: float
    p50_ms: float
    p95_ms: float
    max_ms: float


@dataclass
class AnomalyPolicy:
    """How the latest run is judged against its history."""

    metric: str = "p95_ms"
    window: int = 20
    min_history: int = 5
    threshold: float = 3.5
    min_increase: float = 0.2
    min_delta_ms: float = 5.0

    def __post_init__(self) -> None:
        if self.metric not in METRICS:
            raise APITesterException(f"metric must be one of {METRICS}, not {self.metric!r}")
        if self.window < 1 or self.min_history < 1 or self.min_history > self.window:
            raise APITesterException("need 1 <= min_history <= window")


@dataclass
class EndpointVerdict:
    """The latest value of one endpoint compared with its baseline."""

    endpoint: str
    metric: str
    latest: float
    baseline_median: Optional[float]
    robust_z: Optional[float]
    history: int
    status: str

    def to_dict(self) -> dict:
        """JSON-ready form."""
        return asdict(self)


def endpoint_key(record: Mapping[str, object], templates: Iterable[str] = ()) -> Optional[str]:
    """Return ``"METHOD /path/template"`` for a record, or ``None`` when it has no URL."""
    url = record.get("request_url")
    if not url:
        return None
    path = urlparse(str(url)).path or "/"
    template = match_path_template(path, list(templates)) or generalize_path(path)
    return f"{str(record.get('request_method') or 'GET').upper()} {template}"


def endpoint_stats(records: Iterable[Mapping[str, object]], templates: Iterable[str] = ()) -> List[EndpointStats]:
    """Group records by endpoint and summarize their latencies; records without a timing are ignored."""
    template_list = list(templates)
    grouped: Dict[str, List[float]] = {}
    for record in records:
        key = endpoint_key(record, template_list)
        latency = record_latency_ms(record)
        if key is not None and latency is not None:
            grouped.setdefault(key, []).append(latency)
    return [EndpointStats(key, len(values), statistics.fmean(values), percentile(values, 50),
                          percentile(values, 95), max(values))
            for key, values in sorted(grouped.items())]


def _connect(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(Path(db_path))
    connection.executescript(ENDPOINT_SCHEMA_SQL)
    return connection


def record_endpoint_latencies(db_path: str = DEFAULT_TREND_DB, run_label: str = "",
                              report_paths: Optional[Sequence[str]] = None,
                              templates: Iterable[str] = ()) -> dict:
    """
    Store this run's per-endpoint latencies (current test record plus saved reports).

    :return: ``{"run_id", "run_label", "endpoints"}``, the number of endpoints stored.
    """
    stats = endpoint_stats(collect_records(report_paths), templates)
    run_id = uuid.uuid4().hex
    captured_at = datetime.now(timezone.utc).isoformat()
    with closing(_connect(db_path)) as connection, connection:
        connection.executemany(
            "INSERT INTO trend_endpoint_samples (run_id, run_label, captured_at, endpoint, sample_count,"
            " mean_ms, p50_ms, p95_ms, max_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [(run_id, run_label, captured_at, item.endpoint, item.sample_count, item.mean_ms, item.p50_ms,
              item.p95_ms, item.max_ms) for item in stats],
        )
    return {"run_id": run_id, "run_label": run_label, "endpoints": len(stats)}


def endpoint_history(db_path: str = DEFAULT_TREND_DB) -> Dict[str, List[dict]]:
    """Return every endpoint's samples, oldest first, as dicts with the run fields and metrics."""
    if not Path(db_path).exists():
        return {}
    with closing(_connect(db_path)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute("SELECT * FROM trend_endpoint_samples ORDER BY id").fetchall()
    history: Dict[str, List[dict]] = {}
    for row in rows:
        history.setdefault(row["endpoint"], []).append(dict(row))
    return history


def _latest_run_id(history: Mapping[str, List[dict]]) -> Optional[str]:
    newest = max((samples[-1] for samples in history.values()), key=lambda sample: sample["id"], default=None)
    return None if newest is None else newest["run_id"]


def judge(endpoint: str, values: Sequence[float], policy: AnomalyPolicy) -> EndpointVerdict:
    """Judge the last of ``values`` against the ``policy.window`` values before it."""
    latest = values[-1]
    baseline = list(values[-1 - policy.window:-1])
    if len(baseline) < policy.min_history:
        return EndpointVerdict(endpoint, policy.metric, latest, None, None, len(baseline), STATUS_INSUFFICIENT)
    median = statistics.median(baseline)
    mad = statistics.median(abs(value - median) for value in baseline)
    robust_z = None if mad == 0 else _MAD_TO_Z * (latest - median) / mad
    slower = latest >= median * (1 + policy.min_increase) and latest - median >= policy.min_delta_ms
    anomaly = slower and (robust_z is None or robust_z > policy.threshold)
    return EndpointVerdict(endpoint, policy.metric, latest, median, robust_z, len(baseline),
                           STATUS_ANOMALY if anomaly else STATUS_OK)


def anomaly_policy(policy: Union[AnomalyPolicy, Mapping[str, object], None] = None) -> AnomalyPolicy:
    """Return ``policy`` as an :class:`AnomalyPolicy` (a mapping is the JSON action form; ``None`` the defaults)."""
    if isinstance(policy, AnomalyPolicy):
        return policy
    try:
        return AnomalyPolicy(**dict(policy or {}))
    except TypeError as error:
        raise APITesterException(f"bad anomaly policy {policy!r}: {error}") from error


def detect_latency_anomalies(db_path: str = DEFAULT_TREND_DB,
                             policy: Union[AnomalyPolicy, Mapping[str, object], None] = None) -> List[EndpointVerdict]:
    """Judge every endpoint of the latest run; endpoints missing from that run are not judged."""
    rules = anomaly_policy(policy)
    history = endpoint_history(db_path)
    latest_run = _latest_run_id(history)
    return [judge(endpoint, [float(sample[rules.metric]) for sample in samples], rules)
            for endpoint, samples in sorted(history.items()) if samples[-1]["run_id"] == latest_run]


def assert_no_latency_anomalies(db_path: str = DEFAULT_TREND_DB,
                                policy: Union[AnomalyPolicy, Mapping[str, object], None] = None) -> List[dict]:
    """
    Return the verdicts as dicts.

    :raises APIAssertException: naming each endpoint whose latest run is an anomaly.
    """
    verdicts = detect_latency_anomalies(db_path, policy)
    anomalies = [verdict for verdict in verdicts if verdict.status == STATUS_ANOMALY]
    if anomalies:
        raise APIAssertException("latency anomalies: " + "; ".join(
            f"{item.endpoint} {item.metric} {item.latest:.1f} ms vs median {item.baseline_median:.1f} ms"
            for item in anomalies))
    return [verdict.to_dict() for verdict in verdicts]
