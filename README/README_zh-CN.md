# APITestka

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](../licenses/APITestka_LICENSE)
[![PyPI](https://img.shields.io/pypi/v/je_api_testka.svg)](https://pypi.org/project/je_api_testka/)

**APITestka** 是一个轻量级、跨平台的自动化 API 测试框架。
支持 HTTP/HTTPS、SOAP/XML 和 JSON，具备高性能的请求执行、
详细的报告生成功能，以及灵活的 CLI 脚本支持。

APITestka 专为速度与扩展性而设计，每秒可执行数千次请求，
集成了模拟服务器与远程自动化功能，
并可生成多种格式的报告以便于分析。

> **其他语言：**
> [English](../README.md) | [繁體中文](README_zh-TW.md)

---

## 目录

- [功能特性](#功能特性)
- [架构概览](#架构概览)
- [安装](#安装)
- [快速开始](#快速开始)
  - [使用 requests 后端](#使用-requests-后端)
  - [使用 httpx 后端（同步）](#使用-httpx-后端同步)
  - [使用 httpx 后端（异步）](#使用-httpx-后端异步)
  - [HTTP/2 支持](#http2-支持)
  - [SOAP/XML 请求](#soapxml-请求)
  - [Session 持久化请求](#session-持久化请求)
- [结果断言](#结果断言)
- [报告生成](#报告生成)
  - [HTML 报告](#html-报告)
  - [JSON 报告](#json-报告)
  - [XML 报告](#xml-报告)
- [模拟服务器](#模拟服务器)
- [回调执行器](#回调执行器)
- [脚本化执行器](#脚本化执行器)
  - [JSON 关键字驱动测试](#json-关键字驱动测试)
  - [通过 Python 执行 JSON 文件](#通过-python-执行-json-文件)
  - [执行整个目录的 JSON 文件](#执行整个目录的-json-文件)
  - [添加自定义命令](#添加自定义命令)
- [CLI 使用方式](#cli-使用方式)
- [远程自动化（Socket 服务器）](#远程自动化socket-服务器)
- [项目脚手架](#项目脚手架)
- [GUI（可选）](#gui可选)
- [测试记录](#测试记录)
- [项目结构](#项目结构)
- [系统要求](#系统要求)
- [开发](#开发)
- [贡献](#贡献)
- [许可证](#许可证)
- [链接](#链接)

---

## 功能特性

| 类别 | 说明 |
|---|---|
| **HTTP 客户端** | `requests`（同步、支持 Session）与 `httpx`（同步 + 异步、HTTP/2） |
| **协议** | HTTP、HTTPS、SOAP/XML、JSON |
| **报告格式** | HTML、JSON、XML |
| **脚本化** | 通过 Executor 进行 JSON 关键字驱动测试执行 |
| **模拟服务器** | 内置基于 Flask 的模拟服务器，用于本地测试 |
| **远程自动化** | TCP Socket 服务器，支持远程命令执行 |
| **断言** | 内置响应字段断言（状态码、头部、内容等） |
| **回调系统** | API 调用完成后执行回调函数 |
| **CLI** | 完整的命令行接口，支持 CI/CD 集成 |
| **项目脚手架** | 自动生成项目结构与模板 |
| **GUI** | 可选的 PySide6 GUI（通过 `pip install je_api_testka[gui]` 安装） |
| **跨平台** | Windows、macOS、Linux |
| **性能** | 每秒可执行数千次请求 |

---

## 架构概览

```
je_api_testka/
├── requests_wrapper/      # 基于 requests 的 HTTP 客户端
├── httpx_wrapper/         # 基于 httpx 的 HTTP 客户端（同步 + 异步）
├── utils/
│   ├── assert_result/     # 响应断言
│   ├── callback/          # 回调函数执行器
│   ├── executor/          # JSON 关键字驱动的动作执行器
│   ├── generate_report/   # HTML / JSON / XML 报告生成
│   ├── mock_server/       # 基于 Flask 的模拟服务器
│   ├── socket_server/     # TCP Socket 服务器（远程自动化）
│   ├── project/           # 项目脚手架与模板
│   ├── json/              # JSON 读写工具
│   ├── xml/               # XML 解析/转换工具
│   ├── test_record/       # 全局测试记录存储
│   ├── logging/           # 日志实例
│   ├── file_process/      # 文件列表工具
│   ├── package_manager/   # 动态加载包
│   └── exception/         # 自定义异常
└── gui/                   # 可选的 PySide6 GUI
```

---

## 安装

```bash
pip install je_api_testka
```

安装 GUI 支持：

```bash
pip install je_api_testka[gui]
```

---

## 快速开始

### 使用 requests 后端

```python
from je_api_testka import test_api_method_requests

# GET 请求
result = test_api_method_requests("get", "http://httpbin.org/get")
print(result["response_data"]["status_code"])  # 200

# POST 请求，带参数
result = test_api_method_requests(
    "post",
    "http://httpbin.org/post",
    params={"task": "new task"}
)
print(result["response_data"]["status_code"])  # 200
```

### 使用 httpx 后端（同步）

```python
from je_api_testka import test_api_method_httpx

result = test_api_method_httpx("get", "http://httpbin.org/get")
print(result["response_data"]["status_code"])  # 200
```

### 使用 httpx 后端（异步）

```python
import asyncio
from je_api_testka import test_api_method_httpx_async

async def main():
    result = await test_api_method_httpx_async("get", "http://httpbin.org/get")
    print(result["response_data"]["status_code"])  # 200

asyncio.run(main())
```

### HTTP/2 支持

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

### SOAP/XML 请求

```python
from je_api_testka import test_api_method_requests

result = test_api_method_requests(
    "post",
    "http://example.com/soap-endpoint",
    soap=True,
    data='<soap:Envelope>...</soap:Envelope>'
)
```

当 `soap=True` 时，`Content-Type` 头部会自动设置为 `application/soap+xml`。

### Session 持久化请求

`requests` 后端支持 Session 方法，用于持久化连接（cookies、认证等）：

```python
from je_api_testka import test_api_method_requests

# 可用方法：session_get, session_post, session_put, session_patch, session_delete, session_head, session_options
result = test_api_method_requests("session_get", "http://httpbin.org/get")
```

---

## 结果断言

传入 `result_check_dict` 可自动断言响应字段：

```python
from je_api_testka import test_api_method_requests

# 若 status_code 不是 200，将抛出 APIAssertException
test_api_method_requests(
    "get",
    "http://httpbin.org/get",
    result_check_dict={"status_code": 200}
)
```

可断言的响应数据字段：`status_code`、`text`、`content`、`headers`、`cookies`、`encoding`、`elapsed`、`request_time_sec`、`request_method`、`request_url`、`request_body`、`start_time`、`end_time`。

---

## 报告生成

报告从全局的 `test_record_instance` 生成，所有测试结果会自动记录。

### HTML 报告

```python
from je_api_testka import test_api_method_requests, generate_html_report

test_api_method_requests("get", "http://httpbin.org/get")
test_api_method_requests("post", "http://httpbin.org/post")

# 生成 "my_report.html"，包含成功/失败表格
generate_html_report("my_report")
```

### JSON 报告

```python
from je_api_testka import test_api_method_requests, generate_json_report

test_api_method_requests("get", "http://httpbin.org/get")

# 生成 "my_report_success.json" 和 "my_report_failure.json"
generate_json_report("my_report")
```

### XML 报告

```python
from je_api_testka import test_api_method_requests, generate_xml_report

test_api_method_requests("get", "http://httpbin.org/get")

# 生成 "my_report_success.xml" 和 "my_report_failure.xml"
generate_xml_report("my_report")
```

---

## 模拟服务器

APITestka 内置基于 Flask 的模拟服务器，用于本地测试：

```python
from je_api_testka import flask_mock_server_instance, request

# 添加自定义路由
def my_endpoint():
    return {"message": "hello", "params": dict(request.args)}

flask_mock_server_instance.add_router(
    {"/api/test": my_endpoint},
    methods=["GET", "POST"]
)

# 启动模拟服务器（默认：localhost:8090）
flask_mock_server_instance.start_mock_server()
```

也可以创建自定义 host/port 的新实例：

```python
from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

server = FlaskMockServer("0.0.0.0", 5000)
server.add_router({"/health": lambda: "OK"}, methods=["GET"])
server.start_mock_server()
```

---

## 回调执行器

在 API 测试完成后执行回调函数：

```python
from je_api_testka import callback_executor

def my_callback(message):
    print(f"回调：{message}")

callback_executor.callback_function(
    trigger_function_name="AT_test_api_method",
    callback_function=my_callback,
    callback_function_param={"message": "测试完成！"},
    callback_param_method="kwargs",
    http_method="get",
    test_url="http://httpbin.org/get"
)
```

---

## 脚本化执行器

Executor 实现了 JSON 关键字驱动测试，测试动作以 JSON 数组定义，并通过编程方式执行。

### JSON 关键字驱动测试

创建一个 JSON 文件（例如 `test_actions.json`）：

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

### 通过 Python 执行 JSON 文件

```python
from je_api_testka import execute_action, read_action_json

execute_action(read_action_json("test_actions.json"))
```

### 执行整个目录的 JSON 文件

```python
from je_api_testka import execute_files, get_dir_files_as_list

execute_files(get_dir_files_as_list("path/to/json_dir"))
```

### 添加自定义命令

```python
from je_api_testka import add_command_to_executor, execute_action

def my_custom_function(url):
    print(f"自定义测试：{url}")

add_command_to_executor({"my_test": my_custom_function})

execute_action([
    ["my_test", ["http://example.com"]]
])
```

**内置的 Executor 命令：**

| 命令 | 说明 |
|---|---|
| `AT_test_api_method` | 使用 requests 后端测试 API |
| `AT_test_api_method_httpx` | 使用 httpx 同步后端测试 API |
| `AT_delegate_async_httpx` | 使用 httpx 异步后端测试 API（同步调用） |
| `AT_generate_html` | 生成 HTML 报告数据 |
| `AT_generate_html_report` | 生成 HTML 报告文件 |
| `AT_generate_json` | 生成 JSON 报告数据 |
| `AT_generate_json_report` | 生成 JSON 报告文件 |
| `AT_generate_xml` | 生成 XML 报告数据 |
| `AT_generate_xml_report` | 生成 XML 报告文件 |
| `AT_execute_action` | 执行嵌套动作列表 |
| `AT_execute_files` | 从多个文件执行动作 |
| `AT_add_package_to_executor` | 动态加载包到执行器 |
| `AT_add_package_to_callback_executor` | 动态加载包到回调执行器 |
| `AT_flask_mock_server_add_router` | 添加路由到模拟服务器 |
| `AT_start_flask_mock_server` | 启动模拟服务器 |

---

## CLI 使用方式

APITestka 提供完整的 CLI 接口：

```bash
# 执行单个 JSON 动作文件
python -m je_api_testka -e test_actions.json

# 执行目录中所有 JSON 文件
python -m je_api_testka -d path/to/json_dir

# 直接执行 JSON 字符串
python -m je_api_testka --execute_str '[["AT_test_api_method", {"http_method": "get", "test_url": "http://httpbin.org/get"}]]'

# 创建新项目（含模板）
python -m je_api_testka -c MyProject
```

| 参数 | 说明 |
|---|---|
| `-e`, `--execute_file` | 执行单个 JSON 动作文件 |
| `-d`, `--execute_dir` | 执行目录中所有 JSON 文件 |
| `--execute_str` | 直接执行 JSON 字符串 |
| `-c`, `--create_project` | 创建项目目录及模板文件 |

---

## 远程自动化（Socket 服务器）

APITestka 内置 TCP Socket 服务器，用于远程命令执行：

```python
from je_api_testka import start_apitestka_socket_server

# 启动 Socket 服务器（默认：localhost:9939）
server = start_apitestka_socket_server(host="localhost", port=9939)
```

客户端可通过 TCP 发送 JSON 格式的动作列表，服务器会执行并返回结果。发送 `quit_server` 可关闭服务器。

也支持 CLI 参数：

```bash
python -m je_api_testka.utils.socket_server.api_testka_socket_server localhost 9939
```

---

## 项目脚手架

生成含有关键字与执行器模板的项目结构：

```python
from je_api_testka import create_project_dir

create_project_dir(project_path=".", parent_name="MyAPIProject")
```

生成的结构如下：

```
MyAPIProject/
├── keyword/
│   ├── keyword1.json          # 示例关键字测试（POST）
│   ├── keyword2.json          # 示例关键字测试（GET）
│   └── bad_keyword_1.json     # 含包加载的示例
└── executor/
    ├── executor_one_file.py   # 执行单个关键字文件
    ├── executor_folder.py     # 执行目录中所有关键字文件
    └── executor_bad_file.py   # 含动态包加载的示例
```

---

## GUI（可选）

APITestka 提供可选的 PySide6 图形用户界面：

```bash
pip install je_api_testka[gui]
```

GUI 需要 PySide6 6.11.0 及 qt-material。

---

## 测试记录

所有 API 测试结果会自动存储在全局的 `test_record_instance` 中：

```python
from je_api_testka import test_api_method_requests, test_record_instance

test_api_method_requests("get", "http://httpbin.org/get")
test_api_method_requests("get", "http://invalid-url")

# 获取成功的测试记录
print(len(test_record_instance.test_record_list))

# 获取错误记录
print(len(test_record_instance.error_record_list))

# 清除所有记录
test_record_instance.clean_record()
```

每条成功记录包含：`status_code`、`text`、`content`、`headers`、`history`、`encoding`、`cookies`、`elapsed`、`request_time_sec`、`request_method`、`request_url`、`request_body`、`start_time`、`end_time`。

---

## 项目结构

```
APITestka/
├── je_api_testka/             # 主包
│   ├── __init__.py            # 公开 API 导出
│   ├── __main__.py            # CLI 入口点
│   ├── requests_wrapper/      # requests HTTP 客户端封装
│   ├── httpx_wrapper/         # httpx HTTP 客户端封装（同步 + 异步）
│   ├── utils/                 # 工具模块
│   └── gui/                   # 可选的 PySide6 GUI
├── test/                      # 测试套件
│   ├── test_requests/         # requests 后端测试
│   ├── test_httpx_sync/       # httpx 同步后端测试
│   ├── test_httpx_async/      # httpx 异步后端测试
│   └── test_utils/            # 工具模块测试
├── docs/                      # Sphinx 文档源码
├── apitestka_driver/          # 独立驱动程序可执行文件
├── licenses/                  # 许可证文件
├── pyproject.toml             # 构建配置
├── requirements.txt           # 运行时依赖
└── dev_requirements.txt       # 开发依赖
```

---

## 系统要求

- **Python** 3.10 或更高版本
- **依赖包：** `requests`、`Flask`、`httpx`
- **可选（GUI）：** `PySide6==6.11.0`、`qt-material`

---

## 开发

```bash
# 克隆仓库
git clone https://github.com/Intergration-Automation-Testing/APITestka.git
cd APITestka

# 安装开发依赖
pip install -r dev_requirements.txt

# 运行测试
pytest
```

---

## 贡献

请参阅 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解贡献指南。

---

## 许可证

本项目使用 MIT 许可证。详见 [licenses/APITestka_LICENSE](../licenses/APITestka_LICENSE)。

---

## 链接

- **主页：** https://github.com/Intergration-Automation-Testing/APITestka
- **文档：** https://apitestka.readthedocs.io/en/latest/
- **PyPI：** https://pypi.org/project/je_api_testka/
