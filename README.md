# APITestka

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](licenses/APITestka_LICENSE)
[![PyPI](https://img.shields.io/pypi/v/je_api_testka.svg)](https://pypi.org/project/je_api_testka/)
[![Documentation Status](https://readthedocs.org/projects/apitestka/badge/?version=latest)](https://apitestka.readthedocs.io/en/latest/?badge=latest)

**APITestka** is a lightweight, cross-platform Python framework for automated API testing.
It started as an HTTP/HTTPS / SOAP-XML / JSON request runner with reporting and a JSON-driven
executor, and now ships with a much wider toolkit — variable chaining, OpenAPI / Postman /
HAR / cURL importers, a record-replay proxy, security probes, parallel runners, an MCP
server for Claude, and more.

> **Translations / Other Languages:**
> [繁體中文](README/README_zh-TW.md) | [简体中文](README/README_zh-CN.md)

---

## Table of Contents

- [Highlights](#highlights)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Feature Map](#feature-map)
  - [HTTP / Protocol Backends](#http--protocol-backends)
  - [Data Layer](#data-layer)
  - [Assertions, Diffs and SLAs](#assertions-diffs-and-slas)
  - [Connection Layer](#connection-layer)
  - [Mock Server](#mock-server)
  - [Runner](#runner)
  - [Reports and Observability](#reports-and-observability)
  - [Integrations](#integrations)
  - [CLI / Developer Experience](#cli--developer-experience)
  - [Security Probes](#security-probes)
  - [OpenAPI Inference](#openapi-inference)
  - [Test-as-Spec Loop](#test-as-spec-loop)
  - [Contract Testing](#contract-testing)
  - [GUI](#gui)
  - [Pluggable AI Backend](#pluggable-ai-backend)
- [MCP Server for Claude](#mcp-server-for-claude)
- [Project Structure](#project-structure)
- [Optional Extras](#optional-extras)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Links](#links)

---

## Highlights

| Area | What you get |
|---|---|
| **Backends** | `requests` (sync, sessions), `httpx` (sync + async, HTTP/2), WebSocket, SSE, GraphQL |
| **Data layer** | Variable store, `{{var}}` templating, CSV/JSON data-driven loops, env profiles, fake data |
| **Assertions** | Field assertions, JSON Schema, JSONPath, snapshot, structural diffs, OpenAPI contract drift, response-time SLAs |
| **Connection** | mTLS, proxies, DNS override, VCR-style cassette record/replay |
| **Mock server** | Static, dynamic, stateful, fault injection, OpenAPI-driven, Jinja templating, webhook receiver, record-replay proxy, WebSocket and gRPC endpoints |
| **Runner** | Sequential & parallel execution, tag filters, dependency-aware ordering, retry policies |
| **Reports** | HTML / JSON / XML / **JUnit / Allure / Markdown** / shields.io badge / SQLite trend store / run diff / per-endpoint latency trends with anomaly detection |
| **Integrations** | Slack / Teams / Discord webhook, GitHub PR comment, cURL & HAR importers, OpenAPI / Postman importer, LoadDensity load-test bridge |
| **CLI / DX** | Subcommand CLI, REPL, terminal summary, shell completion, scaffold |
| **Security** | Auth helpers (Basic / Bearer / JWT / AWS SigV4), header / CORS / rate-limit / SSRF probes, pip-audit wrapper, fuzz inputs |
| **Spec inference** | Test record → OpenAPI, JSON Schema inference, OpenAPI changelog, test-as-spec loop (drift, coverage, generated tests for gaps) |
| **Contract testing** | Pact v2 consumer contracts from test runs, provider verification, bidirectional check against OpenAPI |
| **AI** | Pluggable backend with deterministic fallback for test generation, fake data, failure classification; Anthropic reference backend |
| **MCP** | First-class Claude Code / MCP server exposing the framework as tools |
| **GUI** | Optional PySide6 GUI (English / 繁中 / 简中 / 日本語) plus Swagger UI embed |
| **Cross-platform** | Windows, macOS, Linux. Python 3.10–3.14 |

---

## Installation

```bash
pip install je_api_testka
```

Optional extras (install with `pip install 'je_api_testka[<extra>]'`):

| Extra | Adds |
|---|---|
| `gui` | PySide6 GUI |
| `websocket` | `websockets` for the WebSocket wrapper |
| `schema` | `jsonschema` and `jsonpath-ng` for advanced assertions |
| `security` | `pyjwt` and `botocore` for JWT / AWS SigV4 helpers |
| `otel` | `opentelemetry-api` / `opentelemetry-sdk` for tracing hooks |
| `mcp` | `mcp` Python SDK for the MCP server |

---

## Quick Start

```python
from je_api_testka import test_api_method_requests, generate_html_report

test_api_method_requests(
    "get", "https://httpbin.org/get",
    result_check_dict={"status_code": 200},
)
generate_html_report("smoke")
```

JSON-driven equivalent (`smoke.json`):

```json
{
  "api_testka": [
    ["AT_test_api_method", {
      "http_method": "get",
      "test_url": "https://httpbin.org/get",
      "result_check_dict": {"status_code": 200}
    }],
    ["AT_generate_html_report", {"html_file_name": "smoke"}]
  ]
}
```

```bash
apitestka run smoke.json
```

---

## Core Concepts

- **Backends** — every HTTP call goes through `requests_wrapper`, `httpx_wrapper`,
  `websocket_wrapper`, `sse_wrapper`, or `graphql_wrapper`. They share a record format.
- **`test_record_instance`** — a thread-safe singleton that captures every request /
  response. Reports, diffs, badges, and the trend store all read from it.
- **Executor** — a command map (`AT_*` keys) over Python callables. JSON action lists
  drive it. New features register themselves here so `apitestka run` can use them
  without writing Python.
- **VariableStore** — a thread-safe key/value store. `{{var}}` placeholders inside
  payloads, URLs, headers, and templates resolve against it. Combine with
  `AT_extract_and_store` to chain requests.
- **Optional dependencies** — heavyweight features (WebSockets, JSON Schema, JWT, MCP)
  live behind extras and raise a friendly error if you call them without installing.

---

## Feature Map

### HTTP / Protocol Backends

| Backend | Function |
|---|---|
| `requests` | `test_api_method_requests` (sync, sessions) |
| `httpx` sync | `test_api_method_httpx` |
| `httpx` async | `test_api_method_httpx_async` (HTTP/2 via `http2=True`) |
| WebSocket | `test_api_method_websocket`, `test_api_method_websocket_async` (extra: `websocket`) |
| SSE | `iter_sse_events`, `test_api_method_sse` |
| GraphQL | `test_api_method_graphql`, `test_api_method_graphql_async` |

```python
from je_api_testka import test_api_method_graphql

test_api_method_graphql(
    "https://api.example.invalid/graphql",
    query="query Get($id: ID!) { user(id: $id) { id name } }",
    variables={"id": "42"},
)
```

### Data Layer

```python
from je_api_testka.data import (
    variable_store, render_template, load_env_profile,
    fake_uuid, iter_csv_rows,
)
from je_api_testka.data.variable_store import extract_and_store

load_env_profile("envs/dev.json")           # populates variable_store
extract_and_store({"data": {"id": 7}}, "data.id", "user_id")
render_template("/users/{{user_id}}")        # -> "/users/7"

for row in iter_csv_rows("data/users.csv"):
    variable_store.set("email", row["email"])
    test_api_method_requests("post", "https://x.invalid/login", json=row)
```

Executor commands: `AT_set_variable`, `AT_get_variable`, `AT_clear_variables`,
`AT_extract_and_store`, `AT_render_template`, `AT_fake_uuid`, `AT_fake_email`,
`AT_fake_word`, `AT_load_env_profile`.

### Assertions, Diffs and SLAs

```python
from je_api_testka import (
    check_json_schema, check_jsonpath, assert_snapshot,
    RetryPolicy, retry_call,
)
from je_api_testka.diff import diff_payloads, diff_openapi_specs
from je_api_testka.diff.sla_check import ResponseSLA, assert_sla

check_json_schema(payload, {"type": "object", "required": ["id"]})
check_jsonpath(payload, "$.data.id", expected=7)
assert_snapshot("user-by-id", payload, ignore_keys=["timestamp"])
diff = diff_payloads(prod_response, staging_response, ignore_paths=["server_time"])
assert_sla(records, ResponseSLA(max_ms=2000, p95_ms=1500))
assert_sla(sla={"max_ms": 2000})   # the run recorded so far; JSON: ["AT_assert_sla", {"sla": {...}}]
```

### Connection Layer

```python
from je_api_testka.connection import (
    ConnectionOptions, apply_to_requests_kwargs,
    dns_override, Cassette, replay_or_record,
)

options = ConnectionOptions(cert=("c.crt", "c.key"),
                            proxies={"https": "http://proxy:8080"})

with dns_override({"api.example.invalid": "127.0.0.1"}):
    test_api_method_requests("get", "https://api.example.invalid/health")

cassette = Cassette("tape.json")  # offline replay-or-record
```

### Mock Server

The bundled `FlaskMockServer` now supports several layered features:

| Feature | API |
|---|---|
| Static routes | `flask_mock_server_instance.add_router({...})` |
| Dynamic routes | `server.add_dynamic_route(...)` + `DynamicRouter` rules |
| Stateful store | `server.state` (`StatefulStore`) |
| Fault injection | `server.fault_injector.configure(latency_seconds=..., failure_probability=...)` |
| OpenAPI driven | `server.load_openapi(spec)` |
| Templated | `server.add_template_route("/x", {"msg": "{{name}}"})` |
| Webhook receive | `server.add_webhook("/hook")` then read `server.webhook_receiver.all()` |
| Record-replay | `server.add_proxy("https://upstream", "tape.json")` |

```bash
apitestka mock --host 0.0.0.0 --port 9000
apitestka mock --config mock.json       # HTTP routes plus WebSocket and gRPC endpoints
```

**WebSocket and gRPC endpoints.** `WebSocketMockServer` (`websocket` extra) serves scripted
routes: a greeting on connect, a reply map for known messages, and a fallback for the rest
(`{{message}}` echoes, `null` stays silent). `GrpcStubServer` (`grpc` extra) serves methods by
full path without compiled stubs: fixed unary responses, server streams, or a status-code
error. Payloads are raw bytes, so serialized protobuf works with generated clients; `str` is
sent as UTF-8 and other JSON values as compact JSON. Both keep what they received for
assertions, and an unknown WebSocket path is refused with HTTP 404.

```python
from je_api_testka.utils.mock_server.websocket_mock import WebSocketMockServer, WebSocketRoute
from je_api_testka.utils.mock_server.grpc_stub import GrpcStubServer

with WebSocketMockServer(port=0) as ws:          # port 0 picks a free port
    ws.add_route("/chat", WebSocketRoute(replies={"ping": "pong"}))
    ...                                          # connect to f"{ws.url}/chat"
    ws.received("/chat")                         # frames the route got

with GrpcStubServer(port=0) as grpc_mock:        # needs the grpc extra
    grpc_mock.add_unary_response("/shop.Catalog/Get", {"id": 1})
    ...                                          # grpc.insecure_channel(grpc_mock.address)
```

A `--config` file describes all three kinds; every section is optional:

```json
{
  "http": {"routes": [{"rule": "/health", "body": {"ok": true}}], "openapi": "spec.json"},
  "websocket": {"port": 8765, "routes": {"/chat": {"greeting": "hi", "replies": {"ping": "pong"}}}},
  "grpc": {"port": 50051, "methods": {
    "/shop.Catalog/Get": {"response": {"id": 1}},
    "/shop.Catalog/List": {"stream": [{"id": 1}, {"id": 2}]},
    "/shop.Catalog/Delete": {"error": {"code": "PERMISSION_DENIED", "details": "read only"}}
  }}
}
```

JSON actions reach the same mocks with `AT_mock_start_websocket_server` / `AT_mock_start_grpc_server`
(`routes` / `methods` in the config form above), `AT_mock_websocket_received` /
`AT_mock_grpc_received`, and `AT_mock_stop_websocket_server` / `AT_mock_stop_grpc_server`.

### Runner

```python
from je_api_testka.runner import (
    run_actions_parallel, filter_actions_by_tag, order_actions,
)

actions = order_actions(filter_actions_by_tag(actions, {"smoke"}))
results = run_actions_parallel(actions, max_workers=8)
```

### Reports and Observability

```python
from je_api_testka import (
    generate_html_report, generate_json_report, generate_xml_report,
)
from je_api_testka.utils.generate_report.junit_report import generate_junit_report
from je_api_testka.utils.generate_report.allure_report import generate_allure_report
from je_api_testka.utils.generate_report.markdown_report import generate_markdown_report
from je_api_testka.utils.generate_report.badge import generate_badge
from je_api_testka.utils.generate_report.run_diff import diff_runs
from je_api_testka.utils.generate_report.trend_store import record_current_run

generate_html_report("report")
generate_junit_report("junit.xml")          # GitHub Actions / Jenkins
generate_allure_report("allure-results")    # `allure generate` consumable
generate_markdown_report("report.md")       # Slack / GitHub-friendly
generate_badge("badge.json")                # shields.io endpoint
record_current_run("trend.sqlite")          # historical trend
```

**Response-time trends and anomalies.** `record_endpoint_latencies` stores each run's per-endpoint
latency (count, mean, p50, p95, max) in the trend database. An endpoint is the method plus the path
template: the OpenAPI template when one is given, otherwise the path with identifiers generalized
(`/items/42` → `/items/{id}`). `detect_latency_anomalies` compares every endpoint of the latest run with
the median and MAD of its previous runs (20 by default, at least 5). It flags a slowdown of at least 20 %
and 5 ms whose robust z-score is above 3.5; all of these are settings. `generate_trend_report` writes an
HTML table with a sparkline per endpoint. JSON actions: `AT_record_endpoint_latencies`,
`AT_detect_latency_anomalies`, `AT_assert_no_latency_anomalies`, `AT_generate_trend_report`.

```python
from je_api_testka.utils.generate_report.latency_trends import (
    record_endpoint_latencies, detect_latency_anomalies, assert_no_latency_anomalies,
)
from je_api_testka.utils.generate_report.trend_report import generate_trend_report

record_endpoint_latencies("trend.sqlite", run_label="build-128")   # after each run
assert_no_latency_anomalies("trend.sqlite", {"metric": "p95_ms", "threshold": 3.5})
generate_trend_report("trends.html", "trend.sqlite")
```

```bash
apitestka trend record --report run_success.json --label build-128 --openapi openapi.json
apitestka trend check            # exit 1 on an anomaly
apitestka trend report -o trends.html
```

OpenTelemetry hook (no-op when `opentelemetry-api` is absent):

```python
from je_api_testka.utils.observability import instrument_request

with instrument_request("GET", "https://x.invalid"):
    test_api_method_requests("get", "https://x.invalid")
```

### Integrations

```python
from je_api_testka.integrations import (
    notify_via_webhook, post_pr_comment,
    curl_to_action, convert_har,
)
from je_api_testka.cli.import_specs import convert_spec_file

notify_via_webhook("https://hooks.slack.invalid/...", summary="...", platform="slack")
post_pr_comment("acme/widget", pr_number=42, token="<gha-token>")

action = curl_to_action("curl -X POST https://api/x -d '{\"a\":1}'")
actions = convert_har("traffic.har")
actions = convert_spec_file("openapi.json", spec_format="openapi")
```

Each importer returns `["AT_test_api_method", {...}]` actions that `execute_action` runs
as they are. Runner metadata (`id`, `depends_on`, `tags`) may stay in the kwargs; the
executor strips it before the call.

**Load testing with LoadDensity.** The same requests can run as a load test on
[LoadDensity](https://github.com/Integration-Automation/LoadDensity) (Locust). `AT_test_api_method` and
`AT_test_api_method_httpx` actions, or recorded traffic from saved reports, become LoadDensity HTTP tasks:
URL, method, `params`, `headers`, `cookies`, `json`, `data`, `timeout`, `allow_redirects` and `verify` carry
over, and `result_check_dict["status_code"]` becomes a status assertion. Other actions, and relative URLs,
are left out and listed. `load run` starts LoadDensity in its own process
(`python -m je_load_density --execute_file`) and judges the run from its summary: no requests, a
failure rate above `--max-failure-rate` or a p95 above `--max-p95-ms` exits with 1.

```bash
pip install je_load_density            # in this interpreter, or point --python at another one
apitestka load convert --actions smoke.json -o load.json --users 20 --time 30
apitestka load run --actions smoke.json --users 20 --spawn-rate 5 --time 30 \
    --max-failure-rate 0.01 --max-p95-ms 500
apitestka load run --report run_success.json --time 60 --python /opt/ld/bin/python
```

JSON actions: `AT_write_load_test` writes the LoadDensity file; `AT_run_load_test` runs it and fails the
action when a threshold is broken.

```json
["AT_run_load_test", {"action_file": "smoke.json", "profile": {"user_count": 20, "test_time": 30},
                      "thresholds": {"max_failure_rate": 0.01, "max_p95_ms": 500}}]
```

### CLI / Developer Experience

```bash
apitestka run actions.json              # or directory
apitestka create my_project
apitestka mock --port 9000
apitestka import openapi.json out.json --format openapi
apitestka repl                          # JSON action REPL
apitestka summary                       # ANSI-coloured summary
apitestka scaffold https://api/x out.json
apitestka completion bash               # source >> ~/.bashrc
apitestka mcp                           # MCP server over stdio
apitestka openapi --report run_success.json -o openapi.json   # infer a spec from a saved run
apitestka openapi --run actions.json    # run first, print the inferred spec
apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000   # see Contract Testing
apitestka generate-tests openapi.json -o actions.json [--ai anthropic]         # see Pluggable AI Backend
apitestka load run --actions smoke.json --users 20 --time 30                    # see Integrations
apitestka trend check                                                           # see Reports and Observability
apitestka spec check openapi.json --run tests/ --min-coverage 0.8               # see Test-as-Spec Loop
```

### Security Probes

```python
from je_api_testka.security import (
    basic_auth_header, bearer_token_header, build_jwt, aws_sigv4_headers,
    scan_security_headers, cors_preflight, probe_rate_limit, probe_ssrf,
    fuzz_string_inputs, run_pip_audit,
)

scan_security_headers(response_headers)              # HSTS, CSP, nosniff…
cors_preflight("https://api/x", origin="https://app")
probe_rate_limit("https://api/x", burst=20)
probe_ssrf("https://api/fetch", parameter="url")
run_pip_audit()                                      # delegates to pip-audit
```

### OpenAPI Inference

```python
from je_api_testka.spec import (
    infer_schema, records_to_openapi, build_openapi, export_openapi, load_report_records, openapi_changelog,
)

records_to_openapi(title="Recovered", version="0.1.0")   # from the in-memory test record
build_openapi(["run_success.json"])                  # record plus saved JSON reports
export_openapi("openapi.json", ["run_success.json"]) # same, written as UTF-8 JSON
openapi_changelog(prev_spec, current_spec)           # markdown diff
```

Records with the same method and path merge into one operation: every status code seen gets
a response entry, query parameter names become `in: query` parameters, and JSON or text
bodies become response and request-body schemas. A saved report is the
`<name>_success.json` file from `generate_json_report`; the `AT_export_openapi` command and
`apitestka openapi` read it too.

### Test-as-Spec Loop

`apitestka spec check` keeps the committed OpenAPI document and the tests in step. It runs the tests (or
reads saved reports) and then does three things:

- **Drift**: every recorded request is checked against the document the way a contract interaction is
  (operation, query parameters, request body, declared status, response schema). A request to an operation
  the document does not declare is reported as undocumented.
- **Coverage**: lists the documented operations no test exercised; `--min-coverage` fails the run below a share.
- **Closing the gap**: `--missing-actions` writes actions for the untested operations (the AI backend when
  one is set, otherwise deterministic requests built from the document's examples). `--inferred-spec` writes
  the document the tests describe, with paths grouped under the committed templates (`/items/7` →
  `/items/{id}`).

The command exits with 1 on an undocumented operation, a drift problem or low coverage. JSON action:
`AT_check_spec_against_tests` (fails the action with the report).

```bash
apitestka spec check openapi.json --run tests/ --min-coverage 0.8 \
    --missing-actions tests/generated.json --inferred-spec build/openapi.inferred.json
```

```python
from je_api_testka.spec.spec_loop import check_records_against_spec, missing_test_actions, infer_spec_from_tests

report = check_records_against_spec(records, committed_spec)   # records: success records of the run
report.coverage, report.uncovered, report.undocumented, report.problems
actions = missing_test_actions(committed_spec, report)
```

### Contract Testing

Pact-style, bidirectional consumer contracts (`je_api_testka.contract`). The consumer's test run
becomes a contract in the Pact v2 file format, so it can go to a Pact Broker or Pactflow as it is. Every
response body gets a `type` matching rule by default: the provider must return the same structure
and value types, not the same values. The contract is then checked from two sides:

- **Provider verification** replays each interaction against a running provider: equal status,
  the contract's headers present (`Content-Type` by media type), and the body satisfying the
  matching rules (`type`, `regex`, `min`; objects may carry extra keys). Provider states
  (`providerState`) are set up through a Python callable or a setup URL that receives
  `{"consumer": ..., "state": ...}`.
- **Bidirectional check** compares the contract with the provider's OpenAPI document without
  running the provider: the operation exists (path templates match), query parameters are declared
  and required ones sent, the request body fits its schema, the status is declared (exact, `2XX` or
  `default`), and the response body fits its schema (`$ref`, `allOf` / `anyOf` / `oneOf`, `nullable`).
  The provider keeps its OpenAPI document honest from its own test run, e.g. with `apitestka openapi`.

```python
from je_api_testka.contract import write_contract, verify_contract, check_contract_against_openapi

# consumer: its test run (current record plus saved reports) becomes the contract
write_contract("pacts/web-shop.json", consumer="web", provider="shop", report_paths=["run_success.json"])
# provider: replay the contract against a running provider
verify_contract("pacts/web-shop.json", base_url="http://localhost:8000")
# bidirectional: check the contract against the provider's OpenAPI document, no provider needed
check_contract_against_openapi("pacts/web-shop.json", "openapi.json")
```

```bash
apitestka contract record --report run_success.json --consumer web --provider shop -o pacts/web-shop.json
apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000
apitestka contract compare pacts/web-shop.json openapi.json
```

`verify` and `compare` print a report (`--json` for JSON) and exit with 1 when the contract does not
hold. JSON actions: `AT_write_contract`, `AT_verify_contract`, `AT_check_contract_against_openapi`
(the last two fail the action with the report).

### GUI

```bash
pip install 'je_api_testka[gui]'
```

Headless models (`HistoryPanelModel`, `EnvManagerModel`, `render_side_by_side`) live in
the `je_api_testka.gui.*` submodules (`history_panel`, `env_manager_model`, `diff_viewer`),
allowing tests and headless tooling to drive panels without PySide6. The actual Qt widgets
live in `main_widget.py`.

Locales: English, 繁體中文, 简体中文, 日本語. Switch via `LanguageWrapper.reset_language(...)`.

### Pluggable AI Backend

Three helpers can ask a language model: `generate_tests_from_openapi` (actions for every
operation), `generate_fake_payload` (a value for a JSON Schema) and `classify_failures` (labels for the
errors its rules cannot place). The default backend (`NoOpAIBackend`) never calls a network, and every
helper then uses its deterministic fallback, as it also does when a reply is empty or unusable
(generated actions must be a JSON list of `["AT_...", {...}]`).

`AnthropicAIBackend` (`ai` extra) is the reference implementation on the Anthropic API. It takes
credentials from the environment the `anthropic` SDK reads (`ANTHROPIC_API_KEY`, or an `ant auth login`
profile) and never stores a key. The default model is `claude-opus-5-5`, with effort `medium` sent
explicitly. Server-side refusal fallbacks are on (`fallbacks="default"`); pass `fallbacks=None` to
turn them off. A refusal, a truncated reply, a rate limit, a server error or a network failure gives
the deterministic fallback, and a rejected request (bad key, unknown model) raises `APIAIBackendException`.

```python
from je_api_testka.ai import AnthropicAIBackend, set_ai_backend, generate_tests_from_openapi

set_ai_backend(AnthropicAIBackend())                   # claude-opus-5-5, effort "medium"
set_ai_backend(AnthropicAIBackend(model="claude-sonnet-5-5", effort="low", timeout=60))
actions = generate_tests_from_openapi(my_openapi_spec)
```

Select a backend with `set_ai_backend(...)`, `select_ai_backend("anthropic", model=..., effort=...)`,
the `AT_select_ai_backend` action, or the environment: without a selection, the first use reads
`APITESTKA_AI_BACKEND` (`noop` or `anthropic`), `APITESTKA_AI_MODEL` and `APITESTKA_AI_EFFORT`.

```bash
pip install 'je_api_testka[ai]'
export ANTHROPIC_API_KEY=...                            # or an `ant auth login` profile
apitestka generate-tests openapi.json -o actions.json --ai anthropic --effort high
APITESTKA_AI_BACKEND=anthropic apitestka mcp            # any entry point, no code changes
```

Any other provider plugs in the same way: subclass `AIBackend` and implement `complete(prompt, *, context)`.

---

## MCP Server for Claude

APITestka ships an [MCP](https://modelcontextprotocol.io/) server so Claude (and any other
MCP-compatible client) can drive the framework. Eight tools are exposed:

| Tool | Purpose |
|---|---|
| `apitestka_run_action` | Execute an action list |
| `apitestka_test_api` | One-shot HTTP request via `requests` backend |
| `apitestka_curl_to_action` | cURL → action JSON |
| `apitestka_har_import` | HAR file → action list |
| `apitestka_render_markdown` | Markdown report from current records |
| `apitestka_records_to_openapi` | Reconstruct an OpenAPI document from the record or saved reports (`report_paths`) |
| `apitestka_clear_records` | Wipe the test record |
| `apitestka_get_records` | Return successes / failures |

Install and run:

```bash
pip install 'je_api_testka[mcp]'
apitestka-mcp        # or: apitestka mcp / python -m je_api_testka.mcp_server
```

Claude Code config (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "apitestka": {
      "command": "apitestka-mcp"
    }
  }
}
```

---

## Project Structure

```
je_api_testka/
├── __init__.py              # Public API exports
├── __main__.py              # Legacy CLI entry point
├── ai/                      # Pluggable AI backend + helpers
├── cli/                     # apitestka CLI subcommands + REPL + completions
├── connection/              # ConnectionOptions, DNS override, Cassette
├── contract/                # Pact-style consumer contracts, provider verification, OpenAPI check
├── data/                    # VariableStore, templates, faker, env profiles
├── diff/                    # Response diff / contract drift / SLA
├── graphql_wrapper/         # GraphQL helper
├── gui/                     # Optional PySide6 GUI + headless models
├── httpx_wrapper/           # httpx sync + async wrapper
├── integrations/            # Notifications, PR comments, importers
├── mcp_server/              # Claude / MCP server
├── pytest_plugin/           # pytest fixtures
├── requests_wrapper/        # requests wrapper
├── runner/                  # Parallel runner, tag filter, dependency runner
├── security/                # Auth helpers, fuzz, header / CORS / SSRF / rate-limit / CVE
├── spec/                    # OpenAPI inference / changelog
├── sse_wrapper/             # Server-Sent Events helper
├── utils/                   # Executor, mock server, generators, etc.
└── websocket_wrapper/       # WebSocket wrapper
```

---

## Optional Extras

```bash
pip install 'je_api_testka[websocket]'
pip install 'je_api_testka[grpc]'
pip install 'je_api_testka[ai]'
pip install 'je_api_testka[schema]'
pip install 'je_api_testka[security]'
pip install 'je_api_testka[otel]'
pip install 'je_api_testka[mcp]'
pip install 'je_api_testka[gui]'
```

---

## Development

```bash
git clone https://github.com/Integration-Automation/APITestka.git
cd APITestka
pip install -r dev_requirements.txt
pytest                     # full suite (~300+ tests)
```

CI runs the suite against Python 3.10 – 3.14 on Ubuntu, macOS, and Windows.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Every commit must ship with unit tests
(see `CLAUDE.md` → *Testing Guidelines*).

---

## License

MIT — see [licenses/APITestka_LICENSE](licenses/APITestka_LICENSE).

---

## Links

- **Homepage:** https://github.com/Integration-Automation/APITestka
- **Documentation:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
- **MCP:** https://modelcontextprotocol.io/
