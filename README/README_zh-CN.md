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
  - [测试即规格回路](#测试即规格回路)
  - [契约测试](#契约测试)
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
| **模拟服务器** | 静态、动态、stateful、故障注入、OpenAPI 驱动、Jinja 模板、Webhook 接收、record-replay 代理、WebSocket 与 gRPC 端点 |
| **Runner** | 顺序与并行、Tag 过滤、Dependency-aware 排序、Retry 策略 |
| **报告** | HTML / JSON / XML / **JUnit / Allure / Markdown** / shields.io badge / SQLite 趋势库 / Run diff / 各端点延迟趋势与异常检测 |
| **生态集成** | Slack / Teams / Discord webhook、GitHub PR comment、cURL & HAR 导入、OpenAPI / Postman 导入、LoadDensity 负载测试桥接 |
| **CLI / DX** | 子命令式 CLI、REPL、终端摘要、Shell completion、Scaffold |
| **安全** | Auth helper(Basic / Bearer / JWT / AWS SigV4)、Header / CORS / Rate limit / SSRF probe、pip-audit、Fuzz |
| **Spec 反推** | 测试记录 → OpenAPI、JSON Schema 推断、OpenAPI changelog、测试即规格回路(偏移、覆盖率、为缺口生成测试) |
| **契约测试** | 从测试运行生成 Pact v2 消费者契约、提供端验证、与 OpenAPI 双向比较 |
| **AI** | 可插拔后端,LLM 不可用时自动回退到确定性 fallback;附 Anthropic 参考实现 |
| **MCP** | 一级支持 Claude Code,将框架作为 MCP 工具暴露 |
| **GUI** | 可选 PySide6 GUI:每个功能一页的侧边栏、附历史与环境的请求构建器、浅色与深色主题、英 / 繁中 / 简中 / 日、嵌入 Swagger UI |
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

### 断言、Diff 与 SLA

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
assert_sla(sla={"max_ms": 2000})   # 目前录下的运行;JSON:["AT_assert_sla", {"sla": {...}}]
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
apitestka mock --config mock.json       # HTTP routes 再加上 WebSocket 与 gRPC 端点
```

**WebSocket 与 gRPC 端点。** `WebSocketMockServer`(`websocket` extra)提供按脚本响应的路由:
连接时发送问候、已知消息查回复表、其他消息走 fallback(`{{message}}` 会回声,`null` 不响应)。
`GrpcStubServer`(`grpc` extra)不需要编译 stub,直接用完整路径提供方法:固定的 unary 响应、
server stream,或返回某个状态码的错误。payload 是原始 bytes,所以序列化好的 protobuf 可以给
生成出来的 client 使用;`str` 以 UTF-8 发送,其他 JSON 值以紧凑 JSON 发送。两者都会保留收到的内容
供断言使用,未知的 WebSocket 路径会以 HTTP 404 拒绝。

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

`--config` 文件可以描述三种端点,每一段都可以省略:

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

JSON action 也能操作同样的 mock:`AT_mock_start_websocket_server` / `AT_mock_start_grpc_server`
(`routes` / `methods` 使用上面的配置格式)、`AT_mock_websocket_received` / `AT_mock_grpc_received`,
以及 `AT_mock_stop_websocket_server` / `AT_mock_stop_grpc_server`。

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

**响应时间趋势与异常检测。** `record_endpoint_latencies` 把每次运行各端点的延迟(次数、平均、p50、p95、
最大值)存进趋势数据库。端点是 method 加上路径模板:有 OpenAPI 时用它的模板,否则把路径里的标识符泛化
(`/items/42` → `/items/{id}`)。`detect_latency_anomalies` 拿最近一次运行的每个端点,与它之前几次运行
(默认 20 次、至少 5 次)的中位数与 MAD 比较;变慢至少 20 % 且 5 ms、并且 robust z-score 超过 3.5 才算异常,
这些都可以调整。`generate_trend_report` 写出每个端点附 sparkline 的 HTML 表格。JSON action:
`AT_record_endpoint_latencies`、`AT_detect_latency_anomalies`、`AT_assert_no_latency_anomalies`、
`AT_generate_trend_report`。

```python
from je_api_testka.utils.generate_report.latency_trends import (
    record_endpoint_latencies, detect_latency_anomalies, assert_no_latency_anomalies,
)
from je_api_testka.utils.generate_report.trend_report import generate_trend_report

record_endpoint_latencies("trend.sqlite", run_label="build-128")   # 每次运行后
assert_no_latency_anomalies("trend.sqlite", {"metric": "p95_ms", "threshold": 3.5})
generate_trend_report("trends.html", "trend.sqlite")
```

```bash
apitestka trend record --report run_success.json --label build-128 --openapi openapi.json
apitestka trend check            # 有异常时退出码为 1
apitestka trend report -o trends.html
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

每个导入工具都返回 `["AT_test_api_method", {...}]` 形式的 action,`execute_action`
可以直接执行。runner 的元数据(`id`、`depends_on`、`tags`)可以留在 kwargs 里,
executor 调用前会先去掉。

**用 LoadDensity 做负载测试。** 同一批请求可以在
[LoadDensity](https://github.com/Integration-Automation/LoadDensity)(Locust)上运行负载测试。
`AT_test_api_method` 与 `AT_test_api_method_httpx` action,或保存报告里录到的流量,会变成 LoadDensity 的
HTTP task:URL、method、`params`、`headers`、`cookies`、`json`、`data`、`timeout`、`allow_redirects` 与
`verify` 原样带过去,`result_check_dict["status_code"]` 变成状态码断言。其他 action 与相对网址会被跳过并列出。
`load run` 在独立进程启动 LoadDensity(`python -m je_load_density --execute_file`),并根据它的摘要判断结果:
没有任何请求、失败率超过 `--max-failure-rate` 或 p95 超过 `--max-p95-ms` 时退出码为 1。

```bash
pip install je_load_density            # 装在这个解释器,或用 --python 指定另一个
apitestka load convert --actions smoke.json -o load.json --users 20 --time 30
apitestka load run --actions smoke.json --users 20 --spawn-rate 5 --time 30 \
    --max-failure-rate 0.01 --max-p95-ms 500
apitestka load run --report run_success.json --time 60 --python /opt/ld/bin/python
```

JSON action:`AT_write_load_test` 写出 LoadDensity 文件;`AT_run_load_test` 执行它,超过阈值时该 action 失败。

```json
["AT_run_load_test", {"action_file": "smoke.json", "profile": {"user_count": 20, "test_time": 30},
                      "thresholds": {"max_failure_rate": 0.01, "max_p95_ms": 500}}]
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
apitestka openapi --report run_success.json -o openapi.json   # 从保存的运行结果反推规格
apitestka openapi --run actions.json    # 先运行再打印反推的规格
apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000   # 见契约测试
apitestka generate-tests openapi.json -o actions.json [--ai anthropic]         # 见可插拔 AI 后端
apitestka load run --actions smoke.json --users 20 --time 30                    # 见生态集成
apitestka trend check                                                           # 见报告与可观测性
apitestka spec check openapi.json --run tests/ --min-coverage 0.8               # 见测试即规格回路
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
from je_api_testka.spec import (
    infer_schema, records_to_openapi, build_openapi, export_openapi, load_report_records, openapi_changelog,
)

records_to_openapi(title="Recovered", version="0.1.0")   # 从内存中的测试记录
build_openapi(["run_success.json"])                  # 测试记录加上保存的 JSON 报告
export_openapi("openapi.json", ["run_success.json"]) # 同上,并写成 UTF-8 JSON
openapi_changelog(prev_spec, current_spec)           # markdown changelog
```

同一个 method 与路径的记录会合并成一个 operation:每个出现过的状态码各有一条 response,
查询参数名称变成 `in: query` 参数,JSON 或文本内容变成响应与请求体的 schema。
保存的报告是 `generate_json_report` 生成的 `<name>_success.json`;`AT_export_openapi`
命令与 `apitestka openapi` 也能读取它。

### 测试即规格回路

`apitestka spec check` 让已提交的 OpenAPI 文档与测试保持一致。它先运行测试(或读取保存的报告),再做三件事:

- **偏移**:每个录下的请求都按契约交互的方式与文档比较(operation、查询参数、请求体、声明的状态码、响应 schema);
  请求了文档没声明的 operation 会列为未文档化。
- **覆盖率**:列出没有任何测试访问到的已文档化 operation;`--min-coverage` 在低于比例时让运行失败。
- **补上缺口**:`--missing-actions` 为没测到的 operation 写出 action(设置了 AI backend 时用它,否则用文档里的示例
  生成确定性的请求)。`--inferred-spec` 写出测试描述出来的文档,路径会归到已提交的模板下
  (`/items/7` → `/items/{id}`)。

有未文档化的 operation、偏移问题或覆盖率不足时退出码为 1。JSON action:`AT_check_spec_against_tests`
(失败时该 action 会带着报告失败)。

```bash
apitestka spec check openapi.json --run tests/ --min-coverage 0.8 \
    --missing-actions tests/generated.json --inferred-spec build/openapi.inferred.json
```

```python
from je_api_testka.spec.spec_loop import check_records_against_spec, missing_test_actions, infer_spec_from_tests

report = check_records_against_spec(records, committed_spec)   # records:本次运行的成功记录
report.coverage, report.uncovered, report.undocumented, report.problems
actions = missing_test_actions(committed_spec, report)
```

### 契约测试

Pact 风格的双向消费者契约(`je_api_testka.contract`)。消费端的测试运行会变成 Pact v2 文件格式的
契约,可以直接发送到 Pact Broker 或 Pactflow。响应体默认带 `type` 匹配规则:提供端必须返回相同的
结构与值的类型,而不是相同的值。契约接着从两边检查:

- **提供端验证**:把每个交互重放到运行中的提供端,检查状态码相同、契约列出的 header 都存在
  (`Content-Type` 只比较 media type)、响应体符合匹配规则(`type`、`regex`、`min`;对象可以多带字段)。
  提供端状态(`providerState`)通过 Python 函数或设置 URL 建立,设置 URL 会收到
  `{"consumer": ..., "state": ...}`。
- **双向检查**:不用启动提供端,直接把契约和提供端的 OpenAPI 文档比较:operation 存在(路径模板可匹配)、
  查询参数已声明且必填的已发送、请求体符合 schema、状态码已声明(完全相同、`2XX` 或 `default`)、
  响应体符合 schema(`$ref`、`allOf` / `anyOf` / `oneOf`、`nullable`)。提供端用自己的测试运行
  保持 OpenAPI 文档正确,例如用 `apitestka openapi`。

```python
from je_api_testka.contract import write_contract, verify_contract, check_contract_against_openapi

# 消费端:测试运行(当前记录加上保存的报告)变成契约
write_contract("pacts/web-shop.json", consumer="web", provider="shop", report_paths=["run_success.json"])
# 提供端:把契约重放到运行中的提供端
verify_contract("pacts/web-shop.json", base_url="http://localhost:8000")
# 双向:不用提供端,直接和它的 OpenAPI 文档比较
check_contract_against_openapi("pacts/web-shop.json", "openapi.json")
```

```bash
apitestka contract record --report run_success.json --consumer web --provider shop -o pacts/web-shop.json
apitestka contract verify pacts/web-shop.json --base-url http://localhost:8000
apitestka contract compare pacts/web-shop.json openapi.json
```

`verify` 与 `compare` 会打印报告(`--json` 输出 JSON),契约不成立时退出码为 1。JSON action:
`AT_write_contract`、`AT_verify_contract`、`AT_check_contract_against_openapi`(后两者失败时该 action
会带着报告失败)。

### GUI

```bash
pip install 'je_api_testka[gui]'
python -m je_api_testka.gui.main_window
```

侧边栏通往各功能的页面,下方是控制台:

- **请求**:method、URL、后端与环境在同一行;参数、请求头、请求体、认证与选项放在响应(状态、耗时、大小、格式化后的
  响应体、响应头)旁边,左侧是请求历史。`{{name}}` 占位符会套用启用中环境的值,**复制为 action** 会把请求转成 executor JSON。
- **环境**:具名的变量组,可启用、导入与导出。
- **执行器**:执行输入的 action JSON、文件或文件夹。
- **记录与报告**:以表格展示测试记录与明细、失败列表,并生成 HTML、JSON、XML、JUnit、Markdown 与 Allure 报告。
- **模拟服务器**、**契约**、**OpenAPI**(推导、测试即规格检查、用 AI 后端生成测试)、**负载测试**(LoadDensity)、
  **趋势**(延迟异常与 HTML 报告)与 **工具**(JSON、XML、创建项目)。

窗口有浅色与深色主题(纯 Qt style sheet;**主题** 默认跟随系统),以及 English、繁體中文、简体中文、日本語四种语言。
`je_api_testka.gui.main_widget.APITestkaWidget` 是可嵌入的 widget,PyBreeze 就是嵌入它。页面背后的逻辑
(`request_model`、`history_panel`、`env_manager_model`)不依赖 Qt。

### 可插拔 AI 后端

有三个工具会询问语言模型:`generate_tests_from_openapi`(为每个 operation 生成 action)、
`generate_fake_payload`(生成符合 JSON Schema 的值)与 `classify_failures`(给规则分不出来的错误打标签)。
默认 `NoOpAIBackend` 不会访问网络,各工具会改用确定性的 fallback;回复为空或无法使用时也一样
(生成的 action 必须是 `["AT_...", {...}]` 组成的 JSON list)。

`AnthropicAIBackend`(`ai` extra)是基于 Anthropic API 的参考实现。凭据取自 `anthropic` SDK 读取的环境
(`ANTHROPIC_API_KEY` 或 `ant auth login` 配置文件),不会保存密钥。默认模型是 `claude-opus-5-5`,并显式发送
effort `medium`。服务器端的拒答 fallback 默认开启(`fallbacks="default"`),传 `fallbacks=None` 可关闭。
遇到拒答、回复被截断、速率限制、服务器错误或网络失败时会改用确定性 fallback;请求被拒(密钥错误、
未知模型)则抛出 `APIAIBackendException`。

```python
from je_api_testka.ai import AnthropicAIBackend, set_ai_backend, generate_tests_from_openapi

set_ai_backend(AnthropicAIBackend())                   # claude-opus-5-5, effort "medium"
set_ai_backend(AnthropicAIBackend(model="claude-sonnet-5-5", effort="low", timeout=60))
actions = generate_tests_from_openapi(my_openapi_spec)
```

选择 backend 的方式:`set_ai_backend(...)`、`select_ai_backend("anthropic", model=..., effort=...)`、
`AT_select_ai_backend` action,或环境变量:没有显式选择时,第一次使用会读取 `APITESTKA_AI_BACKEND`
(`noop` 或 `anthropic`)、`APITESTKA_AI_MODEL` 与 `APITESTKA_AI_EFFORT`。

```bash
pip install 'je_api_testka[ai]'
export ANTHROPIC_API_KEY=...                            # or an `ant auth login` profile
apitestka generate-tests openapi.json -o actions.json --ai anthropic --effort high
APITESTKA_AI_BACKEND=anthropic apitestka mcp            # any entry point, no code changes
```

其他 provider 也用同样方式接入:继承 `AIBackend` 并实现 `complete(prompt, *, context)`。

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
| `apitestka_records_to_openapi` | 从测试记录或保存的报告(`report_paths`)反推 OpenAPI 文档 |
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
├── contract/                # Pact 风格消费者契约、提供端验证、OpenAPI 比较
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
pip install 'je_api_testka[grpc]'
pip install 'je_api_testka[ai]'
pip install 'je_api_testka[schema]'
pip install 'je_api_testka[security]'
pip install 'je_api_testka[otel]'
pip install 'je_api_testka[mcp]'
pip install 'je_api_testka[gui]'
```

---

## 开发

```bash
git clone https://github.com/Integration-Automation/APITestka.git
cd APITestka
pip install -r dev_requirements.txt
pytest                     # 整套测试
```

CI 矩阵:Ubuntu / macOS / Windows × Python 3.10–3.14。

GUI widget 测试以 offscreen 模式运行(`QT_QPA_PLATFORM=offscreen`)。Linux 上 Qt 需要几个系统库
(`sudo apt-get install libegl1 libgl1 libx11-6 libxkbcommon0 libfontconfig1 libfreetype6`),本机没装时这些测试会跳过。CI 会安装它们并设置 `APITESTKA_REQUIRE_QT=1`,
让 Qt 加载失败变成错误而不是跳过。

---

## 贡献

请见 [CONTRIBUTING.md](../CONTRIBUTING.md)。每个 commit 必须附带单元测试
(详情见 `CLAUDE.md` 的 *Testing Guidelines* 段)。

---

## 许可证

MIT — 详见 [licenses/APITestka_LICENSE](../licenses/APITestka_LICENSE)。

---

## 链接

- **首页:** https://github.com/Integration-Automation/APITestka
- **文档:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
- **MCP:** https://modelcontextprotocol.io/
