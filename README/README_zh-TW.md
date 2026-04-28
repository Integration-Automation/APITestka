# APITestka

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](../licenses/APITestka_LICENSE)
[![PyPI](https://img.shields.io/pypi/v/je_api_testka.svg)](https://pypi.org/project/je_api_testka/)
[![Documentation Status](https://readthedocs.org/projects/apitestka/badge/?version=latest)](https://apitestka.readthedocs.io/en/latest/?badge=latest)

**APITestka** 是一個輕量級、跨平台的 Python 自動化 API 測試框架。
它最初是 HTTP/HTTPS / SOAP-XML / JSON 的請求執行器,搭配報告產生與 JSON 驅動的 executor;
現在已擴充為一整套工具:變數鏈式請求、OpenAPI / Postman / HAR / cURL 匯入器、
record-replay proxy、安全性檢測、平行執行 runner,以及給 Claude 用的 MCP server 等等。

> **其他語言:**
> [English](../README.md) | [简体中文](README_zh-CN.md)

---

## 目錄

- [亮點](#亮點)
- [安裝](#安裝)
- [快速開始](#快速開始)
- [核心概念](#核心概念)
- [功能總覽](#功能總覽)
  - [HTTP / 協定後端](#http--協定後端)
  - [資料層](#資料層)
  - [斷言、Diff 與 SLA](#斷言diff-與-sla)
  - [連線層](#連線層)
  - [模擬伺服器](#模擬伺服器)
  - [Runner](#runner)
  - [報告與可觀測性](#報告與可觀測性)
  - [生態整合](#生態整合)
  - [CLI / 開發體驗](#cli--開發體驗)
  - [安全檢測](#安全檢測)
  - [OpenAPI 反推](#openapi-反推)
  - [GUI](#gui)
  - [可插拔 AI 後端](#可插拔-ai-後端)
- [Claude 用的 MCP Server](#claude-用的-mcp-server)
- [專案結構](#專案結構)
- [Optional Extras](#optional-extras)
- [開發](#開發)
- [貢獻](#貢獻)
- [授權](#授權)
- [連結](#連結)

---

## 亮點

| 類別 | 內容 |
|---|---|
| **後端** | `requests`(同步、session)、`httpx`(同步 + 非同步、HTTP/2)、WebSocket、SSE、GraphQL |
| **資料層** | 變數儲存區、`{{var}}` 模板、CSV/JSON 資料驅動、環境設定檔、假資料 |
| **斷言** | 欄位斷言、JSON Schema、JSONPath、Snapshot、結構化 diff、OpenAPI contract drift、回應時間 SLA |
| **連線** | mTLS、Proxy、DNS override、VCR-style cassette 錄製/回放 |
| **模擬伺服器** | 靜態、動態、stateful、故障注入、OpenAPI 驅動、Jinja 模板、Webhook 接收、record-replay proxy |
| **Runner** | 順序與平行執行、Tag 過濾、Dependency-aware 排序、Retry 策略 |
| **報告** | HTML / JSON / XML / **JUnit / Allure / Markdown** / shields.io badge / SQLite 趨勢資料庫 / Run diff |
| **生態整合** | Slack / Teams / Discord webhook、GitHub PR comment、cURL & HAR 匯入、OpenAPI / Postman 匯入 |
| **CLI / DX** | 子命令式 CLI、REPL、終端摘要、Shell completion、Scaffold |
| **安全** | Auth helper(Basic / Bearer / JWT / AWS SigV4)、Header / CORS / Rate limit / SSRF probe、pip-audit、Fuzz |
| **Spec 反推** | 測試紀錄 → OpenAPI、JSON Schema 推斷、OpenAPI changelog |
| **AI** | 可插拔後端,LLM 不可用時自動退回確定性 fallback |
| **MCP** | 一級支援 Claude Code,將框架曝露為 MCP 工具 |
| **GUI** | 可選 PySide6 GUI(英 / 繁中 / 简中 / 日)+ 嵌入 Swagger UI |
| **跨平台** | Windows、macOS、Linux,Python 3.10–3.14 |

---

## 安裝

```bash
pip install je_api_testka
```

Optional extras(`pip install 'je_api_testka[<extra>]'`):

| Extra | 加入的功能 |
|---|---|
| `gui` | PySide6 GUI |
| `websocket` | `websockets` 給 WebSocket wrapper 使用 |
| `schema` | `jsonschema` / `jsonpath-ng` 進階斷言 |
| `security` | `pyjwt` / `botocore` 給 JWT / AWS SigV4 |
| `otel` | `opentelemetry-api` / `opentelemetry-sdk` tracing hook |
| `mcp` | `mcp` Python SDK 給 MCP server |

---

## 快速開始

```python
from je_api_testka import test_api_method_requests, generate_html_report

test_api_method_requests(
    "get", "https://httpbin.org/get",
    result_check_dict={"status_code": 200},
)
generate_html_report("smoke")
```

JSON 驅動版本(`smoke.json`):

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

- **後端** — 所有 HTTP 呼叫經過 `requests_wrapper` / `httpx_wrapper` /
  `websocket_wrapper` / `sse_wrapper` / `graphql_wrapper`,共用同一份紀錄格式。
- **`test_record_instance`** — thread-safe 全域單例,捕捉所有 request/response;
  報告、diff、badge、trend 全部從這裡讀取。
- **Executor** — `AT_*` 命名的命令對應到 Python 函式。JSON action list 驅動它,
  所有新功能都在這裡註冊,讓 `apitestka run` 可以無痛使用。
- **VariableStore** — thread-safe 的 key/value 儲存。`{{var}}` placeholder
  在 payload、URL、header、template 中皆可解析。配 `AT_extract_and_store` 串接 request。
- **Optional dependencies** — 重型功能(WebSocket、JSON Schema、JWT、MCP)走 extras,
  未安裝時呼叫會拋出友善訊息。

---

## 功能總覽

### HTTP / 協定後端

| 後端 | 函式 |
|---|---|
| `requests` | `test_api_method_requests`(同步、session) |
| `httpx` 同步 | `test_api_method_httpx` |
| `httpx` 非同步 | `test_api_method_httpx_async`(`http2=True` 啟用 HTTP/2) |
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

### 資料層

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

### 斷言、Diff 與 SLA

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

### 連線層

```python
from je_api_testka.connection import (
    ConnectionOptions, apply_to_requests_kwargs,
    dns_override, Cassette, replay_or_record,
)

options = ConnectionOptions(cert=("c.crt", "c.key"),
                            proxies={"https": "http://proxy:8080"})

with dns_override({"api.example.invalid": "127.0.0.1"}):
    test_api_method_requests("get", "https://api.example.invalid/health")

cassette = Cassette("tape.json")  # 離線 replay-or-record
```

### 模擬伺服器

`FlaskMockServer` 現在支援以下功能:

| 功能 | API |
|---|---|
| 靜態 routes | `flask_mock_server_instance.add_router({...})` |
| 動態 routes | `server.add_dynamic_route(...)` 搭配 `DynamicRouter` |
| Stateful 儲存 | `server.state`(`StatefulStore`) |
| 故障注入 | `server.fault_injector.configure(latency_seconds=..., failure_probability=...)` |
| OpenAPI 驅動 | `server.load_openapi(spec)` |
| 模板回應 | `server.add_template_route("/x", {"msg": "{{name}}"})` |
| 接收 Webhook | `server.add_webhook("/hook")`,讀 `server.webhook_receiver.all()` |
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

### 報告與可觀測性

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
generate_markdown_report("report.md")       # Slack / GitHub 友善
generate_badge("badge.json")                # shields.io endpoint
record_current_run("trend.sqlite")          # 歷史趨勢
```

OpenTelemetry hook(沒裝 `opentelemetry-api` 時自動 no-op):

```python
from je_api_testka.utils.observability import instrument_request

with instrument_request("GET", "https://x.invalid"):
    test_api_method_requests("get", "https://x.invalid")
```

### 生態整合

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

### CLI / 開發體驗

```bash
apitestka run actions.json              # 也可給目錄
apitestka create my_project
apitestka mock --port 9000
apitestka import openapi.json out.json --format openapi
apitestka repl                          # JSON action REPL
apitestka summary                       # ANSI 彩色摘要
apitestka scaffold https://api/x out.json
apitestka completion bash               # source >> ~/.bashrc
apitestka mcp                           # 走 stdio 啟動 MCP server
```

### 安全檢測

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

`je_api_testka.gui` 內的 headless model(`HistoryPanelModel`、`EnvManagerModel`、
`render_side_by_side`)讓測試與 headless 工具不需 PySide6 也能驅動面板。
真正的 Qt widget 在 `main_widget.py`。

語系:English、繁體中文、简体中文、日本語。透過 `LanguageWrapper.reset_language(...)` 切換。

### 可插拔 AI 後端

預設 `NoOpAIBackend` 不會碰網路。要啟用 LLM 驅動的測試生成,自行掛載:

```python
from je_api_testka.ai import AIBackend, set_ai_backend, generate_tests_from_openapi

class AnthropicBackend(AIBackend):
    def complete(self, prompt, *, context=None):
        ...  # 呼叫你的 LLM provider
        return llm_response_text

set_ai_backend(AnthropicBackend())
actions = generate_tests_from_openapi(my_openapi_spec)  # LLM 回應不是合法 JSON
                                                        # 時會自動降級為確定性 happy path
```

---

## Claude 用的 MCP Server

APITestka 內建 [MCP](https://modelcontextprotocol.io/) server,讓 Claude 等
MCP-compatible client 可以直接驅動本框架。共曝露八個工具:

| Tool | 用途 |
|---|---|
| `apitestka_run_action` | 執行 action list |
| `apitestka_test_api` | 一次性 HTTP 請求(走 `requests` 後端) |
| `apitestka_curl_to_action` | cURL → action JSON |
| `apitestka_har_import` | HAR 檔 → action list |
| `apitestka_render_markdown` | 從目前紀錄產 Markdown 報告 |
| `apitestka_records_to_openapi` | 反推 OpenAPI 文件 |
| `apitestka_clear_records` | 清空測試紀錄 |
| `apitestka_get_records` | 拿目前的成功 / 失敗紀錄 |

安裝與啟動:

```bash
pip install 'je_api_testka[mcp]'
apitestka-mcp        # 或: apitestka mcp / python -m je_api_testka.mcp_server
```

Claude Code 設定(`~/.claude/mcp.json`):

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

## 專案結構

```
je_api_testka/
├── __init__.py              # 公開 API
├── __main__.py              # 舊版 CLI 進入點
├── ai/                      # 可插拔 AI 後端 + 周邊
├── cli/                     # apitestka CLI 子命令、REPL、shell completion
├── connection/              # ConnectionOptions、DNS override、Cassette
├── data/                    # VariableStore、template、faker、env profile
├── diff/                    # Response diff / contract drift / SLA
├── graphql_wrapper/         # GraphQL helper
├── gui/                     # 可選 PySide6 GUI + headless model
├── httpx_wrapper/           # httpx 同步 + 非同步 wrapper
├── integrations/            # 通知、PR comment、匯入器
├── mcp_server/              # Claude / MCP server
├── pytest_plugin/           # pytest fixtures
├── requests_wrapper/        # requests wrapper
├── runner/                  # Parallel / tag / dependency runner
├── security/                # Auth、fuzz、header / CORS / SSRF / rate limit / CVE
├── spec/                    # OpenAPI 反推 / changelog
├── sse_wrapper/             # SSE helper
├── utils/                   # Executor、mock server、報告產生器等
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

## 開發

```bash
git clone https://github.com/Intergration-Automation-Testing/APITestka.git
cd APITestka
pip install -r dev_requirements.txt
pytest                     # 整套(300+ 測試)
```

CI 矩陣:Ubuntu / macOS / Windows × Python 3.10–3.14。

---

## 貢獻

請見 [CONTRIBUTING.md](../CONTRIBUTING.md)。每個 commit 必須附單元測試
(細節見 `CLAUDE.md` 的 *Testing Guidelines* 段)。

---

## 授權

MIT — 詳見 [licenses/APITestka_LICENSE](../licenses/APITestka_LICENSE)。

---

## 連結

- **首頁:** https://github.com/Intergration-Automation-Testing/APITestka
- **文件:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
- **MCP:** https://modelcontextprotocol.io/
