# docs/updates: update log index

`progress.md` holds only work that is **not done yet**. Everything that *was* done (what changed, measured numbers, decisions, snapshots) is recorded here: **one batch file per month**, one entry per piece of work, each entry with a fixed-format ID and tags, and one row per entry in the index below.

> No TODOs here. If an entry mentions something still open, it only points to it (e.g. "open item: `progress.md` #3"); the item itself lives in `progress.md`.

## How to query

Run from the repository root:

| To find | Command |
|---|---|
| every entry, one line each | `rg -n "^## U-2" docs/updates` |
| entries of one type | `rg -n "^## U-2.*#done" docs/updates` |
| entries with a topic tag | `rg -n "^## U-2.*#<tag>" docs/updates` |
| one day or one month | `rg -n "^## U-202609" docs/updates` |
| the full text of one entry | `rg -n -A 60 "^## U-20260922-01" docs/updates` |
| any keyword | `rg -n "keyword" docs/updates` |

Without `rg`: `git grep -n "^## U-2" -- docs/updates`, or in PowerShell `Select-String -Path docs/updates/*.md -Pattern '^## U-2'`.

## Entry format

```markdown
## U-YYYYMMDD-NN · YYYY-MM-DD · one-line title · #type #topic

- **What**: ...
- **Result / numbers**: ...
- **Files**: `path` ...
- **Evidence**: commit, file:line, link ...
- **Open items**: none / see `progress.md` ...
```

- **ID**: `U-` + date + two-digit sequence for that day. IDs are never renumbered or reused, so code comments and other documents can cite them.
- **Type tag** (exactly one): `#done` finished `progress.md` item, `#snapshot` measurement or inventory, `#decision`, `#incident`, `#migration`, `#docs`, `#release`.
- Topic tags are free-form (`#mcp`, `#wayland`, ...).
- Keep conclusions, numbers, files and evidence; drop the reasoning trail and dead ends.

## Batch rules

1. One file per month: `docs/updates/YYYY-MM.md`. Append new entries at the end.
2. Over about 800 lines, continue in `YYYY-MM-b.md` (then `-c`) and list it in the batch table below.
3. **Claim the ID under a lock.** Several sessions may write this log at the same time (for example parallel autonomous runs), and without a lock two of them pick the same number:
   1. `mkdir docs/updates/.id-lock`. Creating a directory is atomic, so only one writer succeeds. If it already exists, someone else is claiming: wait a few seconds and retry. A lock older than 10 minutes is stale and may be removed.
   2. Find the day's last number with `rg -n "^## U-YYYYMMDD" docs/updates` and write the heading line and the index row.
   3. `rmdir docs/updates/.id-lock`, then fill in the body. Git never tracks the empty lock directory.
   4. Before committing, `rg -c "^## U-<your ID>" docs/updates` must report one match in total. If not, renumber your entry under the lock and fix its index row. Whoever merges a branch renumbers entries that reuse an ID.
4. **One line per index row**: title only (about 60 characters), no summary.
5. Never rewrite a recorded entry. Correct it with a new `#decision` or `#incident` entry and add "→ corrected in U-..." to the old one.

## When a `progress.md` item is done

In the same commit: delete the item from `progress.md`, add a `#done` entry here that names it, and add its index row.

---

## Index (newest first)

| ID | Date | Title | Tags | Batch |
|---|---|---|---|---|
| U-20261001-27 | 2026-10-01 | The publish lock is resolved with the 7-day cut-off the other locks use | #ci #security #X-13 | [2026-10](2026-10.md) |
| U-20261001-26 | 2026-10-01 | Both publish jobs build with the locked setuptools | #done #ci #security #X-13 | [2026-10](2026-10.md) |
| U-20261001-25 | 2026-10-01 | Both publish jobs install hash-locked build tooling | #done #ci #security #X-13 | [2026-10](2026-10.md) |
| U-20261001-24 | 2026-10-01 | The sdist carries no tests | #done #packaging #X-13 | [2026-10](2026-10.md) |
| U-20261001-23 | 2026-10-01 | CI publishes je_api_testka_dev from the dev branch | #release #ci #X-13 | [2026-10](2026-10.md) |
| U-20261001-22 | 2026-10-01 | je_action_core comes from PyPI | #done #build #L-6 | [2026-10](2026-10.md) |
| U-20261001-21 | 2026-10-01 | je_action_core pin moves to 19bfe0a | #build #L-6 | [2026-10](2026-10.md) |
| U-20261001-20 | 2026-10-01 | Executor and its helpers move to je_action_core | #migration #executor #L-6 | [2026-10](2026-10.md) |
| U-20261001-19 | 2026-10-01 | Unknown executor commands raise APITesterExecuteException | #bugfix #executor #L-6 | [2026-10](2026-10.md) |
| U-20261001-18 | 2026-10-01 | GUI checked on a real display; four fixes | #bugfix #gui | [2026-10](2026-10.md) |
| U-20261001-17 | 2026-10-01 | httpx records request_url as text | #bugfix #spec | [2026-10](2026-10.md) |
| U-20261001-16 | 2026-10-01 | Package gate in front of AT_add_package_to_executor | #change #security #X-12 | [2026-10](2026-10.md) |
| U-20261001-15 | 2026-10-01 | The package passes its lint rules | #change #lint | [2026-10](2026-10.md) |
| U-20261001-14 | 2026-10-01 | reformat_xml_file raises its own exception for bad XML | #bugfix #gui | [2026-10](2026-10.md) |
| U-20261001-13 | 2026-10-01 | Every workflow job has a timeout | #ci #tests | [2026-10](2026-10.md) |
| U-20261001-12 | 2026-10-01 | GUI widget tests run on Linux CI too | #done #ci #gui | [2026-10](2026-10.md) |
| U-20261001-11 | 2026-10-01 | GUI widget tests broke Linux CI (libEGL); now skipped there | #incident #ci #gui | [2026-10](2026-10.md) |
| U-20261001-10 | 2026-10-01 | Development status classifier moves to Beta | #done #packaging | [2026-10](2026-10.md) |
| U-20261001-09 | 2026-10-01 | GUI redesign: sidebar pages, request workspace, themes | #done #gui | [2026-10](2026-10.md) |
| U-20261001-08 | 2026-10-01 | Test-as-spec loop: drift, coverage and generated tests | #done #openapi #spec | [2026-10](2026-10.md) |
| U-20261001-07 | 2026-10-01 | Per-endpoint latency trends and anomaly detection | #done #trend #report | [2026-10](2026-10.md) |
| U-20261001-06 | 2026-10-01 | Load-test bridge to LoadDensity | #done #load #cross-project | [2026-10](2026-10.md) |
| U-20261001-05 | 2026-10-01 | Anthropic reference AI backend and backend selection | #done #ai | [2026-10](2026-10.md) |
| U-20261001-04 | 2026-10-01 | Pact-style bidirectional contract testing | #done #contract | [2026-10](2026-10.md) |
| U-20261001-03 | 2026-10-01 | Mock server serves WebSocket and gRPC endpoints | #done #mock #grpc #websocket | [2026-10](2026-10.md) |
| U-20261001-02 | 2026-10-01 | Imported, scaffolded and AI-generated actions run as they are | #bugfix #executor | [2026-10](2026-10.md) |
| U-20261001-01 | 2026-10-01 | records_to_openapi reachable from the CLI and MCP | #done #openapi #cli #mcp | [2026-10](2026-10.md) |
| U-20260925-03 | 2026-09-25 | Python classifiers list every version CI tests | #packaging #tests | [2026-09](2026-09.md) |
| U-20260925-02 | 2026-09-25 | dev_requirements.txt pins the package's PySide6 | #deps #tests | [2026-09](2026-09.md) |
| U-20260925-01 | 2026-09-25 | Dependabot waits 7 days before proposing a new release | #ci #security #deps | [2026-09](2026-09.md) |
| U-20260924-02 | 2026-09-24 | Keep checkout credentials only in the job that pushes | #ci #security | [2026-09](2026-09.md) |
| U-20260924-01 | 2026-09-24 | Move CI to Node 24 actions pinned by commit | #ci #security #deps | [2026-09](2026-09.md) |
| U-20260923-14 | 2026-09-23 | MCP server runs on mcp 1.x and 2.x; extra allows <3 | #done #mcp #compat | [2026-09](2026-09.md) |
| U-20260923-13 | 2026-09-23 | CI installs from a hash-locked file; dev merged into main | #done #ci #release | [2026-09](2026-09.md) |
| U-20260923-12 | 2026-09-23 | HTML report escapes what the API under test returns | #bugfix #security | [2026-09](2026-09.md) |
| U-20260923-11 | 2026-09-23 | Reports and project templates are written as UTF-8 | #bugfix #encoding | [2026-09](2026-09.md) |
| U-20260923-10 | 2026-09-23 | XMLParser raises its own exception for bad input | #bugfix | [2026-09](2026-09.md) |
| U-20260923-09 | 2026-09-23 | TLS certificates are verified by default | #change #security | [2026-09](2026-09.md) |
| U-20260923-08 | 2026-09-23 | Action JSON is read and written as UTF-8; bad files raise | #bugfix #encoding | [2026-09](2026-09.md) |
| U-20260923-07 | 2026-09-23 | Socket server stops reading sys.argv; its documented command line works | #change #bugfix #socket | [2026-09](2026-09.md) |
| U-20260923-06 | 2026-09-23 | CLAUDE.md package tree matches the code | #done #docs | [2026-09](2026-09.md) |
| U-20260923-05 | 2026-09-23 | APITestka.log moves out of the working directory; root logger left alone | #done #logging | [2026-09](2026-09.md) |
| U-20260923-04 | 2026-09-23 | dev.toml carries the scripts, plugin and extras again | #done #packaging | [2026-09](2026-09.md) |
| U-20260923-03 | 2026-09-23 | Licence texts restored; root LICENSE ships in the wheel | #done #packaging | [2026-09](2026-09.md) |
| U-20260923-02 | 2026-09-23 | PySide6 6.11.2 and Dependabot on dev | #done #deps #ci | [2026-09](2026-09.md) |
| U-20260923-01 | 2026-09-23 | Keep the mcp extra below 2.0 and test the server end to end | #done #mcp #bugfix | [2026-09](2026-09.md) |
| U-20260922-04 | 2026-09-22 | Contract test for the legacy CLI flags | #done #tests | [2026-09](2026-09.md) |
| U-20260922-03 | 2026-09-22 | Point project URLs at the current repository | #done #metadata | [2026-09](2026-09.md) |
| U-20260922-02 | 2026-09-22 | Stop tracking .idea/ | #done #housekeeping | [2026-09](2026-09.md) |
| U-20260922-01 | 2026-09-22 | Adopt progress/architecture/docs-updates rules | #docs #migration | [2026-09](2026-09.md) |

## Batches

| File | Period | Entries |
|---|---|---:|
| [2026-10.md](2026-10.md) | 2026-10 | 27 |
| [2026-09.md](2026-09.md) | 2026-09 | 23 |
