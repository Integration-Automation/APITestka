# APITestka

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](../licenses/APITestka_LICENSE)
[![PyPI](https://img.shields.io/pypi/v/je_api_testka.svg)](https://pypi.org/project/je_api_testka/)
[![Documentation Status](https://readthedocs.org/projects/apitestka/badge/?version=latest)](https://apitestka.readthedocs.io/en/latest/?badge=latest)

**APITestka** 是一个轻量级、跨平台的 Python 自动化 API 测试框架。
最初是 HTTP/HTTPS / SOAP-XML / JSON 的请求执行器,搭配报告生成与 JSON 驱动的 executor;
现在已扩充为完整工具集:变量链式请求、OpenAPI / Postman / HAR / cURL 导入器、
record-replay 代理、安全检测、并行执行 runner,以及给 Claude 用的 MCP server 等等。

> **其他语言:**
> [English](../README.md) | [繁體中文](README_zh-TW.md)

---

## 目录

- [亮点](#亮点)
- [安装](#安装)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [功能总览](#功能总览)
  - [HTTP / 协议后端](#http--协议后端)
  - [数据层](#数据层)
  - [断言、Diff 与 SLA](#断言diff-与-sla)
  - [连接层](#连接层)
  - [模拟服务器](#模拟服务器)
  - [Runner](#runner)
  - [报告与可观测性](#报告与可观测性)
  - [生态集成](#生态集成)
  - [CLI / 开发体验](#cli--开发体验)
  - [安全检测](#安全检测)
  - [OpenAPI 反推](#openapi-反推)
  - [GUI](#gui)
  - [可插拔 AI 后端](#可插拔-ai-后端)
- [Claude 的 MCP Server](#claude-的-mcp-server)
- [项目结构](#项目结构)
- [Optional Extras](#optional-extras)
- [开发](#开发)
- [贡献](#贡献)
- [许可证](#许可证)
- [链接](#链接)

---

## 亮点

| 类别 | 内容 |
|---|---|
| **后端** | `requests`(同步、session)、`httpx`(同步 + 异步、HTTP/2)、WebSocket、SSE、GraphQL |
| **数据层** | 变量存储、`{{var}}` 模板、CSV/JSON 数据驱动、环境配置、假数据 |
| **断言** | 字段断言、JSON Schema、JSONPath、Snapshot、结构化 diff、OpenAPI contract drift、响应时间 SLA |
| **连接** | mTLS、代理、DNS override、VCR-style cassette 录制/回放 |
| **模拟服务器** | 静态、动态、stateful、故障注入、OpenAPI 驱动、Jinja 模板、Webhook 接收、record-replay 代理 |
| **Runner** | 顺序与并行、Tag 过滤、Dependency-aware 排序、Retry 策略 |
| **报告** | HTML / JSON / XML / **JUnit / Allure / Markdown** / shields.io badge / SQLite 趋势库 / Run diff |
| **生态集成** | Slack / Teams / Discord webhook、GitHub PR comment、cURL & HAR 导入、OpenAPI / Postman 导入 |
| **CLI / DX** | 子命令式 CLI、REPL、终端摘要、Shell completion、Scaffold |
| **安全** | Auth helper(Basic / Bearer / JWT / AWS SigV4)、Header / CORS / Rate limit / SSRF probe、pip-audit、Fuzz |
| **Spec 反推** | 测试记录 → OpenAPI、JSON Schema 推断、OpenAPI changelog |
| **AI** | 可插拔后端,LLM 不可用时自动回退到确定性 fallback |
| **MCP** | 一级支持 Claude Code,将框架作为 MCP 工具暴露 |
| **GUI** | 可选 PySide6 GUI(英 / 繁中 / 简中 / 日)+ 嵌入 Swagger UI |
| **跨平台** | Windows、macOS、Linux,Python 3.10–3.14 |

---

## 安装

```bash
pip install je_api_testka
```

Optional extras(`pip install 'je_api_testka[<extra>]'`):

| Extra | 增加的功能 |
|---|---|
| `gui` | PySide6 GUI |
| `websocket` | `websockets`,供 WebSocket wrapper 使用 |
| `schema` | `jsonschema` / `jsonpath-ng` 进阶断言 |
| `security` | `pyjwt` / `botocore` 给 JWT / AWS SigV4 |
| `otel` | `opentelemetry-api` / `opentelemetry-sdk` tracing hook |
| `mcp` | `mcp` Python SDK 给 MCP server |

---

## 快速开始

```python
from je_api_testka import test_api_method_requests, generate_html_report

test_api_method_requests(
    "get", "https://httpbin.org/get",
    result_check_dict={"status_code": 200},
)
generate_html_report("smoke")
```

JSON 驱动版本(`smoke.json`):

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

## 核心概念

- **后端** — 所有 HTTP 调用通过 `requests_wrapper` / `httpx_wrapper` /
  `websocket_wrapper` / `sse_wrapper` / `graphql_wrapper`,共用同一份记录格式。
- **`test_record_instance`** — thread-safe 全局单例,捕获所有 request/response;
  报告、diff、badge、trend 都从这里读取。
- **Executor** — `AT_*` 命名的命令对应到 Python 函数。JSON action list 驱动它,
  所有新功能都在这里注册,`apitestka run` 即可使用。
- **VariableStore** — thread-safe 的 key/value 存储。`{{var}}` placeholder
  在 payload、URL、header、template 中均可解析。配 `AT_extract_and_store` 串接 request。
- **Optional dependencies** — 重型功能(WebSocket、JSON Schema、JWT、MCP)走 extras,
  未安装时调用会抛出友好提示。

---

## 功能总览

### HTTP / 协议后端

| 后端 | 函数 |
|---|---|
| `requests` | `test_api_method_requests`(同步、session) |
| `httpx` 同步 | `test_api_method_httpx` |
| `httpx` 异步 | `test_api_method_httpx_async`(`http2=True` 启用 HTTP/2) |
| WebSocket | `test_api_method_websocket`、`test_api_method_websocket_async`(extra:`websocket`) |
| SSE | `iter_sse_events`、`test_api_method_sse` |
| GraphQL | `test_api_method_graphql`、`test_api_method_graphql_async` |

```python
from je_api_testka import test_api_method_graphql

test_api_method_graphql(
    "https://api.example.invalid/graphql",
    query="query Get($id: ID!) { user(id: $id) { id name } }",
    variables={"id": "42"},
)
```

### 数据层

```python
from je_api_testka import (
    variable_store, render_template, extract_and_store, load_env_profile,
    fake_uuid, iter_csv_rows,
)

load_env_profile("envs/dev.json")
extract_and_store({"data": {"id": 7}}, "data.id", "user_id")
render_template("/users/{{user_id}}")        # -> "/users/7"

for row in iter_csv_rows("data/users.csv"):
    variable_store.set("email", row["email"])
    test_api_method_requests("post", "https://x.invalid/login", json=row)
```

Executor 命令:`AT_set_variable`、`AT_get_variable`、`AT_clear_variables`、
`AT_extract_and_store`、`AT_render_template`、`AT_fake_uuid`、`AT_fake_email`、
`AT_fake_word`、`AT_load_env_profile`。

### 断言、Diff 与 SLA

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

### 连接层

```python
from je_api_testka.connection import (
    ConnectionOptions, apply_to_requests_kwargs,
    dns_override, Cassette, replay_or_record,
)

options = ConnectionOptions(cert=("c.crt", "c.key"),
                            proxies={"https": "http://proxy:8080"})

with dns_override({"api.example.invalid": "127.0.0.1"}):
    test_api_method_requests("get", "https://api.example.invalid/health")

cassette = Cassette("tape.json")  # 离线 replay-or-record
```

### 模拟服务器

`FlaskMockServer` 现支持以下功能:

| 功能 | API |
|---|---|
| 静态 routes | `flask_mock_server_instance.add_router({...})` |
| 动态 routes | `server.add_dynamic_route(...)` 搭配 `DynamicRouter` |
| Stateful 存储 | `server.state`(`StatefulStore`) |
| 故障注入 | `server.fault_injector.configure(latency_seconds=..., failure_probability=...)` |
| OpenAPI 驱动 | `server.load_openapi(spec)` |
| 模板回应 | `server.add_template_route("/x", {"msg": "{{name}}"})` |
| 接收 Webhook | `server.add_webhook("/hook")`,读 `server.webhook_receiver.all()` |
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

### 报告与可观测性

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
generate_allure_report("allure-results")    # `allure generate` 可吃
generate_markdown_report("report.md")       # Slack / GitHub 友好
generate_badge("badge.json")                # shields.io endpoint
record_current_run("trend.sqlite")          # 历史趋势
```

OpenTelemetry hook(未安装 `opentelemetry-api` 时自动 no-op):

```python
from je_api_testka.utils.observability import instrument_request

with instrument_request("GET", "https://x.invalid"):
    test_api_method_requests("get", "https://x.invalid")
```

### 生态集成

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

### CLI / 开发体验

```bash
apitestka run actions.json              # 也可指定目录
apitestka create my_project
apitestka mock --port 9000
apitestka import openapi.json out.json --format openapi
apitestka repl                          # JSON action REPL
apitestka summary                       # ANSI 彩色摘要
apitestka scaffold https://api/x out.json
apitestka completion bash               # source >> ~/.bashrc
apitestka mcp                           # 走 stdio 启动 MCP server
```

### 安全检测

```python
from je_api_testka.security import (
    basic_auth_header, bearer_token_header, build_jwt, aws_sigv4_headers,
    scan_security_headers, cors_preflight, probe_rate_limit, probe_ssrf,
    fuzz_string_inputs, run_pip_audit,
)

scan_security_headers(response_headers)              # HSTS / CSP / nosniff…
cors_preflight("https://api/x", origin="https://app")
probe_rate_limit("https://api/x", burst=20)
probe_ssrf("https://api/fetch", parameter="url")
run_pip_audit()
```

### OpenAPI 反推

```python
from je_api_testka.spec import infer_schema, records_to_openapi, openapi_changelog

records_to_openapi(title="Recovered", version="0.1.0")
openapi_changelog(prev_spec, current_spec)           # markdown changelog
```

### GUI

```bash
pip install 'je_api_testka[gui]'
```

`je_api_testka.gui` 中的 headless model(`HistoryPanelModel`、`EnvManagerModel`、
`render_side_by_side`)让测试与 headless 工具无需 PySide6 也能驱动面板。
真正的 Qt widget 在 `main_widget.py`。

语种:English、繁體中文、简体中文、日本語。通过 `LanguageWrapper.reset_language(...)` 切换。

### 可插拔 AI 后端

默认 `NoOpAIBackend` 不会触网。要启用 LLM 驱动的测试生成,自行挂载:

```python
from je_api_testka.ai import AIBackend, set_ai_backend, generate_tests_from_openapi

class AnthropicBackend(AIBackend):
    def complete(self, prompt, *, context=None):
        ...  # 调用你的 LLM provider
        return llm_response_text

set_ai_backend(AnthropicBackend())
actions = generate_tests_from_openapi(my_openapi_spec)  # LLM 回应不是合法 JSON 时
                                                        # 自动降级为确定性 happy path
```

---

## Claude 的 MCP Server

APITestka 内置 [MCP](https://modelcontextprotocol.io/) server,Claude 等
MCP-compatible client 可以直接驱动本框架。共暴露八个工具:

| Tool | 用途 |
|---|---|
| `apitestka_run_action` | 执行 action list |
| `apitestka_test_api` | 一次性 HTTP 请求(走 `requests` 后端) |
| `apitestka_curl_to_action` | cURL → action JSON |
| `apitestka_har_import` | HAR 文件 → action list |
| `apitestka_render_markdown` | 从当前记录生成 Markdown 报告 |
| `apitestka_records_to_openapi` | 反推 OpenAPI 文档 |
| `apitestka_clear_records` | 清空测试记录 |
| `apitestka_get_records` | 拿当前的成功 / 失败记录 |

安装与启动:

```bash
pip install 'je_api_testka[mcp]'
apitestka-mcp        # 或: apitestka mcp / python -m je_api_testka.mcp_server
```

Claude Code 配置(`~/.claude/mcp.json`):

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

## 项目结构

```
je_api_testka/
├── __init__.py              # 公开 API
├── __main__.py              # 旧版 CLI 入口
├── ai/                      # 可插拔 AI 后端 + 周边
├── cli/                     # apitestka CLI 子命令、REPL、shell completion
├── connection/              # ConnectionOptions、DNS override、Cassette
├── data/                    # VariableStore、template、faker、env profile
├── diff/                    # Response diff / contract drift / SLA
├── graphql_wrapper/         # GraphQL helper
├── gui/                     # 可选 PySide6 GUI + headless model
├── httpx_wrapper/           # httpx 同步 + 异步 wrapper
├── integrations/            # 通知、PR comment、导入器
├── mcp_server/              # Claude / MCP server
├── pytest_plugin/           # pytest fixtures
├── requests_wrapper/        # requests wrapper
├── runner/                  # Parallel / tag / dependency runner
├── security/                # Auth、fuzz、header / CORS / SSRF / rate limit / CVE
├── spec/                    # OpenAPI 反推 / changelog
├── sse_wrapper/             # SSE helper
├── utils/                   # Executor、mock server、报告生成器等
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

## 开发

```bash
git clone https://github.com/Intergration-Automation-Testing/APITestka.git
cd APITestka
pip install -r dev_requirements.txt
pytest                     # 整套(300+ 测试)
```

CI 矩阵:Ubuntu / macOS / Windows × Python 3.10–3.14。

---

## 贡献

请见 [CONTRIBUTING.md](../CONTRIBUTING.md)。每个 commit 必须附带单元测试
(详情见 `CLAUDE.md` 的 *Testing Guidelines* 段)。

---

## 许可证

MIT — 详见 [licenses/APITestka_LICENSE](../licenses/APITestka_LICENSE)。

---

## 链接

- **首页:** https://github.com/Intergration-Automation-Testing/APITestka
- **文档:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
- **MCP:** https://modelcontextprotocol.io/
