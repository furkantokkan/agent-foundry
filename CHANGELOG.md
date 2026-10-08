# Changelog

## 0.9.2 - 2026-10-08

- Enforce the two-Editor limit without a race. Agents open Editors only
  through the new `unity-cli/scripts/unity_editor_open.py`. It holds an
  OS-held lock in the repository's Git common dir, shared by every worktree,
  through the Editor count, `unity open`, and the new PID. The OS drops the
  lock when the script exits, so there is no stale lock to reclaim and no lock
  file is ever deleted. Editors are counted from the process table, which also
  sees Editors `unity status` cannot reach. Running Editors stay the slots, so
  closing an Editor frees its slot. A launch whose Editor has not appeared yet
  keeps its slot as a reservation, read and written only under the lock, until
  the Editor appears, so a slow start cannot be overtaken. Reservations never
  expire by age; after a failed launch, `--clear-reservation` frees the slot.
  The script fails closed: an unreadable process table, a Unity process
  without a readable command line, a failing `git`, or an unexpected error
  gives an OPEN_FAILED verdict and opens nothing. Import workers are detected
  by their `-name AssetImportWorkerN` argument, so an Editor whose path
  contains that word still counts. An unquoted path with a ` -Name` part is
  matched against the Unity project on disk. The Git fallback is decided from
  the filesystem, not from git's localized message. A reservation for a
  removed project is dropped, and a failed tidy-up after a successful open no
  longer turns OPENED into OPEN_FAILED.
- Code lanes report `COMPILE_UNVERIFIED` to the integration owner only when
  the seeded Roslyn check returns it. `COMPILE_OK` needs no Unity compile.
- Remove the leftover `unity-preflight/agents/openai.yaml`. The skill was
  retired in 0.4.0, but this Codex UI metadata kept an empty `unity-preflight`
  folder shipping. Validation now rejects any packaged skill folder without
  `SKILL.md`. This supersedes the unmerged 0.4.1 PR #6.
- These fixes answer the review findings on 0.9.0, on this PR's first draft,
  and an independent review of the script. Validation:
  - package/hash checks;
  - 28 new unit tests, stable over three runs, including:
    - two separate processes opening at once with a limit of 1: one opens and
      the other gets LIMIT_REACHED;
    - a slow launch keeps its slot until its Editor appears, and an old
      reservation keeps it until it is cleared;
    - a lock holder that is killed releases the lock;
    - real Git worktrees under a non-ASCII path with a space;
    - fail-closed cases: process table, `git`, and an unstartable CLI;
  - a read-only scan of this machine's Editors that matches the WMI process
    list.

## 0.9.1 - 2026-10-08

- Add portable model-routing guidance for Sonnet 5.5 through the `sonnet`
  family alias and `gpt-6.1-sol` for bounded Codex work. Keep existing host
  policies, explicit user choices, task complexity, and reasoning effort in
  control. Orchestration loads these defaults only when no host/repository
  routing policy exists.
- Document Sonnet 5.5's Claude Code 2.1.284 minimum and session restart.
  Preserve Sonnet alias entries rather than pinning every skill to a version.
- First prepared as 0.8.2 on 2026-09-29; rebased onto 0.9.0 and renumbered.

## 0.9.0 - 2026-10-08

- Keep Unity Editors bounded during agentic work. `unity-cli` adds "Editor
  instances and worktrees": at most two Editors per repository, a status check
  before `unity open` and after a timeout, a recorded owner who closes the
  Editor, no `Temp/UnityLockfile` deletion, and Editor-free code lanes. A lane
  is seeded with `unity vcs git worktree add --seed full` plus the generated
  project files, so the Roslyn check runs there without Unity.
- Tracked orchestration runs Unity tasks as code lanes plus one integration
  checkout. That checkout owns the Editor, applies lane diffs in order, and
  runs final-stage tests in one shared batch.
- The three Unity role agents no longer request `isolation: worktree`. It
  created unseeded worktrees, and the compile check then told agents to open
  Unity there. The compile check's messages now point lanes to seeding.
- Validation scope: package/hash checks, the new compile-check message on a
  project without a Library, the shared-batch unit tests, and CLI dry runs of
  the seeding modes. No orchestration run is claimed.
- Make the Pipeline package (`com.unity.pipeline`) the default Editor bridge on
  Unity 6+. When it is missing, `unity-cli` installs it under the standing
  authorization in the checkout that owns the Editor, never in a code lane.
  Upgrades, pins, and removal keep their approval gates, and it is never
  installed below Unity 6. Readiness reports a missing package as a warning
  and names the install as the next action.
- Keep Pipeline Editor-only. Its runtime assemblies (`Unity.Pipeline`,
  `Unity.Pipeline.IlInterpreter`) have no platform restriction, so they are
  excluded from every player build with an `IFilterBuildAssemblies` filter.
  The runtime server (`enableInBuilds`) stays off. The facts come from the
  package's own source and documentation (0.6.0-exp.1); no build is claimed.

- Add five focused Unity reconstruction skills for grid drag/gate exits,
  composable board effects, transactional boosters, timed life economies,
  and grid level authoring with Undo, reload-safe drafts and runtime parity.
- Each includes an implementation recipe, configurable policy boundaries,
  failure/verification scenarios and Codex interface metadata. Add focused
  routing and update the core inventory to 98 skills.
- Validation scope: skill/package metadata, bundled references, export hashes
  and independent reconstruction scenarios; no new Unity/device test claims.

- Add reusable Unity ownership and authoring guidance for lifetimes, reentrant
  transitions, owned async work, data authority, committed transactions, UI
  previews/input, scoped Editor saves/tests, solver parity and pool identity.
- Route implementation, architecture and optimization skills to the shared
  reference; align async/data examples with its ownership rules.
- Validation: package/reference/hash checks and independent instruction review.
  This documentation change does not claim new Unity or device test results.

## 0.8.1 - 2026-09-28

- Drop the fixed "about an hour" session budget from 0.8.0. The rule is now to
  size the process to the work. Estimate the work and the process around it
  (batch cycles, reviews, decisions, waiting) separately, and restructure when
  the process costs more than the work, as when an hour of edits is planned as
  eight hours. The fast finish starts when the user asks to wrap up, or when
  waiting and repeated cycles keep extending the estimate, not at a time limit.

## 0.8.0 - 2026-09-28

- Fast finish. `agent-orchestration` gains "Time budget and fast finish": aim
  a session's remaining work at about an hour, estimate it from measured batch
  times, and group small fixes so that one batch means one implement -> verify
  cycle, with tests once at the end. Consult the decision owner at plan and
  end, not per batch, and never wait in-session for another owner's paths.
  When the estimate is larger, or the user asks to wrap up:
  - time-box the batch in flight (revert it when it only improved quality);
  - defer long or blocked chains to follow-up tasks with their specs;
  - verify once (Roslyn, then an Editor refresh for new files, then one shared
    test batch of the changed code's tests);
  - report in one short step.

  `implement-task` and `task-cycle` point to it. It never relaxes a close gate.
- Declared failures. A session whose in-progress change fails tests by design
  runs `unity_test_batch.py declare` (with an owner, tests, reason, and
  expiry). Other sessions' results still list those failures but mark them
  declared. A request whose only failures are declared by another owner is
  `FOREIGN_FAIL` (exit 9) instead of `FAIL`. A declaration never hides a
  failure from its own owner. A criterion that rests on declared failures stays
  `UNPROVEN` until a rerun after `undeclare`.
- The live-Editor batch run refreshes the Editor first when files were added.

## 0.7.0 - 2026-09-28

- A task whose session stopped is takeover-able, not locked. The lock protocol
  replaces "stale recovery" with "Liveness and takeover". The claim records the
  long-lived agent process that owns the conversation, with its start time,
  never the short-lived shell that ran the lock command, plus a heartbeat the
  owner renews at every step boundary. The owner has stopped when that process
  is gone or when no heartbeat or lifecycle write happened for the lease window
  (30 minutes unless the repository sets another).
- A waiting agent takes a stopped task over without asking. It moves the claim
  to the audit folder, acquires the lock, keeps the stopped owner's
  uncommitted changes, records the takeover in the lifecycle history, and
  continues the task through its lifecycle skill. An active task with no claim
  has no owner and never blocks.
- An owner that paused re-checks its token before its next write. A lost
  token means `LOCK_TAKEN_OVER`: write nothing more and queue behind the new
  owner.
- `agent-orchestration` takes over and finishes a stopped predecessor on the
  same paths before dispatching the successor, instead of waiting. It still
  waits at real gates (a user decision, a contract change, a protected-target
  approval). `task-status` reports such tasks as `takeover-able`.

## 0.6.0 - 2026-09-28

- Release the lock while waiting for tests. A lifecycle owner submits its
  final-stage tests with `unity_test_batch.py submit --no-wait`, records
  `Current phase: awaiting_tests` and `Pending test request`, releases the task
  lock and its paths, and waits with `wait --id`. Other agents can work on the
  same scripts in the meantime. On the result the owner re-acquires the lock
  as a new owner and re-reads state before using the evidence.
- `AWAITING_TESTS` is a stable handoff. `agent-orchestration` dispatches a
  successor queued on the same paths at that point instead of after the test
  result. A returning predecessor queues behind the current owner, and a
  failing base is reported to the successor's owner.
- Role agents that submit tests (verifier, bugfixer) return
  `AWAITING_TESTS <request-id>` to the lock holder, which resumes them with the
  result. `task-status` reports the phase and resumes a task that has no live
  waiter.
- The batch script re-hashes a request's files on every read of its result, so
  a result for bytes changed after the run reads as `STALE`. `--no-wait`
  queues a request without waiting.

## 0.5.0 - 2026-09-28

- Automatic verified closure: where the caller's user, global, or repository
  policy authorizes it (or an assignment carries
  `Close authority: automatic_verified`), `implement-task` and `task-cycle`
  close a task in the same lifecycle write that finds every gate green,
  recording `Closed by: automatic_verified_closure`. Without that
  authorization the `READY_TO_CLOSE` -> `task-done` handshake is unchanged.
  `task-cycle` closes tasks left in `ready_to_close` after re-checking the gates.
- `agent-orchestration` forwards the resolved close policy to delegated
  lifecycle owners through a new `Close authority` assignment field. Role
  agents never close.
- Add a shared final-stage Unity test batch
  (`unity-cli/scripts/unity_test_batch.py`, with tests). Sessions on one
  project queue their requests. A leader runs the Roslyn gate once, then one
  `unity test` per platform with the merged filter, and hands each request only
  its own tests. A request whose filter matches nothing is `NO_TESTS`, never a
  pass. Files changed after submit make the result `STALE`. An open Editor
  hands the merged plan to the leader session, which publishes a live-Editor
  report. An optional shadow runner project is also supported.
- Verification order for Unity changes: the Roslyn compile check first, Unity's
  own compile only on `COMPILE_UNVERIFIED`, and tests once at the end through
  the shared batch.

## 0.4.0 - 2026-09-28

- Unify `game-studio-orchestration` into one cross-domain `agent-orchestration`
  workflow (compatibility alias kept) and fold Unity readiness into `unity-cli`;
  the standalone `unity-preflight` skill and command are removed. Update
  project instructions that still call `unity-preflight` to call `unity-cli`.
- Add a Roslyn compile check (`unity-cli/scripts/unity_compile_check.py`). It
  compiles only the assemblies of changed files with `dotnet build` against
  `Library/ScriptAssemblies`, handles new/deleted files before Unity
  regenerates project files, ignores `.csproj` files of removed assemblies, and
  rebuilds dependencies whose compiled copy is older than their sources. It
  runs in seconds with the Editor open or closed, also below Unity 6.
- Unity test timing: implementation, repair, and bugfix loops use the compile
  check per edit; focused EditMode/PlayMode tests are written and run once in
  the final stage, then only failing tests re-run. Closure gates are unchanged.
- Route backend handoffs by the project's existing backend: Firebase projects
  use `firebase-game-backend`; `build-live-game` only when the project already
  uses or the user chooses Unity Gaming Services.
- Add the pre-Unity-6 version gate: below `6000.0`, MCP for Unity (`unityMCP`)
  is the approved live-Editor transport, with exact project/version identity
  proven before instance selection.
- Let `review-all-gdds` inherit the session model instead of pinning Fable.

## 0.2.0 - 2026-09-21

- Add 30 Unity specialist skills from `Unity-Technologies/skills` at revision
  `8d85172945197ee8bacbbfea44d6d64cad782004`, preserving Unity Companion
  License attribution and bundled references/resources.
- Expand `unity-cli` from the official baseline and keep Agent Foundry's exact
  project identity, explicit risk approval, machine-readable automation, and
  safer download-inspect-run installation rules.
- Make Unity CLI the mandatory control plane across preflight, implementation,
  verification, orchestration, roles, and global installation guidance. Install
  the official CLI when missing, use built-in `unity mcp` when needed, and keep
  legacy MCP/UnitySkills explicit-request-only instead of automatic fallbacks.
- Expand adaptive routing and package metadata to 123 core skills / 142 total
  skills. Validation covers inventory, manifests, references, JSON, provenance,
  private-path patterns, and installed CLI smoke checks.
## 0.1.4 - 2026-09-20

- Document Unity Liquid UI invocation, standalone installation, source-reference
  boundaries and adaptive routing; keep the generated catalog version current.

- Adapt the existing `game-feel-polish` skill to Unity UI Toolkit with widget,
  input, lifetime and reduced-motion guidance for Claude Code and Codex.
- Replace incomplete Unity code sketches with scoped system mappings; preserve
  time/camera ownership and cover cancellation, pooling and build checks.
- Record the upstream revision and update core plugin metadata to 0.1.3.
- Validation: package/frontmatter checks; no Unity runtime package or Editor
  behavior is claimed by this documentation release.

## 0.1.3 — 2026-09-11

- Add `game-feel-polish`, a core skill that packages the Liquid UI juice-kit architecture and tuned numbers (trauma screen shake, wall-clock hitstop and slow motion, rest-state tween helpers, hit flash, pooled damage numbers, pooled SFX banks, toast stacks, animated counters and lag bars, staggered menu intros, CRT screen looks) for Godot 4, with a Unity port guide and an A/B verification checklist.
- Add the `game-feel-polish` command adapter, Codex/ChatGPT interface metadata, catalog entry, adaptive-skills routing, and MIT attribution for the upstream kit.
- Bump the core plugin to 0.1.2 (93 skills) and correct the installation notes to list all three plugins.

## 0.1.2 — 2026-09-07

- Add AI 3D Foundry, an optional three-skill plugin for reference-first Blender modeling, image-to-textured-3D generation, and cost-aware AI scene assembly.
- Add local environment-token guidance and remove the Hunyuan script's command-line token parameter so credentials are not placed in shell history.
- Add marketplace entries, installation documentation, validation coverage, and MIT notices for the included upstream components.

## 0.1.1 — 2026-09-07

- Add Blender & Texture Foundry, an optional 16-skill plugin for modeling, PBR materials, UVs, baking, look development, rendering, Unity export, and CC0 texture research.
- Add install guidance, a Blender/texture catalog, plugin manifests, validation coverage, and MIT notices for the included upstream components.
- Add original texture-discovery guidance for choosing Poly Haven and ambientCG assets without copying unlicensed Poly Haven source code.

## 0.1.0 — 2026-09-07

- Publish a curated snapshot of 92 skills and 93 command adapters.
- Package shared skills for Codex and Claude Code, with seven Claude aliases and three Unity agent roles.
- Add a searchable catalog, install guidance, provenance manifest, and upstream MIT notices.
- Generalize local paths and project examples; exclude account configuration and marketplace caches.
- Add automated package validation. Full workflow behavior across runtimes remains an open verification area.
