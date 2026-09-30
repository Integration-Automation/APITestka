# progress.md: APITestka

Outstanding work only. When an item is done, delete it in the same commit and add a `#done` entry to `docs/updates/` (format and query commands: `docs/updates/README.md`). No finished items, no history, no rules (rules live in `CLAUDE.md`).
Item numbers (`#n`) are never reused. Tags: [DECIDE] needs the owner's decision, [BLOCKED] waits on something else, [UNVERIFIED] observed but not confirmed.
Cross-repo and workspace items live in `D:\Codes\progress.md` (relevant here: X-12, X-13).

## Open

- **#3** [DECIDE] The PyPI classifier still says `Development Status :: 2 - Pre-Alpha`.
- **#6** GUI redesign: restructure and restyle. `gui/main_widget.py` is one 605-line widget (over the 500-line limit) with six flat tabs. It should become a sidebar-navigated window with a request/response split view, and history and environment panels docked (`gui/history_panel.py`, `gui/env_manager_model.py` exist but are not wired in). It needs a refreshed theme (`gui/main_window.py:21` hard-codes `dark_amber.xml`), pages for the newer features (#8–#13), and all four language wrappers (English, Traditional Chinese, Simplified Chinese, Japanese). `APITestkaWidget` stays the embeddable entry point (PyBreeze contract, `architecture.md` §6).
- **#13** Test-as-spec full loop. The pieces exist separately (`cli/import_specs.py` spec → actions, `spec/records_to_openapi.py` records → spec, `diff/contract_diff.py`, `spec/openapi_changelog.py`), but no single flow runs the tests, infers the spec, checks it against the committed spec, fails on drift, and generates actions for uncovered operations. Depends on #7.
