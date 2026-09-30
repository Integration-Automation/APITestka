# progress.md: APITestka

Outstanding work only. When an item is done, delete it in the same commit and add a `#done` entry to `docs/updates/` (format and query commands: `docs/updates/README.md`). No finished items, no history, no rules (rules live in `CLAUDE.md`).
Item numbers (`#n`) are never reused. Tags: [DECIDE] needs the owner's decision, [BLOCKED] waits on something else, [UNVERIFIED] observed but not confirmed.
Cross-repo and workspace items live in `D:\Codes\progress.md` (relevant here: X-12, X-13).

## Open

- **#14** [BLOCKED] The Qt widget tests (`test/test_gui/test_gui_widgets.py`) skip on the Ubuntu CI jobs because the runner has no `libEGL.so.1`. Add `sudo apt-get install -y libegl1` for Linux in `.github/workflows/ci.yml` before "Run tests". Blocked: `ci.yml` (and `publish.yml`, `test/test_workflow_actions.py`) hold uncommitted `timeout-minutes` edits from another session, which should be committed first.
