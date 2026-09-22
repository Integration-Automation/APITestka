# progress.md: APITestka

Outstanding work only. When an item is done, delete it in the same commit and add a `#done` entry to `docs/updates/` (format and query commands: `docs/updates/README.md`). No finished items, no history, no rules (rules live in `CLAUDE.md`).
Item numbers (`#n`) are never reused. Tags: [DECIDE] needs the owner's decision, [BLOCKED] waits on something else, [UNVERIFIED] observed but not confirmed.
Cross-repo and workspace items live in `D:\Codes\progress.md` (relevant here: X-1, X-12, X-16).

## Open

- **#1** Add the licence text: `licenses/APITestka_LICENSE` is 0 bytes and there is no root `LICENSE`, while `pyproject.toml` declares `license-files = ["LICENSE"]`.
- **#2** `CLAUDE.md` "Architecture & Design Patterns" (≈:27-51) is outdated: it does not mention `ai/`, `cli/`, `mcp_server/`, `pytest_plugin/` or the GraphQL / SSE / WebSocket wrappers.
- **#3** [DECIDE] The PyPI classifier still says `Development Status :: 2 - Pre-Alpha`.
- **#5** `dev.toml` (the `je_api_testka_dev` channel) has no console scripts, no `pytest11` entry point and only the `gui` extra, so the dev package lacks `apitestka`, `apitestka-mcp` and the pytest plugin.
