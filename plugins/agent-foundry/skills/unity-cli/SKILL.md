---
name: unity-cli
description: Drive the experimental `unity` command-line interface for Editor and module installs, project open/build/test/run, connected-Editor commands, licensing, diagnostics, and CI automation. Use when a task needs Unity work from a terminal rather than the Editor UI - installing or listing Editors and modules, running EditMode/PlayMode tests headlessly, batch-mode builds, inspecting connected Editor instances, machine-readable output for scripts, CLI exit codes or environment variables, or migrating off the legacy Unity Hub CLI.
---

# Unity CLI

Run Unity from a terminal: install Editors and modules, open/build/test/run
projects, talk to connected Editor instances, and produce machine-readable
output for automation.

## Transport priority — read first

The CLI is **not** the default way to inspect or mutate a Unity project. Global
rules put it third:

1. **Unity MCP** — first choice for all Editor/project inspection and mutation.
2. **UnitySkills REST** — fallback; prove exact project identity, follow its
   dry-run/diff/risk flow.
3. **Unity CLI (this skill)** — pinned CLI and file inspection.

Never perform the same mutation through two transports. Prefer the CLI when the
work is genuinely terminal-shaped: installs, headless test/build runs, CI, or
querying state while no MCP connection exists.

## The CLI is experimental — verify before trusting

Version on this machine at last check: **1.0.0-beta.3**. Commands and flags
move between releases.

```bash
unity --version
unity <command> --help
```

Installed-version `--help` and current official Unity docs are authoritative.
They override this skill and the snapshot below. When a documented flag is
missing from `--help`, believe `--help`.

Deep reference for install options, module management, editor listing, and Hub
CLI migration (snapshot from 2026-07-31, older than the installed CLI):

```bash
rg -n "install-modules|exit codes|environment variables|Hub CLI|templates" \
  "<optional-local-reference-path>"
```

Search the section you need; do not load the whole file.

## Automation defaults

Always pass these in scripts, CI, and any non-interactive run:

```bash
unity <command> --json --non-interactive --no-banner
```

- `--format <human|json|tsv|ndjson>`; `--json` is shorthand for `--format json`.
- `--format ndjson` streams typed progress frames then a final result frame —
  use it for long installs instead of parsing progress animation.
- Never parse human-format progress output.

Environment equivalents (a flag beats its variable): `UNITY_FORMAT`,
`UNITY_QUIET`, `UNITY_NO_BANNER`, `UNITY_NON_INTERACTIVE`, `UNITY_PROJECT_PATH`,
`UNITY_CLOUD_ORG`, `UNITY_PROXY`, `UNITY_INSTALL_RETRIES`, `UNITY_NO_ELEVATE`
(Windows), `UNITY_NO_UPDATE_CHECK`, `UNITY_EDITOR_VERSION`, `UNITY_ARCHITECTURE`,
`UNITY_TEST_TIMEOUT`.

Unattended auth uses `UNITY_SERVICE_ACCOUNT_ID` + `UNITY_SERVICE_ACCOUNT_SECRET`.
Never commit those; use CI secret storage.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Success |
| `1` | General error — inspect stderr |
| `2` | Usage error: bad flag, bad value, missing required argument |
| `3` | Auth failure: rejected sign-in or expired session |
| `4` | Configuration required: valid args, but a preference/context is unset |
| `6` | Primary operation failed: install failed, tests failed, Editor error exit |
| `130` | Interrupted (SIGINT / Ctrl+C) |
| `143` | Terminated (SIGTERM — `kill`, CI timeout) |

Branch on the code, not on message text. `6` is the one that means "the thing
you asked for ran and failed" — distinguish it from `2` (you called it wrong).

## Risk tiers

Match the global Unity risk model before running anything.

**Read-only — safe to run without approval:**
`status`, `editors` (list), `releases`, `modules list`, `license`, `env`,
`doctor`, `diagnose`, `logs`, `projects` (list), `list`, `changelog`,
`command` with no argument (lists available commands), any `--help`.

**Needs plan approval:** `test`, `run`, `command <cmd>` (executes inside a live
Editor), `open`, `config`, `install-path`, `templates` edits.

**Needs explicit target approval:** `install`, `install-modules`, `uninstall`,
`editor module remove`, `build`, `upgrade`, `self-uninstall`, `auth` sign-in/out,
anything touching Unity Cloud.

`build`, `run`, and `test` spawn a real Editor in batch mode and can write into
the project. Treat their output paths as declared, owned paths.

## Command map

| Area | Commands |
|---|---|
| Editors & modules | `install`/`i`, `install-modules`/`im`, `uninstall`/`u`, `editors`/`e`, `editor`, `modules`, `install-path`/`ip`, `releases` |
| Projects | `open`, `run`, `build`, `test`, `projects`/`p`, `templates`/`t` |
| Connected Editor | `status`, `command`/`cmd`, `list`, `pipeline`/`pipe`, `mcp` |
| Account & cloud | `auth`/`a`, `license`, `cloud` |
| Diagnostics | `doctor`, `diagnose`, `logs`, `env`, `bug`, `cache` |
| CLI lifecycle | `upgrade`, `self-uninstall`, `changelog`, `config`, `language`, `completion`, `analytics`, `shell` |

## Common runs

**Headless tests with a report** — `--mode` omitted uses the Editor default:

```bash
unity test "<project>" --mode EditMode --output test-results.xml \
  --timeout 900 --json --non-interactive --no-banner
```

Exit `6` means tests ran and failed; read the NUnit XML, not stdout.

**Batch build** — Unity has no built-in command-line build, so
`--execute-method` is required and your static C# method must honor
`-buildOutput` itself:

```bash
unity build "<project>" --target StandaloneWindows64 \
  --execute-method Builder.PerformBuild --output-path "<out>" \
  --log-file "<log>" --non-interactive
```

**Inspect live Editors before assuming which one is connected:**

```bash
unity status --json
```

**Run a Pipeline-registered command inside a connected Editor:**

```bash
unity command --project-path "<project>" --timeout 30 --json   # list first
unity command <cmd> [args...] --project-path "<project>" --json
```

**Install an Editor with modules (explicit target approval required):**

```bash
unity install 6000.0.62f1 --json --non-interactive
unity install-modules --version 6000.0.62f1 --json --non-interactive
```

**Many commands in one warm process** — `unity shell` avoids repeated startup
cost when issuing a batch of queries.

## Working rules

- Resolve and state the exact project path before any project command; never
  guess between candidates. `--project-path` and `UNITY_PROJECT_PATH` both set it.
- Editor version comes from `ProjectVersion.txt` unless `--editor-version` or
  `-e/--editor-path` overrides it. Say which one you used.
- `--allow-install` on `test` will silently install a missing Editor version —
  that is a high-risk install, so ask before passing it.
- Do not run a mutating CLI command while an Editor holds the same project
  through MCP or UnitySkills.
- Report the exit code and the report/log path with any failure, not a summary
  of console text.
