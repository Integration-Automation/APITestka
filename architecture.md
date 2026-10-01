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
| `je_api_testka/utils/executor/action_executor.py` | `Executor` (je_action_core's `ActionExecutor` with APITestka's settings): `event_dict` (the `AT_*` command map), `execute_action`, `execute_files`, `add_command_to_executor` |
| `je_api_testka/utils/test_record/` | `test_record_instance`: shared success and error records, guarded by an `RLock` |
| `je_api_testka/utils/assert_result/` | `check_result`, JSON Schema and JSONPath checks, snapshots |
| `je_api_testka/utils/generate_report/` | HTML, JSON, XML, JUnit, Allure and Markdown reports; badge, run diff, trend store; per-endpoint latency history and anomaly detection (`latency_trends.py`, same SQLite file) and the HTML trend report (`trend_report.py`) |
| `je_api_testka/utils/callback/` | `callback_executor` (je_action_core's callback executor): run a trigger command, then a callback; a failure is logged and returns `None` |
| `je_api_testka/utils/mock_server/` | `flask_mock_server_instance` with dynamic, template, proxy, webhook and OpenAPI routes, plus fault injection; `WebSocketMockServer` (`websocket_mock.py`) and `GrpcStubServer` (`grpc_stub.py`) run in background threads; `protocol_mocks.py` keeps one of each for JSON actions; `mock_config.py` reads `apitestka mock --config` |
| `je_api_testka/utils/socket_server/` | `start_apitestka_socket_server`: je_action_core's TCP action server running `execute_action` (port 9939) |
| `je_api_testka/utils/package_manager/` | `package_manager` (je_action_core's, gate on): loads an installed package's members into the executor |
| `je_api_testka/utils/project/` | `create_project_dir` scaffolding (keyword and executor templates) |
| `je_api_testka/utils/{json,xml,file_process,logging,exception,retry,observability}/` | JSON (je_action_core's `ActionJsonFile` with APITestka's messages) and XML I/O, directory listing (je_action_core's), `apitestka_logger` (file at `$APITESTKA_LOG_FILE` or `~/.je_api_testka/logs/APITestka.log`, opened on first use; the root logger is left alone), exception hierarchy, `RetryPolicy`, OpenTelemetry hooks |
| `je_api_testka/data/` | Variable store, template rendering, env profiles, fake-data helpers, data rows |
| `je_api_testka/connection/` | Connection options, DNS override, record/replay cassettes |
| `je_api_testka/diff/`, `spec/` | Response and contract diff, SLA checks; schema inference, records → OpenAPI (`records_to_openapi`; `openapi_export` reads saved JSON reports and writes the spec), OpenAPI changelog, path-template matching (`path_templates`), deterministic examples (`examples`), test-as-spec loop (`spec_loop`: drift, coverage, missing tests, inferred document) |
| `je_api_testka/contract/` | Pact v2 consumer contracts from records (`pact.py`), matching rules (`matching.py`), provider verification (`verifier.py`), bidirectional check against an OpenAPI document (`openapi_compat.py`, `openapi_schema.py`), file-level steps for the executor and CLI (`commands.py`) |
| `je_api_testka/security/` | Auth header helpers, CORS/SSRF/rate-limit probes, header scan, fuzzing, `pip-audit` wrapper |
| `je_api_testka/runner/` | Parallel runner, tag filter, dependency ordering of actions |
| `je_api_testka/integrations/` | cURL and HAR import, webhook notify, GitHub PR comment; LoadDensity bridge (`load_density.py` converts requests to LoadDensity tasks, `load_density_runner.py` runs them out of process and judges the summary, `load_density_commands.py` for the executor and CLI) |
| `je_api_testka/ai/` | Pluggable text-completion backend (no-op by default) used by test generation, failure classification and fake payloads; `AnthropicAIBackend` (`ai` extra) is the reference implementation; selection by `set_ai_backend` / `select_ai_backend` / `AT_select_ai_backend` or `APITESTKA_AI_BACKEND` on first use |
| `je_api_testka/cli/` | Subcommand CLI (`apitestka`): import, REPL, scaffold, completion, terminal summary |
| `je_api_testka/mcp_server/` | MCP stdio server and its tool catalogue |
| `je_api_testka/pytest_plugin/` | pytest fixtures, registered through the `pytest11` entry point |
| `je_api_testka/gui/` | Optional PySide6 GUI (`gui` extra): `main_widget.APITestkaWidget` (sidebar + one page per feature in `gui/pages/`, console), `main_window.APITestkaUI` (Language and Theme menus), `theme.py` (light/dark style sheets), `widgets.py` (shared helpers; `TaskThread` runs work on a daemon thread, so a page can be rebuilt or the window closed mid-task), Qt-free models (`request_model`, `history_panel`, `env_manager_model`), four language wrappers |
| `apitestka_driver/` | Prebuilt socket-server driver (script plus Windows and Linux binaries) |
| `test/` | pytest suite with one `test_<area>/` per package. Shared fixtures are in `test/conftest.py`. The root `conftest.py` keeps source files out of collection |
| `docs/source/` | Sphinx docs (`Eng/`, `Zh/`, `API/`) |

## 3. Entry points and public interfaces

- **Python facade** (`import je_api_testka`): `test_api_method_requests`, `test_api_method_httpx(_async)`,
  `execute_action`, `execute_files`, `add_command_to_executor`, `executor`, `test_record_instance`,
  `generate_{html,json,xml}_report`, `flask_mock_server_instance`, `start_apitestka_socket_server`,
  `callback_executor`, `create_project_dir`.
- **Action format**: an action is `[name]`, `[name, {kwargs}]` or `[name, [args]]`. A file holds a
  list of actions or `{"api_testka": [...]}`. The executor drops runner metadata (`id`, `depends_on`, `tags`) from the
  kwargs before the call. Converters (OpenAPI/Postman/cURL/HAR import, AI test generation, scaffold,
  the `apitestka_test_api` MCP tool) build request actions with
  `utils/executor/request_action.build_request_action` → `["AT_test_api_method", {...}]`.
- **Legacy CLI**: `python -m je_api_testka` with `-e/--execute_file`, `-d/--execute_dir`,
  `-c/--create_project` and `--execute_str`. On `win32`/`cygwin`/`msys`, `--execute_str` is decoded
  with `json.loads` twice. Errors print `repr(error)` to stderr and exit with code 1.
- **Subcommand CLI**: `apitestka` (`je_api_testka.cli.cli_main:main`) with `run`, `create`, `mock`,
  `import`, `repl`, `summary`, `scaffold`, `completion`, `mcp`, `openapi`, `contract record|verify|compare`,
  `generate-tests`, `load convert|run` (`cli/load_cli.py`), `trend record|check|report` (`cli/trend_cli.py`) and
  `spec check` (`cli/spec_cli.py`)
  (`cli/contract_cli.py`); shared helpers are in `cli/cli_common.py`. `cli/completion.py`
  `SUBCOMMANDS` lists the same names (a test compares them with the parser).
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
  embeddable widget is `je_api_testka.gui.main_widget.APITestkaWidget`, constructed with no arguments (the
  keyword-only `history` and `environments` models are optional; the window passes its own to every rebuild, so a
  language switch keeps them); it applies no style sheet, so an embedding application keeps its own look.
- **Packaging**: `pyproject.toml` and `dev.toml` (`je_api_testka_dev`) declare the same console scripts,
  `pytest11` entry point and extras; `test/test_utils/test_dev_toml_parity.py` keeps them equal. Neither the
  wheel nor the sdist carries `test/`: package discovery never finds it, and `MANIFEST.in` prunes it from the
  sdist (`test/test_utils/test_sdist_manifest.py`).
- **PyPI packages**: `je_api_testka` (stable) and `je_api_testka_dev` (dev channel), both published by CI.
  - Stable: a push to `main` runs `publish.yml`, which bumps `pyproject.toml`, uploads, tags and creates the
    GitHub release.
  - Dev: the `publish-dev` job of `ci.yml` runs after the `test` matrix on a push to `dev` (never for `main`, a
    pull request or the schedule), builds from `dev.toml` and uploads when the commit is still the tip of `dev`
    and the wheel differs from the newest published one. `scripts/dev_release.py` takes the version from PyPI
    (newest release plus one patch), so nothing is committed back.
  - Both jobs hold the PyPI token and install only `.github/requirements/publish.txt`: `build` and `twine`,
    hash-locked and wheels-only, generated from `publish.in`. `test/test_workflow_actions.py` fails when a job
    with the token installs anything else. Dependabot's pip entry lists `/.github/requirements`.

## 4. Main flows

**Action file → report**

```
JSON file / --execute_str → __main__ (Windows double json.loads) → execute_action()
  → Executor._execute_event → event_dict["AT_*"] → test_api_method_requests | httpx | ws | sse | graphql
  → optional check_result(result_check_dict) → test_record_instance (test_record_list / error_record_list)
  → AT_generate_*_report → report file   (a failed action is stored as repr(error); the batch continues)
```

**Test-as-spec loop**

```
apitestka spec check / AT_check_spec_against_tests → run actions or read reports → collect_records
  → each record as a contract interaction → interaction_problems(committed spec)   (drift, undocumented)
  → documented operations − exercised ones → uncovered → generate_tests_from_openapi(only uncovered)
  → records with paths mapped to committed templates → records_to_openapi   (inferred document)
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
  a lazy import → extra under `[project.optional-dependencies]` in `pyproject.toml` and `dev.toml`, and the
  package in `.github/requirements/ci.in` (regenerate `ci.txt`) so CI runs its tests → executor registration →
  tests with `pytest.importorskip` plus the missing-dependency path.
- **MCP tool**: add an `MCPToolSpec` and handler to `APITESTKA_TOOLS`, then tests in `test/test_mcp_server/`.
- **CLI subcommand**: add `_cmd_<name>` and a subparser in `build_parser()` (`cli/cli_main.py`), then
  tests in `test/test_cli/`.
- **Mock routes / runtime plugins**: `flask_mock_server_instance.add_router()` (or `add_dynamic_route()`,
  `add_template_route()`); `WebSocketRoute` (reply map, fallback or `handler`) and `GrpcStubServer.register()` /
  `register_server_stream()` for scripted protocol endpoints; `AT_add_package_to_executor` registers an installed
  package's members once the package gate lets it through (§7).

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
- **LoadDensity (subprocess, this repo depends on it)**: `apitestka load run` / `AT_run_load_test`
  (`integrations/load_density_runner.py`) run `python -m je_load_density --execute_file <file>` (LoadDensity's
  hidden legacy flag, guarded by its `test/test_legacy_cli_contract.py`) with `PYTHONIOENCODING=utf-8` and the
  action file's folder as cwd. The file is `{"load_density": [["LD_start_test", {...}],
  ["LD_generate_summary_report", {"report_name": <absolute path without .json>}]]}`. `LD_start_test` gets
  `user_detail_dict.user` (`fast_http_user` / `http_user`), `tasks: {"mode": "sequence"|"weighted", "tasks": [...]}`,
  `user_count`, `spawn_rate`, `test_time`; each task uses `method`, `request_url` (absolute: the HTTP users have
  no base host), `name`, `params`, `headers`, `cookies`, `json`, `data`, `timeout`, `allow_redirects`, `verify`
  and `assertions: [{"type": "status_code", "value": N}]` (`integrations/load_density.py`). The run is judged
  from `<report_name>.json`: `totals.requests`, `totals.failure_rate`, `latency_overall.p95_ms`, because
  LoadDensity exits with 0 even when an action fails. `test/test_integrations/test_load_density.py` checks this
  side against a stand-in package that follows the contract; LoadDensity lists APITestka in its own §6.
- **ActionCore (this repo depends on it)**: `je_action_core` (Integration-Automation/ActionCore) holds the executor,
  command registry, package manager and gate, callback executor, action-file reading and writing, file listing and
  the TCP action server. APITestka uses all of them, with these settings:
  - **executor**: document key `api_testka`, `executor_list_error` for every bad list, `LegacyActionParser` with
    `executor_data_error`, plain record keys, `LoggingReporter(apitestka_logger)`, and `strip_runner_metadata` as
    the action rewrite;
  - **registry**: functions only;
  - **package manager**: `<package>_<member>` names, functions, builtins and classes, the gate on, all errors
    logged;
  - **callback executor**: legacy checks, a failure returns `None`;
  - **socket server**: reads the 8192-byte prefix, answers every error.

  It is a PyPI dependency (`je_action_core>=0.0.1`; hash-locked in `.github/requirements/ci.txt`). ActionCore lists
  APITestka in its own §6.
- **Sibling executors** share the action-list shape and the `Return_Data_Over_JE` socket terminator,
  but differ in command prefix (`AT_` here, `LD_` LoadDensity, `MT_` MailThunder, `FA_` FileAutomation),
  dict key (`api_testka` here) and builtins policy: APITestka registers no Python builtins (explicit
  allowlist); LoadDensity, MailThunder and WebRunner register the same `SAFE_BUILTINS` allowlist.
  APITestka and WebRunner put the same package gate in front of `*_add_package_to_executor` (workspace X-12).

## 7. Design constraints

- Command maps are explicit allowlists. No `eval()` or `exec()` on untrusted input. Validate socket
  payloads (CLAUDE.md § Coding Standards › Security (Mandatory)).
- `AT_add_package_to_executor` / `AT_add_package_to_callback_executor` pass the package gate in
  `utils/package_manager/package_manager_class.py` before importing: `executor.allow_packages(...)` and
  `executor.set_allow_arbitrary_packages(...)` are Python-only switches, never `AT_*` commands, so an action
  file cannot open its own gate. Unconfigured (`None`), any package loads with a `DeprecationWarning`.
- Parse XML with `defusedxml`. Every `requests` call passes a `timeout=`. No `verify=False` without a
  justification comment. No `shell=True` (§ Security (Mandatory); § Static Analysis Compliance › Security).
- Extend through `add_command_to_executor` or new `AT_` commands rather than reshaping the core map
  (§ Software Engineering Practices; § Common Development Workflows › Adding a New Executor Command).
- Import heavy optional dependencies lazily (PySide6, websockets, grpcio, anthropic, jsonschema, mcp).
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
