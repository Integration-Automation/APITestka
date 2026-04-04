# APITestka

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](licenses/APITestka_LICENSE)
[![PyPI](https://img.shields.io/pypi/v/je_api_testka.svg)](https://pypi.org/project/je_api_testka/)

**APITestka** is a lightweight, cross-platform framework for automated API testing.
It supports HTTP/HTTPS, SOAP/XML, and JSON, with high-performance request execution,
detailed reporting, and flexible CLI scripting.

Designed for speed and scalability, APITestka enables thousands of requests per second,
integrates with mock servers and remote automation,
and generates reports in multiple formats for easy analysis.

> **Translations / Other Languages:**
> [繁體中文](README/README_zh-TW.md) | [简体中文](README/README_zh-CN.md)

---

## Table of Contents

- [Features](#features)
- [Architecture Overview](#architecture-overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Using the requests Backend](#using-the-requests-backend)
  - [Using the httpx Backend (Sync)](#using-the-httpx-backend-sync)
  - [Using the httpx Backend (Async)](#using-the-httpx-backend-async)
  - [HTTP/2 Support](#http2-support)
  - [SOAP/XML Request](#soapxml-request)
  - [Session-Based Requests](#session-based-requests)
- [Result Assertion](#result-assertion)
- [Report Generation](#report-generation)
  - [HTML Report](#html-report)
  - [JSON Report](#json-report)
  - [XML Report](#xml-report)
- [Mock Server](#mock-server)
- [Callback Executor](#callback-executor)
- [Scripting with Executor](#scripting-with-executor)
  - [JSON Keyword-Driven Testing](#json-keyword-driven-testing)
  - [Executing JSON Files via Python](#executing-json-files-via-python)
  - [Executing a Directory of JSON Files](#executing-a-directory-of-json-files)
  - [Adding Custom Commands](#adding-custom-commands)
- [CLI Usage](#cli-usage)
- [Remote Automation (Socket Server)](#remote-automation-socket-server)
- [Project Scaffolding](#project-scaffolding)
- [GUI (Optional)](#gui-optional)
- [Test Record](#test-record)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)
- [Links](#links)

---

## Features

| Category | Details |
|---|---|
| **HTTP Clients** | `requests` (sync, session support) and `httpx` (sync + async, HTTP/2) |
| **Protocols** | HTTP, HTTPS, SOAP/XML, JSON |
| **Report Formats** | HTML, JSON, XML |
| **Scripting** | JSON keyword-driven test execution via Executor |
| **Mock Server** | Built-in Flask-based mock server for local testing |
| **Remote Automation** | TCP socket server for remote command execution |
| **Assertions** | Built-in response field assertion (status code, headers, body, etc.) |
| **Callback System** | Execute callback functions after API calls |
| **CLI** | Full command-line interface for CI/CD integration |
| **Project Scaffolding** | Auto-generate project structure with templates |
| **GUI** | Optional PySide6 GUI (install with `pip install je_api_testka[gui]`) |
| **Cross-Platform** | Windows, macOS, Linux |
| **Performance** | Thousands of requests per second |

---

## Architecture Overview

```
je_api_testka/
├── requests_wrapper/      # requests-based HTTP client
├── httpx_wrapper/         # httpx-based HTTP client (sync + async)
├── utils/
│   ├── assert_result/     # Response assertion
│   ├── callback/          # Callback function executor
│   ├── executor/          # JSON keyword-driven action executor
│   ├── generate_report/   # HTML / JSON / XML report generation
│   ├── mock_server/       # Flask-based mock server
│   ├── socket_server/     # TCP socket server for remote automation
│   ├── project/           # Project scaffolding & templates
│   ├── json/              # JSON read/write utilities
│   ├── xml/               # XML parse/convert utilities
│   ├── test_record/       # Global test record storage
│   ├── logging/           # Logging instance
│   ├── file_process/      # File listing utilities
│   ├── package_manager/   # Dynamic package loading
│   └── exception/         # Custom exceptions
└── gui/                   # Optional PySide6 GUI
```

---

## Installation

```bash
pip install je_api_testka
```

To install with GUI support:

```bash
pip install je_api_testka[gui]
```

---

## Quick Start

### Using the requests Backend

```python
from je_api_testka import test_api_method_requests

# GET request
result = test_api_method_requests("get", "http://httpbin.org/get")
print(result["response_data"]["status_code"])  # 200

# POST request with parameters
result = test_api_method_requests(
    "post",
    "http://httpbin.org/post",
    params={"task": "new task"}
)
print(result["response_data"]["status_code"])  # 200
```

### Using the httpx Backend (Sync)

```python
from je_api_testka import test_api_method_httpx

result = test_api_method_httpx("get", "http://httpbin.org/get")
print(result["response_data"]["status_code"])  # 200
```

### Using the httpx Backend (Async)

```python
import asyncio
from je_api_testka import test_api_method_httpx_async

async def main():
    result = await test_api_method_httpx_async("get", "http://httpbin.org/get")
    print(result["response_data"]["status_code"])  # 200

asyncio.run(main())
```

### HTTP/2 Support

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

### SOAP/XML Request

```python
from je_api_testka import test_api_method_requests

result = test_api_method_requests(
    "post",
    "http://example.com/soap-endpoint",
    soap=True,
    data='<soap:Envelope>...</soap:Envelope>'
)
```

When `soap=True`, the `Content-Type` header is automatically set to `application/soap+xml`.

### Session-Based Requests

The `requests` backend supports session-based methods for persistent connections (cookies, auth, etc.):

```python
from je_api_testka import test_api_method_requests

# Use session_get, session_post, session_put, session_patch, session_delete, session_head, session_options
result = test_api_method_requests("session_get", "http://httpbin.org/get")
```

---

## Result Assertion

Pass a `result_check_dict` to automatically assert response fields:

```python
from je_api_testka import test_api_method_requests

# This will raise APIAssertException if status_code is not 200
test_api_method_requests(
    "get",
    "http://httpbin.org/get",
    result_check_dict={"status_code": 200}
)
```

You can assert on any field in the response data: `status_code`, `text`, `content`, `headers`, `cookies`, `encoding`, `elapsed`, `request_time_sec`, `request_method`, `request_url`, `request_body`, `start_time`, `end_time`.

---

## Report Generation

Reports are generated from the global `test_record_instance`, which automatically records all test results.

### HTML Report

```python
from je_api_testka import test_api_method_requests, generate_html_report

test_api_method_requests("get", "http://httpbin.org/get")
test_api_method_requests("post", "http://httpbin.org/post")

# Generates "my_report.html" with success/failure tables
generate_html_report("my_report")
```

### JSON Report

```python
from je_api_testka import test_api_method_requests, generate_json_report

test_api_method_requests("get", "http://httpbin.org/get")

# Generates "my_report_success.json" and "my_report_failure.json"
generate_json_report("my_report")
```

### XML Report

```python
from je_api_testka import test_api_method_requests, generate_xml_report

test_api_method_requests("get", "http://httpbin.org/get")

# Generates "my_report_success.xml" and "my_report_failure.xml"
generate_xml_report("my_report")
```

---

## Mock Server

APITestka includes a built-in Flask-based mock server for local testing:

```python
from je_api_testka import flask_mock_server_instance, request

# Add custom routes
def my_endpoint():
    return {"message": "hello", "params": dict(request.args)}

flask_mock_server_instance.add_router(
    {"/api/test": my_endpoint},
    methods=["GET", "POST"]
)

# Start the mock server (default: localhost:8090)
flask_mock_server_instance.start_mock_server()
```

You can also create a new instance with a custom host/port:

```python
from je_api_testka.utils.mock_server.flask_mock_server import FlaskMockServer

server = FlaskMockServer("0.0.0.0", 5000)
server.add_router({"/health": lambda: "OK"}, methods=["GET"])
server.start_mock_server()
```

---

## Callback Executor

Execute a callback function after an API test completes:

```python
from je_api_testka import callback_executor

def my_callback(message):
    print(f"Callback: {message}")

callback_executor.callback_function(
    trigger_function_name="AT_test_api_method",
    callback_function=my_callback,
    callback_function_param={"message": "Test done!"},
    callback_param_method="kwargs",
    http_method="get",
    test_url="http://httpbin.org/get"
)
```

---

## Scripting with Executor

The Executor enables JSON keyword-driven testing, where test actions are defined as JSON arrays and executed programmatically.

### JSON Keyword-Driven Testing

Create a JSON file (e.g., `test_actions.json`):

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

### Executing JSON Files via Python

```python
from je_api_testka import execute_action, read_action_json

execute_action(read_action_json("test_actions.json"))
```

### Executing a Directory of JSON Files

```python
from je_api_testka import execute_files, get_dir_files_as_list

execute_files(get_dir_files_as_list("path/to/json_dir"))
```

### Adding Custom Commands

```python
from je_api_testka import add_command_to_executor, execute_action

def my_custom_function(url):
    print(f"Custom test on: {url}")

add_command_to_executor({"my_test": my_custom_function})

execute_action([
    ["my_test", ["http://example.com"]]
])
```

**Available built-in Executor commands:**

| Command | Description |
|---|---|
| `AT_test_api_method` | Test API with requests backend |
| `AT_test_api_method_httpx` | Test API with httpx sync backend |
| `AT_delegate_async_httpx` | Test API with httpx async backend (run synchronously) |
| `AT_generate_html` | Generate HTML report data |
| `AT_generate_html_report` | Generate HTML report file |
| `AT_generate_json` | Generate JSON report data |
| `AT_generate_json_report` | Generate JSON report file |
| `AT_generate_xml` | Generate XML report data |
| `AT_generate_xml_report` | Generate XML report file |
| `AT_execute_action` | Execute nested action list |
| `AT_execute_files` | Execute actions from multiple files |
| `AT_add_package_to_executor` | Dynamically load a package into executor |
| `AT_add_package_to_callback_executor` | Dynamically load a package into callback executor |
| `AT_flask_mock_server_add_router` | Add route to mock server |
| `AT_start_flask_mock_server` | Start mock server |

---

## CLI Usage

APITestka provides a full CLI interface:

```bash
# Execute a single JSON action file
python -m je_api_testka -e test_actions.json

# Execute all JSON files in a directory
python -m je_api_testka -d path/to/json_dir

# Execute a JSON string directly
python -m je_api_testka --execute_str '[["AT_test_api_method", {"http_method": "get", "test_url": "http://httpbin.org/get"}]]'

# Create a new project with templates
python -m je_api_testka -c MyProject
```

| Flag | Description |
|---|---|
| `-e`, `--execute_file` | Execute a single JSON action file |
| `-d`, `--execute_dir` | Execute all JSON files in a directory |
| `--execute_str` | Execute a JSON string directly |
| `-c`, `--create_project` | Create a project directory with template files |

---

## Remote Automation (Socket Server)

APITestka includes a TCP socket server for remote command execution:

```python
from je_api_testka import start_apitestka_socket_server

# Start the socket server (default: localhost:9939)
server = start_apitestka_socket_server(host="localhost", port=9939)
```

Clients can send JSON-formatted action lists via TCP, and the server will execute them and return results. Send `quit_server` to shut down the server.

The server also supports CLI arguments:

```bash
python -m je_api_testka.utils.socket_server.api_testka_socket_server localhost 9939
```

---

## Project Scaffolding

Generate a project structure with keyword and executor templates:

```python
from je_api_testka import create_project_dir

create_project_dir(project_path=".", parent_name="MyAPIProject")
```

This creates:

```
MyAPIProject/
├── keyword/
│   ├── keyword1.json          # Example keyword test (POST)
│   ├── keyword2.json          # Example keyword test (GET)
│   └── bad_keyword_1.json     # Example with package loading
└── executor/
    ├── executor_one_file.py   # Execute a single keyword file
    ├── executor_folder.py     # Execute all keyword files in directory
    └── executor_bad_file.py   # Example with dynamic package loading
```

---

## GUI (Optional)

APITestka provides an optional PySide6-based GUI:

```bash
pip install je_api_testka[gui]
```

The GUI requires PySide6 6.11.0 and qt-material.

---

## Test Record

All API test results are automatically stored in a global `test_record_instance`:

```python
from je_api_testka import test_api_method_requests, test_record_instance

test_api_method_requests("get", "http://httpbin.org/get")
test_api_method_requests("get", "http://invalid-url")

# Access successful test records
print(len(test_record_instance.test_record_list))

# Access error records
print(len(test_record_instance.error_record_list))

# Clean all records
test_record_instance.clean_record()
```

Each successful record contains: `status_code`, `text`, `content`, `headers`, `history`, `encoding`, `cookies`, `elapsed`, `request_time_sec`, `request_method`, `request_url`, `request_body`, `start_time`, `end_time`.

---

## Project Structure

```
APITestka/
├── je_api_testka/             # Main package
│   ├── __init__.py            # Public API exports
│   ├── __main__.py            # CLI entry point
│   ├── requests_wrapper/      # requests HTTP client wrapper
│   ├── httpx_wrapper/         # httpx HTTP client wrapper (sync + async)
│   ├── utils/                 # Utility modules
│   └── gui/                   # Optional PySide6 GUI
├── test/                      # Test suite
│   ├── test_requests/         # Tests for requests backend
│   ├── test_httpx_sync/       # Tests for httpx sync backend
│   ├── test_httpx_async/      # Tests for httpx async backend
│   └── test_utils/            # Tests for utility modules
├── docs/                      # Sphinx documentation source
├── apitestka_driver/          # Standalone driver executables
├── licenses/                  # License files
├── pyproject.toml             # Build configuration
├── requirements.txt           # Runtime dependencies
└── dev_requirements.txt       # Development dependencies
```

---

## Requirements

- **Python** 3.10 or later
- **Dependencies:** `requests`, `Flask`, `httpx`
- **Optional (GUI):** `PySide6==6.11.0`, `qt-material`

---

## Development

```bash
# Clone the repository
git clone https://github.com/Intergration-Automation-Testing/APITestka.git
cd APITestka

# Install development dependencies
pip install -r dev_requirements.txt

# Run tests
pytest
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License. See [licenses/APITestka_LICENSE](licenses/APITestka_LICENSE).

---

## Links

- **Homepage:** https://github.com/Intergration-Automation-Testing/APITestka
- **Documentation:** https://apitestka.readthedocs.io/en/latest/
- **PyPI:** https://pypi.org/project/je_api_testka/
