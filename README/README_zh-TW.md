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
  - [測試即規格迴路](#測試即規格迴路)
  - [契約測試](#契約測試)
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
| **模擬伺服器** | 靜態、動態、stateful、故障注入、OpenAPI 驅動、Jinja 模板、Webhook 接收、record-replay proxy、WebSocket 與 gRPC 端點 |
| **Runner** | 順序與平行執行、Tag 過濾、Dependency-aware 排序、Retry 策略 |
| **報告** | HTML / JSON / XML / **JUnit / Allure / Markdown** / shields.io badge / SQLite 趨勢資料庫 / Run diff / 各端點延遲趨勢與異常偵測 |
| **生態整合** | Slack / Teams / Discord webhook、GitHub PR comment、cURL & HAR 匯入、OpenAPI / Postman 匯入、LoadDensity 負載測試橋接 |
| **CLI / DX** | 子命令式 CLI、REPL、終端摘要、Shell completion、Scaffold |
| **安全** | Auth helper(Basic / Bearer / JWT / AWS SigV4)、Header / CORS / Rate limit / SSRF probe、pip-audit、Fuzz |
| **Spec 反推** | 測試紀錄 → OpenAPI、JSON Schema 推斷、OpenAPI changelog、測試即規格迴路(偏移、覆蓋率、替缺口產生測試) |
| **契約測試** | 從測試執行產生 Pact v2 消費者契約、提供端驗證、與 OpenAPI 雙向比對 |
| **AI** | 可插拔後端,LLM 不可用時自動退回確定性 fallback;附 Anthropic 參考實作 |
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
from je_api_testka.data import (
    variable_store, render_template, load_env_profile,
    fake_uuid, iter_csv_rows,
)
from je_api_testka.data.variable_store import extract_and_store

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
    RetryPolicy, retry_call,
)
from je_api_testka.diff import diff_payloads, diff_openapi_specs
from je_api_testka.diff.sla_check import ResponseSLA, assert_sla

check_json_schema(payload, {"type": "object", "required": ["id"]})
check_jsonpath(payload, "$.data.id", expected=7)
assert_snapshot("user-by-id", payload, ignore_keys=["timestamp"])
diff = diff_payloads(prod_response, staging_response, ignore_paths=["server_time"])
assert_sla(records, ResponseSLA(max_ms=2000, p95_ms=1500))
assert_sla(sla={"max_ms": 2000})   # 目前錄下的執行;JSON:["AT_assert_sla", {"sla": {...}}]
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
apitestka mock --config mock.json       # HTTP routes 再加上 WebSocket 與 gRPC 端點
```

**WebSocket 與 gRPC 端點。** `WebSocketMockServer`(`websocket` extra)提供照腳本回應的路由:
連線時送出問候、已知訊息查回覆表、其他訊息走 fallback(`{{message}}` 會回聲,`null` 不回應)。
`GrpcStubServer`(`grpc` extra)不需要編譯 stub,直接用完整路徑提供方法:固定的 unary 回應、
server stream,或回傳某個狀態碼的錯誤。payload 是原始 bytes,所以序列化好的 protobuf 可以給
產生出來的 client 用;`str` 以 UTF-8 送出,其他 JSON 值以精簡 JSON 送出。兩者都會保留收到的內容
供斷言使用,未知的 WebSocket 路徑會以 HTTP 404 拒絕。

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

`--config` 檔可以描述三種端點,每一段都可以省略:

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

JSON action 也能操作同樣的 mock:`AT_mock_start_websocket_server` / `AT_mock_start_grpc_server`
(`routes` / `methods` 用上面的設定格式)、`AT_mock_websocket_received` / `AT_mock_grpc_received`,
以及 `AT_mock_stop_websocket_server` / `AT_mock_stop_grpc_server`。

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

**回應時間趨勢與異常偵測。** `record_endpoint_latencies` 把每次執行各端點的延遲(次數、平均、p50、p95、
最大值)存進趨勢資料庫。端點是 method 加上路徑樣板:有 OpenAPI 時用它的樣板,否則把路徑裡的識別碼一般化
(`/items/42` → `/items/{id}`)。`detect_latency_anomalies` 拿最近一次執行的每個端點,和它先前幾次執行
(預設 20 次、至少 5 次)的中位數與 MAD 比較;變慢至少 20 % 且 5 ms、而且 robust z-score 超過 3.5 才算異常,
這些都可以調整。`generate_trend_report` 寫出每個端點附 sparkline 的 HTML 表格。JSON action:
`AT_record_endpoint_latencies`、`AT_detect_latency_anomalies`、`AT_assert_no_latency_anomalies`、
`AT_generate_trend_report`。

```python
from je_api_testka.utils.generate_report.latency_trends import (
    record_endpoint_latencies, detect_latency_anomalies, assert_no_latency_anomalies,
)
from je_api_testka.utils.generate_report.trend_report import generate_trend_report

record_endpoint_latencies("trend.sqlite", run_label="build-128")   # 每次執行後
assert_no_latency_anomalies("trend.sqlite", {"metric": "p95_ms", "threshold": 3.5})
generate_trend_report("trends.html", "trend.sqlite")
```

```bash
apitestka trend record --report run_success.json --label build-128 --openapi openapi.json
apitestka trend check            # 有異常時結束碼為 1
apitestka trend report -o trends.html
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

每個匯入工具都回傳 `["AT_test_api_method", {...}]` 形式的 action,`execute_action`
可以直接執行。runner 的中繼資料(`id`、`depends_on`、`tags`)可以留在 kwargs 裡,
executor 呼叫前會先拿掉。

**用 LoadDensity 做負載測試。** 同一批請求可以在
[LoadDensity](https://github.com/Integration-Automation/LoadDensity)(Locust)上跑負載測試。
`AT_test_api_method` 與 `AT_test_api_method_httpx` action,或存下報告裡錄到的流量,會變成 LoadDensity 的
HTTP task:URL、method、`params`、`headers`、`cookies`、`json`、`data`、`timeout`、`allow_redirects` 與
`verify` 原樣帶過去,`result_check_dict["status_code"]` 變成狀態碼斷言。其他 action 與相對網址會被略過並列出。
`load run` 在獨立行程啟動 LoadDensity(`python -m je_load_density --execute_file`),並依它的摘要判斷結果:
沒有任何請求、失敗率超過 `--max-failure-rate` 或 p95 超過 `--max-p95-ms` 時結束碼為 1。

```bash
pip install je_load_density            # 裝在這個直譯器,或用 --python 指定另一個
apitestka load convert --actions smoke.json -o load.json --users 20 --time 30
apitestka load run --actions smoke.json --users 20 --spawn-rate 5 --time 30 \
    --max-failure-rate 0.01 --max-p95-ms 500
apitestka load run --report run_success.json --time 60 --python /opt/ld/bin/python
```

JSON action:`AT_write_load_test` 寫出 LoadDensity 檔案;`AT_run_load_test` 執行它,超過門檻時該 action 失敗。

```json
["AT_run_load_test", {"action_file": "smoke.json", "profile": {"user_count": 20, "test_time": 30},
                      "thresholds": {"max_failure_rate": 0.01, "max_p95_ms": 500}}]
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
apitestka openapi --report run_success.json -o openapi.json   # 從存下的執行結果反推規格
apitestka openapi --run actions.json    # 先執行再印出反推的規格
apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000   # 見契約測試
apitestka generate-tests openapi.json -o actions.json [--ai anthropic]         # 見可插拔 AI 後端
apitestka load run --actions smoke.json --users 20 --time 30                    # 見生態整合
apitestka trend check                                                           # 見報告與可觀測性
apitestka spec check openapi.json --run tests/ --min-coverage 0.8               # 見測試即規格迴路
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
from je_api_testka.spec import (
    infer_schema, records_to_openapi, build_openapi, export_openapi, load_report_records, openapi_changelog,
)

records_to_openapi(title="Recovered", version="0.1.0")   # 從記憶體中的測試紀錄
build_openapi(["run_success.json"])                  # 測試紀錄加上存下的 JSON 報告
export_openapi("openapi.json", ["run_success.json"]) # 同上,並寫成 UTF-8 JSON
openapi_changelog(prev_spec, current_spec)           # markdown changelog
```

同一個 method 與路徑的紀錄會合併成一個 operation:每個出現過的狀態碼各有一筆 response,
查詢參數名稱變成 `in: query` 參數,JSON 或文字內容變成回應與請求內容的 schema。
存下的報告是 `generate_json_report` 產生的 `<name>_success.json`;`AT_export_openapi`
指令與 `apitestka openapi` 也讀得到它。

### 測試即規格迴路

`apitestka spec check` 讓已提交的 OpenAPI 文件與測試保持一致。它先執行測試(或讀存下的報告),再做三件事:

- **偏移**:每個錄下的請求都用契約互動的方式和文件比對(operation、查詢參數、請求內容、宣告的狀態碼、回應 schema);
  打到文件沒宣告的 operation 會列為未文件化。
- **覆蓋率**:列出沒有任何測試碰到的已文件化 operation;`--min-coverage` 在低於比例時讓執行失敗。
- **補上缺口**:`--missing-actions` 為沒測到的 operation 寫出 action(有設 AI backend 時用它,否則用文件裡的範例
  產生確定性的請求)。`--inferred-spec` 寫出測試描述出來的文件,路徑會歸到已提交的樣板底下
  (`/items/7` → `/items/{id}`)。

有未文件化的 operation、偏移問題或覆蓋率不足時結束碼為 1。JSON action:`AT_check_spec_against_tests`
(失敗時該 action 會帶著報告失敗)。

```bash
apitestka spec check openapi.json --run tests/ --min-coverage 0.8 \
    --missing-actions tests/generated.json --inferred-spec build/openapi.inferred.json
```

```python
from je_api_testka.spec.spec_loop import check_records_against_spec, missing_test_actions, infer_spec_from_tests

report = check_records_against_spec(records, committed_spec)   # records:這次執行的成功紀錄
report.coverage, report.uncovered, report.undocumented, report.problems
actions = missing_test_actions(committed_spec, report)
```

### 契約測試

Pact 風格的雙向消費者契約(`je_api_testka.contract`)。消費端的測試執行會變成 Pact v2 檔案格式的
契約,可以直接送到 Pact Broker 或 Pactflow。回應內容預設帶 `type` 比對規則:提供端必須回傳相同的
結構與值的型別,而不是相同的值。契約接著從兩邊檢查:

- **提供端驗證**:把每個互動重播到執行中的提供端,檢查狀態碼相同、契約列出的 header 都在
  (`Content-Type` 只比 media type)、內容符合比對規則(`type`、`regex`、`min`;物件可以多帶欄位)。
  提供端狀態(`providerState`)透過 Python 函式或設定 URL 建立,設定 URL 會收到
  `{"consumer": ..., "state": ...}`。
- **雙向檢查**:不用啟動提供端,直接把契約和提供端的 OpenAPI 文件比對:operation 存在(路徑樣板可比對)、
  查詢參數有宣告且必填的有送、請求內容符合 schema、狀態碼有宣告(完全相同、`2XX` 或 `default`)、
  回應內容符合 schema(`$ref`、`allOf` / `anyOf` / `oneOf`、`nullable`)。提供端用自己的測試執行
  維持 OpenAPI 文件正確,例如用 `apitestka openapi`。

```python
from je_api_testka.contract import write_contract, verify_contract, check_contract_against_openapi

# 消費端:測試執行(目前紀錄加上存下的報告)變成契約
write_contract("pacts/web-shop.json", consumer="web", provider="shop", report_paths=["run_success.json"])
# 提供端:把契約重播到執行中的提供端
verify_contract("pacts/web-shop.json", base_url="http://localhost:8000")
# 雙向:不用提供端,直接和它的 OpenAPI 文件比對
check_contract_against_openapi("pacts/web-shop.json", "openapi.json")
```

```bash
apitestka contract record --report run_success.json --consumer web --provider shop -o pacts/web-shop.json
apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000
apitestka contract compare pacts/web-shop.json openapi.json
```

`verify` 與 `compare` 會印出報告(`--json` 輸出 JSON),契約不成立時結束碼為 1。JSON action:
`AT_write_contract`、`AT_verify_contract`、`AT_check_contract_against_openapi`(後兩者失敗時該 action
會帶著報告失敗)。

### GUI

```bash
pip install 'je_api_testka[gui]'
```

`je_api_testka.gui.*` 子模組(`history_panel`、`env_manager_model`、`diff_viewer`)內的
headless model(`HistoryPanelModel`、`EnvManagerModel`、`render_side_by_side`)讓測試與
headless 工具不需 PySide6 也能驅動面板。
真正的 Qt widget 在 `main_widget.py`。

語系:English、繁體中文、简体中文、日本語。透過 `LanguageWrapper.reset_language(...)` 切換。

### 可插拔 AI 後端

有三個工具會詢問語言模型:`generate_tests_from_openapi`(為每個 operation 產生 action)、
`generate_fake_payload`(產生符合 JSON Schema 的值)與 `classify_failures`(替規則分不出來的錯誤貼標籤)。
預設 `NoOpAIBackend` 不會碰網路,各工具會改用確定性的 fallback;回覆是空的或無法使用時也一樣
(產生的 action 必須是 `["AT_...", {...}]` 組成的 JSON list)。

`AnthropicAIBackend`(`ai` extra)是用 Anthropic API 的參考實作。憑證取自 `anthropic` SDK 讀的環境
(`ANTHROPIC_API_KEY` 或 `ant auth login` 設定檔),不會保存金鑰。預設模型是 `claude-opus-5-5`,並明確送出
effort `medium`。伺服器端的拒答 fallback 預設開啟(`fallbacks="default"`),傳 `fallbacks=None` 可關閉。
遇到拒答、回覆被截斷、速率限制、伺服器錯誤或網路失敗時會改用確定性 fallback;請求被拒(金鑰錯誤、
未知模型)則丟出 `APIAIBackendException`。

```python
from je_api_testka.ai import AnthropicAIBackend, set_ai_backend, generate_tests_from_openapi

set_ai_backend(AnthropicAIBackend())                   # claude-opus-5-5, effort "medium"
set_ai_backend(AnthropicAIBackend(model="claude-sonnet-5-5", effort="low", timeout=60))
actions = generate_tests_from_openapi(my_openapi_spec)
```

選擇 backend 的方式:`set_ai_backend(...)`、`select_ai_backend("anthropic", model=..., effort=...)`、
`AT_select_ai_backend` action,或環境變數:沒有明確選擇時,第一次使用會讀 `APITESTKA_AI_BACKEND`
(`noop` 或 `anthropic`)、`APITESTKA_AI_MODEL` 與 `APITESTKA_AI_EFFORT`。

```bash
pip install 'je_api_testka[ai]'
export ANTHROPIC_API_KEY=...                            # or an `ant auth login` profile
apitestka generate-tests openapi.json -o actions.json --ai anthropic --effort high
APITESTKA_AI_BACKEND=anthropic apitestka mcp            # any entry point, no code changes
```

其他 provider 也用同樣方式接上:繼承 `AIBackend` 並實作 `complete(prompt, *, context)`。

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
| `apitestka_records_to_openapi` | 從測試紀錄或存下的報告(`report_paths`)反推 OpenAPI 文件 |
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
├── contract/                # Pact 風格消費者契約、提供端驗證、OpenAPI 比對
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
pip install 'je_api_testka[grpc]'
pip install 'je_api_testka[ai]'
pip install 'je_api_testka[schema]'
pip install 'je_api_testka[security]'
pip install 'je_api_testka[otel]'
pip install 'je_api_testka[mcp]'
pip install 'je_api_testka[gui]'
```

---

## 開發

```bash
git clone https://github.com/Integration-Automation/APITestka.git
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

- **首頁:** https://github.com/Integration-Automation/APITestka
- **文件:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
- **MCP:** https://modelcontextprotocol.io/
