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

### Static Analysis Compliance (SonarQube / Codacy / Pylint / Bandit)

All code must pass static analysis without warnings from SonarQube, Codacy, Pylint, Flake8, and Bandit. Adhere to the following rules:

#### Reliability & Bug Risk
- **No bare `except:` clauses** — always catch specific exception types (`except ValueError:`), never `except:` or `except Exception:` without re-raise/log (S5754, E722)
- **No mutable default arguments** — use `None` as default and assign inside the function (e.g., `def f(x=None): x = x or []`) (W0102)
- **Always close resources** — use `with` context managers for files, sockets, sessions; never rely on garbage collection (S2095, R1732)
- **No unreachable code** — remove statements after `return`, `raise`, `break`, `continue` (S1763, W0101)
- **No identical branches in `if/elif/else`** — collapse duplicates (S1871)
- **No assignment in conditions** — `if x = func():` is forbidden; assign first (S1656)
- **Comparisons must not always be true/false** — avoid `if x is None and x == 5:` patterns (S2589)
- **Use `is`/`is not` for `None`, `True`, `False`** — never `== None` (E711)
- **No self-comparison** — `if x == x:` is a bug (S1764)
- **Loop variables must be used** — if unused, name them `_` (W0612)

#### Security (Bandit / SonarQube Security Hotspots)
- **No `pickle.loads()` on untrusted input** — use JSON instead (B301)
- **No `subprocess` with `shell=True`** — pass arg list (B602, S4721)
- **No `random` module for security** — use `secrets` module for tokens/keys (B311, S2245)
- **No hardcoded `0.0.0.0` bindings** without explicit comment justifying it (B104)
- **No `assert` for runtime validation** — assertions are stripped with `-O`; raise exceptions instead (B101)
- **No `tempfile.mktemp()`** — use `NamedTemporaryFile` or `mkstemp()` (B306)
- **No `requests` calls without timeout** — always pass `timeout=` (S4502)
- **No `verify=False` on TLS connections** without explicit justification comment (B501)
- **SQL/XPath/LDAP must be parameterized** — never f-string user input into queries (S3649)

#### Maintainability & Complexity
- **Cognitive complexity ≤ 15 per function** — refactor nested loops/conditions into helpers (S3776)
- **Cyclomatic complexity ≤ 10** (C901)
- **Function parameters ≤ 7** — group related params into a dataclass/dict (S107, R0913)
- **Function length ≤ 50 lines** of code excluding docstrings (R0915)
- **File length ≤ 500 lines** — split large modules (C0302)
- **Class methods ≤ 20** — split large classes (R0904)
- **Nesting depth ≤ 4 levels** (S134)
- **No duplicate string literals** appearing 3+ times — extract to a module-level constant (S1192)
- **No duplicate code blocks** ≥ 6 lines — extract to a function (common-duplicate)
- **Boolean parameters discouraged** — prefer enums or two named functions (S2301)

#### Naming & Style (Pylint / Flake8)
- **Module names**: `lower_snake_case`, no hyphens (C0103)
- **Constants**: `UPPER_SNAKE_CASE` (C0103)
- **Class names**: `PascalCase` with no underscores (C0103)
- **Avoid single-letter variable names** outside short loops/comprehensions (`i`, `j`, `k` ok; `x`, `y` not for business logic)
- **Line length ≤ 120 characters** (E501)
- **Two blank lines between top-level functions/classes**, one between methods (E302, E305)
- **No trailing whitespace, no tabs** (W291, W191) — use 4 spaces
- **Imports order**: stdlib → third-party → local, separated by blank lines, alphabetized (I100, I201)
- **No wildcard imports** (`from x import *`) outside `__init__.py` (F403, W0401)

#### Code Smells
- **No `TODO`/`FIXME` without an issue link** — `# TODO(#123): description` (S1135)
- **No commented-out code** — delete it; git preserves history (S125)
- **No `print()` in library code** — use the `logging` module (T201)
- **No magic numbers** — extract to named constants (e.g., `DEFAULT_TIMEOUT_SECONDS = 30`) (R2004)
- **Functions returning `None` should not have explicit `return None`** (R1711)
- **Use f-strings, not `%` or `.format()`** for new code (UP032)
- **Use `pathlib.Path` instead of `os.path`** for new code where possible (PTH)
- **Avoid `len(x) == 0`** — use `not x` for empty containers (C1801)

#### Type Safety
- **All public functions need type hints** on parameters and return types (mypy strict)
- **No `Any` in public APIs** — use `TypeVar`, `Protocol`, or concrete types
- **Use `Optional[T]` (or `T | None`)** explicitly; never imply nullability

#### Test Code Exemptions
- Test functions may exceed cognitive complexity for table-driven assertions
- `assert` is allowed and expected in test files
- Magic numbers are acceptable in test fixtures

## Testing Guidelines

- **Every new feature, fix, or refactor MUST ship with unit tests in the same commit.**
  - New module → add a corresponding `test/test_<area>/test_<module>.py`.
  - Bug fix → add a regression test that fails before the fix and passes after.
  - Refactor → existing tests must still pass; add coverage for any newly-exposed branches.
- Place tests under the matching subdirectory (`test/test_utils/`, `test/test_requests/`, etc.); create new subpackages with a `__init__.py` when introducing a fresh area.
- Tests for **optional-dependency** modules (e.g. `websockets`, `jsonschema`) must:
  - Skip gracefully via `pytest.importorskip("<package>")` when the dep is missing, AND
  - Cover the "dependency missing" error path by monkeypatching the import to raise `ImportError`.
- Use the existing fixtures in `test/conftest.py` (`mock_url`, `clean_test_records`, `assert_valid_response`, `run_report_suite`) rather than rolling new ones.
- Run `pytest -x` locally before committing; CI runs the full matrix on Python 3.10–3.14.
- A commit that introduces production code without tests is incomplete and should not be pushed.

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
