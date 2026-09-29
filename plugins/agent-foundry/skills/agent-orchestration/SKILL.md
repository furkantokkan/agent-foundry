---
name: agent-orchestration
description: Coordinate game, Unity, web, SaaS, and tooling work through one orchestration workflow across Claude and Codex. Resolve tracked task IDs, ownership conflicts, worktrees, sequential role handoffs, Editor queues, capacity, and verification. Use for orchestration or independent deliverables; keep one small task in the current agent.
---

# Agent Orchestration

Use this one orchestration entry for every domain. `game-studio-orchestration`
is a compatibility alias, not a separate coordinator. Keep one decision owner
and use delegates for concrete outputs that improve
quality or elapsed time. Loading this skill does not require spawning agents.
Use the current harness's actual tools and the user's existing authorization.

This is the canonical packaged procedure. Command entries are thin adapters. Read [provenance](references/provenance.md) only for source,
scope, or maintenance questions.

## Select the route

| Request | Route |
| --- | --- |
| One bounded change or short status | Current agent and the relevant domain skill |
| Independent investigations | Native read-only delegates; one synthesis owner |
| Several independent changes | Define ownership and dependencies, then isolate writers |
| Several tracked production task IDs | Stay here; load [tracked production](references/tracked-production.md) for conflict checks, worktrees, and lifecycle routing |
| Game/Unity coordination | Stay here; load [game and Unity references](references/game-and-unity.md) only as needed |
| Implement, verify, or repair one tracked task | Existing lifecycle skill; sequential role handoffs |
| Image generation or Blender work | Existing image/art/Blender skill and tools |

For tracked work, do not create a second contract, status file, defect ledger,
lock, scheduler, or closure path. `task-bug` resolves new bug evidence;
`task-cycle` owns defect records; `implement-task` owns a qualifying initial
empty-ledger execution. Closure remains owned by the installed lifecycle skill under current user/repository policy.
The tracked production profile belongs to this skill. Do not dispatch back to
the legacy alias or recursively start a second orchestrator.

Closure is owned by the existing lifecycle skill under the invoking caller's
current user/global/repository policy. Resolve that policy once and forward it
unchanged in every lifecycle assignment as
`Close authority: automatic_verified | explicit_user`. With
`automatic_verified` (a caller's explicit standing rule for verified automatic
closure), the delegated `implement-task` or `task-cycle` owner closes the task
in the same write once its test result and every other gate pass; nobody waits
for a `task-done` handshake. Without such a rule, forward `explicit_user`.
Role agents (implementer, verifier, bugfixer) never close; they return
evidence to that owner. The orchestrator itself never writes a closure, never
forwards authority the caller lacks, and never copies one provider's closure
preference into another. See the tracked profile's policy-resolution rule
before interpreting terminal verdicts.

## Plan before dispatch

1. Verify the exact repository, current instructions, base revision, dirty
   files, active owners, and required acceptance evidence. Refer to source
   files rather than remembered summaries. Do not restart or claim other work.
2. Identify the one decision owner, the smallest useful set of deliverables,
   and each dependency. The main agent normally keeps scope and integration
   decisions. Reviewers supply evidence; they do not become additional judges.
3. Declare every delegate's allowed and forbidden paths/actions, role, input
   revision, checks, output, and stop conditions using the compact
   [assignment contract](references/assignment-contract.md).
4. Check conflicts across paths, public interfaces, generated files, package
   locks, build outputs, runtime instances, and external resources. Different
   folders or worktrees alone do not prove independence.
5. Dispatch only independent, ready work within available capacity. Keep
   dependants queued until their inputs and ownership are valid. Resolve
   ambiguous scope or protected-target authorization before dependent writes;
   continue independent authorized work while a decision is pending.

For a small read-only delegation, the assignment may stay in the tool prompt.
For persistent work, attach it to the existing task handoff rather than
creating another task database. An ephemeral dispatch list describes running
agents; it is never task lifecycle authority.

## Ownership and integration

- Parallel writers require independent tasks, disjoint writable paths, and
  separate branches/worktrees. Reuse suitable worktrees; prefer the managed
  worktree tool when available. Use a branch name describing the change.
  Unity lanes instead use the seeded worktrees from `unity-cli` "Editor
  instances and worktrees", stay Editor-free, and leave the one Editor to the
  integration checkout (tracked production, item 6).
- Shared source files, exports, schemas, and generated outputs have one
  integration owner. Do not permit several append-only writers or resolve
  conflicts by blindly keeping both versions. Dependent changes run in order.
- A read-only investigation can share a checkout. Record the revision or file
  fingerprint it observed; findings over moving files are provisional.
- On one Unity task, implementer, verifier, and bugfixer hand off sequentially.
  The tracked production profile preserves the lifecycle lock and Editor queue
  protocol; scheduling never acquires a competing lifecycle lock. One serialized asset,
  including its `.meta`, has one writer. Load `unity-cli` and its project-readiness reference
  for actual Unity work; a workflow-document edit alone does not touch an Editor.
- After a predecessor releases ownership with a stable handoff, re-read current
  diffs, contracts, fingerprints, and approvals before waking its successor.
  For tracked tasks use `WAITING_FOR_OWNER` under the existing scheduler.
- Integrate completed changes sequentially within the authorized target.
  Worktree creation, delegation, or a passing review does not authorize commits,
  cherry-picks, pushes, publishing, protected Unity assets, or task closure.
  Preserve dirty work and inspect the integration diff before relevant checks.

## Models, quota, and capacity

Use the current global model-selection rules for actual complexity, and honor
an explicit user model choice. Do not pin every delegate to one model or raise
every reviewer to maximum effort. Keep the same decision owner across reviews.
When no host or repository routing policy is defined, use the
[bundled model guidance](references/model-routing.md): Sonnet 5.5 through
`sonnet` for Claude Code, and `gpt-6.1-sol` for bounded Codex work.
Do not spawn an agent solely to change models. Prevent nested fan-out by
default: a delegate returns a proposed split to its owner before spawning.

Capacity is bounded by ready independent work, harness slots, memory, shared
services/Editors, and known account limits. Start only as many workers as help;
reserve capacity for verification and recovery when needed. Missing quota data
does not mean zero usage, unlimited capacity, or a reason to block an otherwise
authorized small task. Reduce concurrency when uncertainty or limits matter.

Prefer the official usage tool exposed by the current harness when quota is
relevant. Preserve measurement time, account/source, window, and reset time.
Do not combine accounts, interpret missing values as zero, poll continuously,
scrape credentials, or assume another model has an independent quota pool.
When no supported source exists, report quota as unknown and use observed
limits/user information. Follow the established exhausted-model fallback;
never wait out a quota reset or buy/use an API fallback without user direction.
When no authorized available route remains, preserve a handoff and report it.

## Time budget and fast finish

Size the process to the work. There is no fixed session limit. The failure to
avoid is overhead that stretches a short job into a long one, for example an
hour of edits planned as eight hours of batches, reviews, and waiting.

- Estimate the work itself (the edits and the checks it needs) separately from
  the process around it (batch cycles, reviews, decisions, handoffs, waiting).
  Use measured durations, such as recent batch times, and show both before
  starting long work. When the process costs more than the work, restructure
  before continuing.
- Group small fixes by file cluster, so that one batch means one implement ->
  verify cycle. Verify each batch with the Roslyn compile check and a diff
  review, and run tests once at the end.
- Consult the decision owner when planning and at the end, not after every
  batch.
- Do not wait inside the session for another owner's paths. Do other work, or
  defer the dependent chain.

When the user asks to wrap up, or waiting and repeated cycles keep extending
the estimate, switch to the fast finish and show its estimate:

1. Start no new batch. Give the batch in flight a short time box of about 15
   minutes. If it still fails and it only improves quality (readability,
   naming, cleanup), revert that batch's own uncommitted changes. Otherwise
   keep its evidence and defer it.
2. Defer long, sequential, or blocked chains as follow-up task contracts
   (`create-task`) that keep their specs, so another session can run them.
   Tell any peer session that was waiting on that chain.
3. Verify once. Run the Roslyn check over every changed file. Refresh the
   Editor when files were added, so it imports them and writes their `.meta`
   files. Then run one shared test batch for the tests of the changed code,
   with EditMode and PlayMode as two requests.
4. Separate our failures from other owners' declared failures: the batch
   reports those as `FOREIGN_FAIL`. When a peer says its change breaks tests by
   design, ask it to `declare` them instead of keeping the list in chat.
5. Close or hand off with one short report: what is done, what was deferred
   (with follow-up IDs), the verification, and how to resume.

The fast finish never relaxes a gate. Deferred work leaves the finished scope
only as a follow-up task, and nothing unverified is reported as done.

## Supervision and completion

Read [harness operations](references/harness-operations.md) when dispatching.
Record the exact agent/session ID. Use completion events or bounded waits and
continue useful independent work. Reuse the assigned agent for follow-ups.
Log silence alone is not proof of death: inspect its status and pending tool
before interrupting or restarting. Never create a replacement writer while
its predecessor may still run. A retry needs a changed condition, retained
partial-work inspection, and a bounded attempt; stop on repeated no-progress.

Treat delegate completion as a claim. Verify the changed-file inventory and
diff against ownership; reproduce important findings against current sources.
Check the required success/failure paths on the actual resulting revision.
Distinguish an implementation claim, fresh verification, and authorized closure.
Explicit user acceptance remains valid evidence under the existing rules.

Return a compact result: changed outputs, evidence with revision/freshness,
unresolved items, and next owner/action. Do not repeat already valid tests
without new changes or unresolved concerns. Record durable learning through
the existing memory/task workflow; do not create automatic paid monitors.
