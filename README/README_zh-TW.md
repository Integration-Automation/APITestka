# APITestka

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](../licenses/APITestka_LICENSE)
[![PyPI](https://img.shields.io/pypi/v/je_api_testka.svg)](https://pypi.org/project/je_api_testka/)
[![Documentation Status](https://readthedocs.org/projects/apitestka/badge/?version=latest)](https://apitestka.readthedocs.io/en/latest/?badge=latest)

**APITestka** 是一個輕量級、跨平台的自動化 API 測試框架。
支援 HTTP/HTTPS、SOAP/XML 和 JSON，具備高效能的請求執行、
詳細的報告產生功能，以及靈活的 CLI 腳本支援。

APITestka 專為速度與擴展性而設計，每秒可執行數千次請求，
整合了模擬伺服器與遠端自動化功能，
並可產生多種格式的報告以便於分析。

> **其他語言：**
> [English](../README.md) | [简体中文](README_zh-CN.md)

---

## 目錄

- [功能特色](#功能特色)
- [架構概覽](#架構概覽)
- [安裝](#安裝)
- [快速開始](#快速開始)
  - [使用 requests 後端](#使用-requests-後端)
  - [使用 httpx 後端（同步）](#使用-httpx-後端同步)
  - [使用 httpx 後端（非同步）](#使用-httpx-後端非同步)
  - [HTTP/2 支援](#http2-支援)
  - [SOAP/XML 請求](#soapxml-請求)
  - [Session 持久化請求](#session-持久化請求)
- [結果斷言](#結果斷言)
- [報告產生](#報告產生)
  - [HTML 報告](#html-報告)
  - [JSON 報告](#json-報告)
  - [XML 報告](#xml-報告)
- [模擬伺服器](#模擬伺服器)
- [回呼執行器](#回呼執行器)
- [腳本化執行器](#腳本化執行器)
  - [JSON 關鍵字驅動測試](#json-關鍵字驅動測試)
  - [透過 Python 執行 JSON 檔案](#透過-python-執行-json-檔案)
  - [執行整個目錄的 JSON 檔案](#執行整個目錄的-json-檔案)
  - [新增自訂命令](#新增自訂命令)
- [CLI 使用方式](#cli-使用方式)
- [遠端自動化（Socket 伺服器）](#遠端自動化socket-伺服器)
- [專案腳手架](#專案腳手架)
- [GUI（選用）](#gui選用)
- [測試紀錄](#測試紀錄)
- [專案結構](#專案結構)
- [系統需求](#系統需求)
- [開發](#開發)
- [貢獻](#貢獻)
- [授權](#授權)
- [連結](#連結)

---

## 功能特色

| 類別 | 說明 |
|---|---|
| **HTTP 用戶端** | `requests`（同步、支援 Session）與 `httpx`（同步 + 非同步、HTTP/2） |
| **協定** | HTTP、HTTPS、SOAP/XML、JSON |
| **報告格式** | HTML、JSON、XML |
| **腳本化** | 透過 Executor 進行 JSON 關鍵字驅動測試執行 |
| **模擬伺服器** | 內建基於 Flask 的模擬伺服器，用於本地測試 |
| **遠端自動化** | TCP Socket 伺服器，支援遠端命令執行 |
| **斷言** | 內建回應欄位斷言（狀態碼、標頭、內容等） |
| **回呼系統** | API 呼叫完成後執行回呼函式 |
| **CLI** | 完整的命令列介面，支援 CI/CD 整合 |
| **專案腳手架** | 自動產生專案結構與範本 |
| **GUI** | 選用的 PySide6 GUI（透過 `pip install je_api_testka[gui]` 安裝） |
| **跨平台** | Windows、macOS、Linux |
| **效能** | 每秒可執行數千次請求 |

---

## 架構概覽

```
je_api_testka/
├── requests_wrapper/      # 基於 requests 的 HTTP 用戶端
├── httpx_wrapper/         # 基於 httpx 的 HTTP 用戶端（同步 + 非同步）
├── utils/
│   ├── assert_result/     # 回應斷言
│   ├── callback/          # 回呼函式執行器
│   ├── executor/          # JSON 關鍵字驅動的動作執行器
│   ├── generate_report/   # HTML / JSON / XML 報告產生
│   ├── mock_server/       # 基於 Flask 的模擬伺服器
│   ├── socket_server/     # TCP Socket 伺服器（遠端自動化）
│   ├── project/           # 專案腳手架與範本
│   ├── json/              # JSON 讀寫工具
│   ├── xml/               # XML 解析/轉換工具
│   ├── test_record/       # 全域測試紀錄儲存
│   ├── logging/           # 日誌實例
│   ├── file_process/      # 檔案列表工具
│   ├── package_manager/   # 動態載入套件
│   └── exception/         # 自訂例外
└── gui/                   # 選用的 PySide6 GUI
```

---

## 安裝

```bash
pip install je_api_testka
```

安裝 GUI 支援：

```bash
pip install je_api_testka[gui]
```

---

## 快速開始

### 使用 requests 後端

```python
from je_api_testka import test_api_method_requests

# GET 請求
result = test_api_method_requests("get", "http://httpbin.org/get")
print(result["response_data"]["status_code"])  # 200

# POST 請求，帶參數
result = test_api_method_requests(
    "post",
    "http://httpbin.org/post",
    params={"task": "new task"}
)
print(result["response_data"]["status_code"])  # 200
```

### 使用 httpx 後端（同步）

```python
from je_api_testka import test_api_method_httpx

result = test_api_method_httpx("get", "http://httpbin.org/get")
print(result["response_data"]["status_code"])  # 200
```

### 使用 httpx 後端（非同步）

```python
import asyncio
from je_api_testka import test_api_method_httpx_async

async def main():
    result = await test_api_method_httpx_async("get", "http://httpbin.org/get")
    print(result["response_data"]["status_code"])  # 200

asyncio.run(main())
```

### HTTP/2 支援

```python
import asyncio
from je_api_testka import test_api_method_httpx_async

async def main():
    result = await test_api_method_httpx_async(
        "get",
        "https://httpbin.org/get",
        http2=True
    )
    print(result["response_data"]["status_code"])

asyncio.run(main())
```

### SOAP/XML 請求

```python
from je_api_testka import test_api_method_requests

result = test_api_method_requests(
    "post",
    "http://example.com/soap-endpoint",
    soap=True,
    data='<soap:Envelope>...</soap:Envelope>'
)
```

當 `soap=True` 時，`Content-Type` 標頭會自動設定為 `application/soap+xml`。

### Session 持久化請求

`requests` 後端支援 Session 方法，用於持久化連線（cookies、驗證等）：

```python
from je_api_testka import test_api_method_requests

# 可用方法：session_get, session_post, session_put, session_patch, session_delete, session_head, session_options
result = test_api_method_requests("session_get", "http://httpbin.org/get")
```

---

## 結果斷言

傳入 `result_check_dict` 可自動斷言回應欄位：

```python
from je_api_testka import test_api_method_requests

# 若 status_code 不是 200，將拋出 APIAssertException
test_api_method_requests(
    "get",
    "http://httpbin.org/get",
    result_check_dict={"status_code": 200}
)
```

可斷言的回應資料欄位：`status_code`、`text`、`content`、`headers`、`cookies`、`encoding`、`elapsed`、`request_time_sec`、`request_method`、`request_url`、`request_body`、`start_time`、`end_time`。

---

## 報告產生

報告從全域的 `test_record_instance` 產生，所有測試結果會自動記錄。

### HTML 報告

```python
from je_api_testka import test_api_method_requests, generate_html_report

test_api_method_requests("get", "http://httpbin.org/get")
test_api_method_requests("post", "http://httpbin.org/post")

# 產生 "my_report.html"，包含成功/失敗表格
generate_html_report("my_report")
```

### JSON 報告

```python
from je_api_testka import test_api_method_requests, generate_json_report

test_api_method_requests("get", "http://httpbin.org/get")

# 產生 "my_report_success.json" 和 "my_report_failure.json"
generate_json_report("my_report")
```

### XML 報告

```python
from je_api_testka import test_api_method_requests, generate_xml_report

test_api_method_requests("get", "http://httpbin.org/get")

# 產生 "my_report_success.xml" 和 "my_report_failure.xml"
generate_xml_report("my_report")
```

---

## 模擬伺服器

APITestka 內建基於 Flask 的模擬伺服器，用於本地測試：

```python
from je_api_testka import flask_mock_server_instance, request

# 新增自訂路由
def my_endpoint():
    return {"message": "hello", "params": dict(request.args)}

flask_mock_server_instance.add_router(
    {"/api/test": my_endpoint},
    methods=["GET", "POST"]
)

# 啟動模擬伺服器（預設：localhost:8090）
flask_mock_server_instance.start_mock_server()
```

也可以建立自訂 host/port 的新實例：

```python
from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

server = FlaskMockServer("0.0.0.0", 5000)
server.add_router({"/health": lambda: "OK"}, methods=["GET"])
server.start_mock_server()
```

---

## 回呼執行器

在 API 測試完成後執行回呼函式：

```python
from je_api_testka import callback_executor

def my_callback(message):
    print(f"回呼：{message}")

callback_executor.callback_function(
    trigger_function_name="AT_test_api_method",
    callback_function=my_callback,
    callback_function_param={"message": "測試完成！"},
    callback_param_method="kwargs",
    http_method="get",
    test_url="http://httpbin.org/get"
)
```

---

## 腳本化執行器

Executor 實現了 JSON 關鍵字驅動測試，測試動作以 JSON 陣列定義，並透過程式化方式執行。

### JSON 關鍵字驅動測試

建立一個 JSON 檔案（例如 `test_actions.json`）：

```json
{
    "api_testka": [
        ["AT_test_api_method", {
            "http_method": "get",
            "test_url": "http://httpbin.org/get",
            "result_check_dict": {"status_code": 200}
        }],
        ["AT_test_api_method", {
            "http_method": "post",
            "test_url": "http://httpbin.org/post",
            "params": {"task": "new task"},
            "result_check_dict": {"status_code": 200}
        }]
    ]
}
```

### 透過 Python 執行 JSON 檔案

```python
from je_api_testka import execute_action, read_action_json

execute_action(read_action_json("test_actions.json"))
```

### 執行整個目錄的 JSON 檔案

```python
from je_api_testka import execute_files, get_dir_files_as_list

execute_files(get_dir_files_as_list("path/to/json_dir"))
```

### 新增自訂命令

```python
from je_api_testka import add_command_to_executor, execute_action

def my_custom_function(url):
    print(f"自訂測試：{url}")

add_command_to_executor({"my_test": my_custom_function})

execute_action([
    ["my_test", ["http://example.com"]]
])
```

**內建的 Executor 命令：**

| 命令 | 說明 |
|---|---|
| `AT_test_api_method` | 使用 requests 後端測試 API |
| `AT_test_api_method_httpx` | 使用 httpx 同步後端測試 API |
| `AT_delegate_async_httpx` | 使用 httpx 非同步後端測試 API（同步呼叫） |
| `AT_generate_html` | 產生 HTML 報告資料 |
| `AT_generate_html_report` | 產生 HTML 報告檔案 |
| `AT_generate_json` | 產生 JSON 報告資料 |
| `AT_generate_json_report` | 產生 JSON 報告檔案 |
| `AT_generate_xml` | 產生 XML 報告資料 |
| `AT_generate_xml_report` | 產生 XML 報告檔案 |
| `AT_execute_action` | 執行巢狀動作列表 |
| `AT_execute_files` | 從多個檔案執行動作 |
| `AT_add_package_to_executor` | 動態載入套件到執行器 |
| `AT_add_package_to_callback_executor` | 動態載入套件到回呼執行器 |
| `AT_flask_mock_server_add_router` | 新增路由到模擬伺服器 |
| `AT_start_flask_mock_server` | 啟動模擬伺服器 |

---

## CLI 使用方式

APITestka 提供完整的 CLI 介面：

```bash
# 執行單一 JSON 動作檔案
python -m je_api_testka -e test_actions.json

# 執行目錄中所有 JSON 檔案
python -m je_api_testka -d path/to/json_dir

# 直接執行 JSON 字串
python -m je_api_testka --execute_str '[["AT_test_api_method", {"http_method": "get", "test_url": "http://httpbin.org/get"}]]'

# 建立新專案（含範本）
python -m je_api_testka -c MyProject
```

| 參數 | 說明 |
|---|---|
| `-e`, `--execute_file` | 執行單一 JSON 動作檔案 |
| `-d`, `--execute_dir` | 執行目錄中所有 JSON 檔案 |
| `--execute_str` | 直接執行 JSON 字串 |
| `-c`, `--create_project` | 建立專案目錄及範本檔案 |

---

## 遠端自動化（Socket 伺服器）

APITestka 內建 TCP Socket 伺服器，用於遠端命令執行：

```python
from je_api_testka import start_apitestka_socket_server

# 啟動 Socket 伺服器（預設：localhost:9939）
server = start_apitestka_socket_server(host="localhost", port=9939)
```

用戶端可透過 TCP 傳送 JSON 格式的動作列表，伺服器會執行並回傳結果。傳送 `quit_server` 可關閉伺服器。

也支援 CLI 參數：

```bash
python -m je_api_testka.utils.socket_server.api_testka_socket_server localhost 9939
```

---

## 專案腳手架

產生含有關鍵字與執行器範本的專案結構：

```python
from je_api_testka import create_project_dir

create_project_dir(project_path=".", parent_name="MyAPIProject")
```

產生的結構如下：

```
MyAPIProject/
├── keyword/
│   ├── keyword1.json          # 範例關鍵字測試（POST）
│   ├── keyword2.json          # 範例關鍵字測試（GET）
│   └── bad_keyword_1.json     # 含套件載入的範例
└── executor/
    ├── executor_one_file.py   # 執行單一關鍵字檔案
    ├── executor_folder.py     # 執行目錄中所有關鍵字檔案
    └── executor_bad_file.py   # 含動態套件載入的範例
```

---

## GUI（選用）

APITestka 提供選用的 PySide6 圖形使用者介面：

```bash
pip install je_api_testka[gui]
```

GUI 需要 PySide6 6.11.0 及 qt-material。

---

## 測試紀錄

所有 API 測試結果會自動儲存在全域的 `test_record_instance` 中：

```python
from je_api_testka import test_api_method_requests, test_record_instance

test_api_method_requests("get", "http://httpbin.org/get")
test_api_method_requests("get", "http://invalid-url")

# 取得成功的測試紀錄
print(len(test_record_instance.test_record_list))

# 取得錯誤紀錄
print(len(test_record_instance.error_record_list))

# 清除所有紀錄
test_record_instance.clean_record()
```

每筆成功紀錄包含：`status_code`、`text`、`content`、`headers`、`history`、`encoding`、`cookies`、`elapsed`、`request_time_sec`、`request_method`、`request_url`、`request_body`、`start_time`、`end_time`。

---

## 專案結構

```
APITestka/
├── je_api_testka/             # 主要套件
│   ├── __init__.py            # 公開 API 匯出
│   ├── __main__.py            # CLI 進入點
│   ├── requests_wrapper/      # requests HTTP 用戶端封裝
│   ├── httpx_wrapper/         # httpx HTTP 用戶端封裝（同步 + 非同步）
│   ├── utils/                 # 工具模組
│   └── gui/                   # 選用的 PySide6 GUI
├── test/                      # 測試套件
│   ├── test_requests/         # requests 後端測試
│   ├── test_httpx_sync/       # httpx 同步後端測試
│   ├── test_httpx_async/      # httpx 非同步後端測試
│   └── test_utils/            # 工具模組測試
├── docs/                      # Sphinx 文件原始碼
├── apitestka_driver/          # 獨立驅動程式執行檔
├── licenses/                  # 授權檔案
├── pyproject.toml             # 建置設定
├── requirements.txt           # 執行時依賴
└── dev_requirements.txt       # 開發依賴
```

---

## 系統需求

- **Python** 3.10 或更高版本
- **依賴套件：** `requests`、`Flask`、`httpx`
- **選用（GUI）：** `PySide6==6.11.0`、`qt-material`

---

## 開發

```bash
# 複製儲存庫
git clone https://github.com/Intergration-Automation-Testing/APITestka.git
cd APITestka

# 安裝開發依賴
pip install -r dev_requirements.txt

# 執行測試
pytest
```

---

## 貢獻

請參閱 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解貢獻指南。

---

## 授權

本專案使用 MIT 授權條款。詳見 [licenses/APITestka_LICENSE](../licenses/APITestka_LICENSE)。

---

## 連結

- **首頁：** https://github.com/Intergration-Automation-Testing/APITestka
- **文件：** https://apitestka.readthedocs.io/en/latest/
- **PyPI：** https://pypi.org/project/je_api_testka/
