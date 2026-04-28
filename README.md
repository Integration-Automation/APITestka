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
| **Mock server** | Static, dynamic, stateful, fault injection, OpenAPI-driven, Jinja templating, webhook receiver, record-replay proxy |
| **Runner** | Sequential & parallel execution, tag filters, dependency-aware ordering, retry policies |
| **Reports** | HTML / JSON / XML / **JUnit / Allure / Markdown** / shields.io badge / SQLite trend store / run diff |
| **Integrations** | Slack / Teams / Discord webhook, GitHub PR comment, cURL & HAR importers, OpenAPI / Postman importer |
| **CLI / DX** | Subcommand CLI, REPL, terminal summary, shell completion, scaffold |
| **Security** | Auth helpers (Basic / Bearer / JWT / AWS SigV4), header / CORS / rate-limit / SSRF probes, pip-audit wrapper, fuzz inputs |
| **Spec inference** | Test record → OpenAPI, JSON Schema inference, OpenAPI changelog |
| **AI** | Pluggable backend with deterministic fallback for test generation, fake data, failure classification |
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
    ["AT_test_api_method_requests", {
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
from je_api_testka import (
    variable_store, render_template, extract_and_store, load_env_profile,
    fake_uuid, iter_csv_rows,
)

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
    diff_payloads, diff_openapi_specs, RetryPolicy, retry_call,
)
from je_api_testka.diff.sla_check import ResponseSLA, assert_sla

check_json_schema(payload, {"type": "object", "required": ["id"]})
check_jsonpath(payload, "$.data.id", expected=7)
assert_snapshot("user-by-id", payload, ignore_keys=["timestamp"])
diff = diff_payloads(prod_response, staging_response, ignore_paths=["server_time"])
assert_sla(records, ResponseSLA(max_ms=2000, p95_ms=1500))
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
```

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
from je_api_testka.spec import infer_schema, records_to_openapi, openapi_changelog

records_to_openapi(title="Recovered", version="0.1.0")
openapi_changelog(prev_spec, current_spec)           # markdown diff
```

### GUI

```bash
pip install 'je_api_testka[gui]'
```

Headless models (`HistoryPanelModel`, `EnvManagerModel`, `render_side_by_side`) live in
`je_api_testka.gui`, allowing tests and headless tooling to drive panels without
PySide6. The actual Qt widgets live in `main_widget.py`.

Locales: English, 繁體中文, 简体中文, 日本語. Switch via `LanguageWrapper.reset_language(...)`.

### Pluggable AI Backend

Default backend (`NoOpAIBackend`) never calls a network. Plug in your own to enable
LLM-driven test generation:

```python
from je_api_testka.ai import AIBackend, set_ai_backend, generate_tests_from_openapi

class AnthropicBackend(AIBackend):
    def complete(self, prompt, *, context=None):
        ...  # call your provider
        return llm_response_text

set_ai_backend(AnthropicBackend())
actions = generate_tests_from_openapi(my_openapi_spec)  # falls back to a deterministic
                                                        # happy path if the LLM reply is
                                                        # not valid JSON
```

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
| `apitestka_records_to_openapi` | Reconstruct an OpenAPI document |
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
pip install 'je_api_testka[schema]'
pip install 'je_api_testka[security]'
pip install 'je_api_testka[otel]'
pip install 'je_api_testka[mcp]'
pip install 'je_api_testka[gui]'
```

---

## Development

```bash
git clone https://github.com/Intergration-Automation-Testing/APITestka.git
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

- **Homepage:** https://github.com/Intergration-Automation-Testing/APITestka
- **Documentation:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
- **MCP:** https://modelcontextprotocol.io/
