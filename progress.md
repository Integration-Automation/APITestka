# progress.md: APITestka

Outstanding work only. When an item is done, delete it in the same commit and add a `#done` entry to `docs/updates/` (format and query commands: `docs/updates/README.md`). No finished items, no history, no rules (rules live in `CLAUDE.md`).
Item numbers (`#n`) are never reused. Tags: [DECIDE] needs the owner's decision, [BLOCKED] waits on something else, [UNVERIFIED] observed but not confirmed.
Cross-repo and workspace items live in `D:\Codes\progress.md` (relevant here: X-12, X-13).

## Open

- **#15** [BLOCKED: two releases must ship the warning first] Flip the package gate's default to refuse packages outside the allowlist.
  - Where: `PackageManager.allow_arbitrary_packages` starts as `None` (load, with a `DeprecationWarning`) in `je_api_testka/utils/package_manager/package_manager_class.py`. Set it to `False` and drop the warning branch in `_check_allowed`.
  - Docs to update: the "Package gate" bullet in the three READMEs, the "Package Gate" section of `docs/source/{Eng,Zh}/doc/executor/executor_doc.rst`, and `architecture.md` §7.
  - Timing: the warning is first released in the version after 0.0.145 (`origin/main` `pyproject.toml`). Flip once two releases after that one have shipped it.
  - Decide first: how a user who only runs action files (`apitestka run`, `python -m je_api_testka -e`, the socket server) allows a package once there is no Python host to call `executor.allow_packages(...)`.
