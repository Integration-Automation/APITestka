# CLAUDE.md - APITestka Development Guide

## Project Overview

APITestka (`je_api_testka`) is a lightweight, cross-platform Python framework for automated API testing. Supports HTTP/HTTPS, SOAP/XML, JSON with `requests` and `httpx` backends.

- **Python**: 3.10+
- **Dependencies**: `requests`, `Flask`, `httpx`
- **Optional GUI**: `PySide6==6.11.0`, `qt-material`

## Build & Test Commands

```bash
pip install -e .                  # Install in development mode
pip install -e .[gui]             # Install with GUI support
pytest                            # Run all tests
pytest test/test_requests/        # Run requests backend tests only
pytest test/test_httpx_sync/      # Run httpx sync tests only
pytest test/test_httpx_async/     # Run httpx async tests only
pytest test/test_utils/           # Run utility tests only
pytest -x                         # Stop on first failure
```

- Test config: `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["test"]`, `asyncio_mode = "auto"`)
- Root `conftest.py` filters out source files from collection

## Architecture & Design Patterns

### Package Structure

```
je_api_testka/
├── requests_wrapper/      # Facade pattern - wraps requests library
├── httpx_wrapper/         # Facade pattern - wraps httpx (sync + async)
├── utils/
│   ├── assert_result/     # Strategy pattern - response validation
│   ├── callback/          # Observer pattern - post-request callbacks
│   ├── executor/          # Command pattern - JSON keyword-driven actions
│   ├── generate_report/   # Template Method - HTML/JSON/XML reports
│   ├── mock_server/       # Flask-based mock server
│   ├── socket_server/     # TCP remote automation server
│   ├── project/           # Factory pattern - project scaffolding
│   ├── json/              # JSON I/O utilities
│   ├── xml/               # XML parse/convert utilities
│   ├── test_record/       # Singleton - global test record storage
│   ├── logging/           # Singleton - logging instance
│   ├── file_process/      # File listing utilities
│   ├── package_manager/   # Plugin pattern - dynamic package loading
│   └── exception/         # Custom exception hierarchy
└── gui/                   # Optional PySide6 GUI
```

### Key Design Principles

- **Facade Pattern**: `requests_wrapper` and `httpx_wrapper` provide unified interfaces over HTTP libraries
- **Command Pattern**: Executor maps string commands to callable functions, enabling JSON-driven test scripting
- **Singleton Pattern**: `test_record_instance` and logging are shared global instances
- **Strategy Pattern**: Assertion checks are decoupled from request execution
- **Observer/Callback Pattern**: `callback_executor` hooks into test completion events

## Coding Standards

### Security (Mandatory)

- **Never** hardcode credentials, tokens, API keys, or secrets in source code
- **Always** validate and sanitize all external input (user input, network data, file content)
- **Prevent injection**: parameterize queries, escape XML/HTML output, validate URLs before requests
- **Use `defusedxml`** or equivalent safe parsers for XML input to prevent XXE attacks
- **Socket server**: validate all incoming commands; reject malformed or unauthorized payloads
- **No `eval()` or `exec()`** on untrusted input; executor command mapping must use explicit allowlists
- **Dependency awareness**: keep `requests`, `Flask`, `httpx` updated; audit for known CVEs
- **File operations**: validate paths to prevent directory traversal; never trust user-supplied file paths without sanitization

### Performance Best Practices

- **Connection reuse**: use session-based requests (`session_get`, etc.) for repeated calls to the same host
- **Async by default**: prefer `httpx` async backend for high-concurrency workloads
- **HTTP/2**: enable `http2=True` for multiplexed connections where supported
- **Lazy imports**: defer heavy imports (PySide6, optional dependencies) until actually needed
- **Minimize allocations**: reuse buffers and avoid unnecessary copies in hot paths (report generation, record storage)
- **Thread safety**: `test_record_instance` must be thread-safe when used in concurrent test execution

### Software Engineering Practices

- **Single Responsibility**: each module handles one concern; do not mix request logic with reporting
- **Open/Closed Principle**: extend executor via `add_command_to_executor` instead of modifying core command map
- **DRY**: shared logic (response parsing, record formatting) must live in utility modules, not duplicated across wrappers
- **Fail fast**: raise specific exceptions (`APIAssertException`, custom errors) immediately on validation failures
- **Type hints**: all public API functions must have type annotations
- **Docstrings**: public functions require docstrings; internal helpers need them only when logic is non-obvious

### Code Style

- Follow PEP 8
- Use snake_case for functions and variables, PascalCase for classes
- Prefix internal/private helpers with underscore (`_helper_func`)
- Keep functions focused and short; extract logic into helpers when a function exceeds ~50 lines
- No unused imports, variables, or dead code blocks - remove them immediately

## Commit Guidelines

- Write commit messages in English
- Use conventional format: `type: short description`
  - Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `security`
- **Do NOT mention any AI tools, assistants, or co-authors in commit messages**
- **No `Co-Authored-By` lines referencing AI in commits**
- Focus on what changed and why, not how it was written
- Examples:
  - `feat: add HTTP/2 multiplexing support for httpx async backend`
  - `fix: prevent XXE injection in XML report parser`
  - `refactor: extract common response parsing to shared utility`
  - `security: sanitize socket server input against command injection`

## Common Development Workflows

### Adding a New Executor Command

1. Define the function in the appropriate module
2. Register via `add_command_to_executor({"COMMAND_NAME": func})`
3. Prefix command names with `AT_` to follow existing convention
4. Add corresponding tests in `test/test_utils/`

### Adding a New Report Format

1. Create module in `je_api_testka/utils/generate_report/`
2. Follow the Template Method pattern used by existing report generators
3. Register in `__init__.py` public API exports
4. Add tests validating output format and edge cases

### Adding Mock Server Routes

1. Define endpoint function with proper request validation
2. Register via `flask_mock_server_instance.add_router()`
3. Always validate input parameters in mock endpoints
