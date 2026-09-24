# APITestka Architecture

> Short overview for people and agents.
> Last verified: 2026-09-22 against `ca9a952` on `dev`.

## 1. Purpose

APITestka (`je_api_testka`) is a keyword-driven API testing framework. It is published as
`je_api_testka` (stable, `pyproject.toml`) and `je_api_testka_dev` (dev, `dev.toml`). Requests go
through `requests` or `httpx` wrappers (plus WebSocket, SSE and GraphQL backends). Every result is
stored in one shared test record, and HTML, JSON, XML, JUnit, Allure and Markdown reports are
built from that record. You can reach the same commands from Python, from JSON action files, the
CLI, a TCP socket server, an MCP server, a pytest plugin and an optional PySide6 GUI.

## 2. Layers and directories

| Path | Responsibility |
| --- | --- |
| `je_api_testka/__init__.py` | Public facade. `__all__` is the supported import surface |
| `je_api_testka/__main__.py` | Legacy flag CLI (`python -m je_api_testka`) |
| `je_api_testka/requests_wrapper/`, `httpx_wrapper/` | HTTP backends: `test_api_method_requests`, `test_api_method_httpx`, `test_api_method_httpx_async`, `delegate_async_httpx` |
| `je_api_testka/websocket_wrapper/`, `sse_wrapper/`, `graphql_wrapper/` | Extra protocol backends that need optional dependencies |
| `je_api_testka/utils/executor/action_executor.py` | `Executor.event_dict` (the `AT_*` command map), `execute_action`, `execute_files`, `add_command_to_executor` |
| `je_api_testka/utils/test_record/` | `test_record_instance`: shared success and error records, guarded by an `RLock` |
| `je_api_testka/utils/assert_result/` | `check_result`, JSON Schema and JSONPath checks, snapshots |
| `je_api_testka/utils/generate_report/` | HTML, JSON, XML, JUnit, Allure and Markdown reports; badge, run diff, trend store |
| `je_api_testka/utils/callback/` | `callback_executor`: run a trigger command, then a callback |
| `je_api_testka/utils/mock_server/` | `flask_mock_server_instance` with dynamic, template, proxy, webhook and OpenAPI routes, plus fault injection |
| `je_api_testka/utils/socket_server/` | `start_apitestka_socket_server` (TCP command server) |
| `je_api_testka/utils/package_manager/` | `package_manager`: loads an installed package's members into the executor |
| `je_api_testka/utils/project/` | `create_project_dir` scaffolding (keyword and executor templates) |
| `je_api_testka/utils/{json,xml,file_process,logging,exception,retry,observability}/` | JSON and XML I/O, directory listing, `apitestka_logger` (file at `$APITESTKA_LOG_FILE` or `~/.je_api_testka/logs/APITestka.log`, opened on first use; the root logger is left alone), exception hierarchy, `RetryPolicy`, OpenTelemetry hooks |
| `je_api_testka/data/` | Variable store, template rendering, env profiles, fake-data helpers, data rows |
| `je_api_testka/connection/` | Connection options, DNS override, record/replay cassettes |
| `je_api_testka/diff/`, `spec/` | Response and contract diff, SLA checks; schema inference, records → OpenAPI, OpenAPI changelog |
| `je_api_testka/security/` | Auth header helpers, CORS/SSRF/rate-limit probes, header scan, fuzzing, `pip-audit` wrapper |
| `je_api_testka/runner/` | Parallel runner, tag filter, dependency ordering of actions |
| `je_api_testka/integrations/` | cURL and HAR import, webhook notify, GitHub PR comment |
| `je_api_testka/ai/` | Pluggable text-completion backend (no-op by default) used by test generation, failure classification and fake payloads |
| `je_api_testka/cli/` | Subcommand CLI (`apitestka`): import, REPL, scaffold, completion, terminal summary |
| `je_api_testka/mcp_server/` | MCP stdio server and its tool catalogue |
| `je_api_testka/pytest_plugin/` | pytest fixtures, registered through the `pytest11` entry point |
| `je_api_testka/gui/` | Optional PySide6 GUI (`gui` extra) with language wrappers |
| `apitestka_driver/` | Prebuilt socket-server driver (script plus Windows and Linux binaries) |
| `test/` | pytest suite with one `test_<area>/` per package. Shared fixtures are in `test/conftest.py`. The root `conftest.py` keeps source files out of collection |
| `docs/source/` | Sphinx docs (`Eng/`, `Zh/`, `API/`) |

## 3. Entry points and public interfaces

- **Python facade** (`import je_api_testka`): `test_api_method_requests`, `test_api_method_httpx(_async)`,
  `execute_action`, `execute_files`, `add_command_to_executor`, `executor`, `test_record_instance`,
  `generate_{html,json,xml}_report`, `flask_mock_server_instance`, `start_apitestka_socket_server`,
  `callback_executor`, `create_project_dir`.
- **Action format**: an action is `[name]`, `[name, {kwargs}]` or `[name, [args]]`. A file holds a
  list of actions or `{"api_testka": [...]}`.
- **Legacy CLI**: `python -m je_api_testka` with `-e/--execute_file`, `-d/--execute_dir`,
  `-c/--create_project` and `--execute_str`. On `win32`/`cygwin`/`msys`, `--execute_str` is decoded
  with `json.loads` twice. Errors print `repr(error)` to stderr and exit with code 1.
- **Subcommand CLI**: `apitestka` (`je_api_testka.cli.cli_main:main`) with `run`, `create`, `mock`,
  `import`, `repl`, `summary`, `scaffold`, `completion` and `mcp`.
- **MCP**: `apitestka-mcp`, `python -m je_api_testka.mcp_server` or `apitestka mcp` (stdio, needs the
  `mcp` extra, mcp 1.x or 2.x: `build_server` registers the handlers with the 1.x `list_tools()`/`call_tool()`
  decorators or passes them to the 2.x `Server(on_list_tools=..., on_call_tool=...)`). Tools are the `apitestka_*` `MCPToolSpec` entries in `APITESTKA_TOOLS`
  (`mcp_server/tool_definitions.py`).
- **TCP socket server**: `start_apitestka_socket_server(host="localhost", port=9939)` takes one JSON
  action list per connection. It replies with each return value, then `Return_Data_Over_JE`.
  `quit_server` stops it.
- **pytest plugin**: `pytest11` entry `apitestka = je_api_testka.pytest_plugin.plugin` provides
  `apitestka_record`, `apitestka_clean_record` and `apitestka_mock_server`.
- **GUI**: `je_api_testka.gui.main_window.APITestkaUI` (`python -m je_api_testka.gui.main_window`). The
  embeddable widget is `je_api_testka.gui.main_widget.APITestkaWidget`.
- **Packaging gap**: only `pyproject.toml` declares the console scripts, the `pytest11` entry point
  and the extras other than `gui`. `dev.toml` (`je_api_testka_dev`) currently declares none of them.

## 4. Main flows

**Action file → report**

```
JSON file / --execute_str → __main__ (Windows double json.loads) → execute_action()
  → Executor._execute_event → event_dict["AT_*"] → test_api_method_requests | httpx | ws | sse | graphql
  → optional check_result(result_check_dict) → test_record_instance (test_record_list / error_record_list)
  → AT_generate_*_report → report file   (a failed action is stored as repr(error); the batch continues)
```

**Remote execution**

```
TCP client → TCPServerHandler.handle → json.loads → execute_action → return values + Return_Data_Over_JE
MCP host → apitestka-mcp → build_server → dispatch_tool(name, args) → APITESTKA_TOOLS handler → executor / wrappers
```

## 5. Extension points

- **New executor command**:
  1. Write a typed, documented function in the module that owns the concern.
  2. Register it in `Executor.__init__` (`utils/executor/action_executor.py`) under an `AT_` name, or
     at runtime with `add_command_to_executor({...})` (functions and methods only). Register only sync
     entry points, because the executor does not await coroutines.
  3. For callback triggers, also add it to `CallbackFunctionExecutor.event_dict`
     (`utils/callback/callback_function_executor.py`).
  4. Export public names from `je_api_testka/__init__.py` and `__all__`, then add tests in `test/test_<area>/`.
- **New report format**: module in `utils/generate_report/` that reads `test_record_instance` →
  `AT_generate_*` command → export from `__init__.py` → tests.
- **New protocol backend**: `<proto>_wrapper/` package that records into `test_record_instance`, with
  a lazy import → extra under `[project.optional-dependencies]` in `pyproject.toml` (`dev.toml` mirrors
  only `gui`) → executor registration → tests with `pytest.importorskip` plus the missing-dependency path.
- **MCP tool**: add an `MCPToolSpec` and handler to `APITESTKA_TOOLS`, then tests in `test/test_mcp_server/`.
- **CLI subcommand**: add `_cmd_<name>` and a subparser in `build_parser()` (`cli/cli_main.py`), then
  tests in `test/test_cli/`.
- **Mock routes / runtime plugins**: `flask_mock_server_instance.add_router()` (or `add_dynamic_route()`,
  `add_template_route()`); `AT_add_package_to_executor` registers an installed package's members.

## 6. Cross-project boundaries

- **PyBreeze (subprocess)** runs `python -m je_api_testka --execute_str <json>` or `--execute_file <path>`
  (`PyBreeze/pybreeze/extend/process_executor/python_task_process_manager.py`; the package name is in
  `.../process_executor/api_testka/api_testka_process.py`). On Windows PyBreeze runs `json.dumps` on
  the string again, so the legacy flags and the double decode in `__main__.py` are a contract, guarded by
  `test/test_cli/test_legacy_cli_contract.py`.
- **PyBreeze (in-process)** embeds `je_api_testka.gui.main_widget.APITestkaWidget`
  (`pybreeze/pybreeze_ui/menu/automation_menu/api_testka_menu/build_api_testka_menu.py`). It also
  generates scripts that import `test_api_method_requests` (`pybreeze/utils/curl_import/script_templates.py`).
- **TestPioneer**: `with: api-runner` imports `je_api_testka.execute_action` in-process
  (`test_pioneer/executor/run/utils.py`). `parallel_run` spawns
  `python -m je_api_testka --execute_file <script>` (`test_pioneer/executor/run/parallel_run.py`).
- **Sibling executors** share the action-list shape and the `Return_Data_Over_JE` socket terminator,
  but differ in command prefix (`AT_` here, `LD_` LoadDensity, `MT_` MailThunder, `FA_` FileAutomation),
  dict key (`api_testka` here) and builtins policy: APITestka registers no Python builtins (explicit
  allowlist), LoadDensity registers builtins minus `_UNSAFE_BUILTINS`, and MailThunder registers
  every builtin (known gap).

## 7. Design constraints

- Command maps are explicit allowlists. No `eval()` or `exec()` on untrusted input. Validate socket
  payloads (CLAUDE.md § Coding Standards › Security (Mandatory)).
- Parse XML with `defusedxml`. Every `requests` call passes a `timeout=`. No `verify=False` without a
  justification comment. No `shell=True` (§ Security (Mandatory); § Static Analysis Compliance › Security).
- Extend through `add_command_to_executor` or new `AT_` commands rather than reshaping the core map
  (§ Software Engineering Practices; § Common Development Workflows › Adding a New Executor Command).
- Import heavy optional dependencies lazily (PySide6, websockets, jsonschema, mcp).
  `test_record_instance` must stay thread-safe (§ Performance Best Practices).
- Limits: cognitive complexity ≤ 15, cyclomatic complexity ≤ 10, ≤ 7 parameters, functions ≤ 50
  lines, files ≤ 500 lines, lines ≤ 120 characters (§ Static Analysis Compliance › Maintainability & Complexity).
- Public API is type-annotated and documented. No `print()` in library code; use `apitestka_logger`
  (§ Software Engineering Practices; § Static Analysis Compliance › Code Smells).
- Every change ships with tests. Optional-dependency tests use `pytest.importorskip` and cover the
  missing-dependency path. Reuse the fixtures in `test/conftest.py` (§ Testing Guidelines).
- English commit messages in the `type: description` format (§ Commit Guidelines).

## 8. When to update this file

- A package or subpackage under `je_api_testka/` is added, removed or renamed.
- `__main__.py` flags, `apitestka` subcommands, `[project.scripts]` or the `pytest11` entry point change.
- The action format, the `api_testka` key, the `AT_` prefix, or executor/callback registration changes.
- The socket protocol (port, terminator, `quit_server`) or the MCP tool catalogue shape changes.
- Any §6 contract changes: PyBreeze or TestPioneer invocation, Windows double encoding, `APITestkaWidget`.
- A CLAUDE.md section referenced in §7 is renamed or its rule changes.
- Refresh the "Last verified" line whenever this file is re-checked against HEAD.
