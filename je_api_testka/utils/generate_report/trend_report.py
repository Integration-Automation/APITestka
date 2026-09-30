"""
HTML report of per-endpoint latency trends.

One row per endpoint of the latest run: the metric's latest value, the baseline
median, the robust z-score, the verdict, and an inline SVG sparkline of the
last ``limit_runs`` values (the latest point is red when it is an anomaly).
Endpoint names come from requested URLs, so every value is HTML-escaped.
"""
from __future__ import annotations

import html
from pathlib import Path
from typing import List, Mapping, Optional, Sequence, Union

from je_api_testka.utils.generate_report.latency_trends import (
    STATUS_ANOMALY,
    AnomalyPolicy,
    EndpointVerdict,
    anomaly_policy,
    detect_latency_anomalies,
    endpoint_history,
)
from je_api_testka.utils.generate_report.trend_store import DEFAULT_TREND_DB

DEFAULT_TREND_REPORT: str = "apitestka_trend_report.html"
_SPARK_WIDTH: int = 160
_SPARK_HEIGHT: int = 32
LINE_COLOUR: str = "#0969da"
ANOMALY_COLOUR: str = "#cf222e"
_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>APITestka latency trends</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1f2328; background: #ffffff; }}
table {{ border-collapse: collapse; }}
th, td {{ border-bottom: 1px solid #d0d7de; padding: 6px 10px; text-align: left; }}
td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.anomaly {{ color: #cf222e; font-weight: 600; }}
.insufficient_history {{ color: #6e7781; }}
polyline {{ fill: none; stroke: #0969da; stroke-width: 1.5; }}
</style></head><body>
<h1>Latency trends</h1>
<p>Metric: {metric}. Baseline: median of up to {window} previous runs; anomaly when at least
{increase:.0%} and {delta:g} ms slower and the robust z-score is above {threshold:g}.</p>
<table><thead><tr><th>Endpoint</th><th>Latest (ms)</th><th>Baseline (ms)</th><th>z</th><th>Runs</th>
<th>Status</th><th>Trend</th></tr></thead><tbody>
{rows}
</tbody></table></body></html>
"""


def sparkline(values: Sequence[float], last_colour: str = LINE_COLOUR) -> str:
    """Return an inline SVG polyline for ``values`` with the last point in ``last_colour`` ("" for no values)."""
    if not values:
        return ""
    low, high = min(values), max(values)
    span = (high - low) or 1.0
    step = _SPARK_WIDTH / max(len(values) - 1, 1)
    points = [(index * step, _SPARK_HEIGHT - 2 - (value - low) / span * (_SPARK_HEIGHT - 4))
              for index, value in enumerate(values)]
    last_x, last_y = points[-1]
    return (f'<svg width="{_SPARK_WIDTH}" height="{_SPARK_HEIGHT}" role="img" aria-label="trend">'
            f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}"/>'
            f'<circle cx="{last_x:.1f}" cy="{last_y:.1f}" r="2.5" fill="{html.escape(last_colour)}"/></svg>')


def _number(value: Optional[float]) -> str:
    return "" if value is None else f"{value:.1f}"


def _row(verdict: EndpointVerdict, values: Sequence[float]) -> str:
    status = html.escape(verdict.status)
    return (f"<tr><td>{html.escape(verdict.endpoint)}</td><td class=\"num\">{_number(verdict.latest)}</td>"
            f"<td class=\"num\">{_number(verdict.baseline_median)}</td>"
            f"<td class=\"num\">{_number(verdict.robust_z)}</td><td class=\"num\">{verdict.history + 1}</td>"
            f"<td class=\"{status}\">{status}</td>"
            f"<td>{sparkline(values, ANOMALY_COLOUR if verdict.status == STATUS_ANOMALY else LINE_COLOUR)}</td></tr>")


def render_trend_report(db_path: str = DEFAULT_TREND_DB,
                        policy: Union[AnomalyPolicy, Mapping[str, object], None] = None,
                        limit_runs: int = 30) -> str:
    """Return the trend report as an HTML string."""
    rules = anomaly_policy(policy)
    history = endpoint_history(db_path)
    rows: List[str] = []
    for verdict in detect_latency_anomalies(db_path, rules):
        values = [float(sample[rules.metric]) for sample in history[verdict.endpoint]][-limit_runs:]
        rows.append(_row(verdict, values))
    return _PAGE.format(metric=html.escape(rules.metric), window=rules.window, increase=rules.min_increase,
                        delta=rules.min_delta_ms, threshold=rules.threshold,
                        rows="\n".join(rows) or '<tr><td colspan="7">No runs recorded yet.</td></tr>')


def generate_trend_report(output_path: str = DEFAULT_TREND_REPORT, db_path: str = DEFAULT_TREND_DB,
                          policy: Union[AnomalyPolicy, Mapping[str, object], None] = None,
                          limit_runs: int = 30) -> str:
    """Write :func:`render_trend_report` to ``output_path`` as UTF-8 and return the path."""
    Path(output_path).write_text(render_trend_report(db_path, policy, limit_runs), encoding="utf-8")
    return str(output_path)
