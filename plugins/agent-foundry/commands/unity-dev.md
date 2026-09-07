---
description: Work on a Unity task using the repository's canonical architecture, ownership, automation, and verification policies.
argument-hint: [unity-task]
---

# Unity Game Dev

Use the `unity-game-dev` Codex skill for this request. Add
`clean-oop-architecture` only when the task involves architecture, DI, naming,
testability, or refactoring.

Treat the complete block below as one raw input and preserve quoted paths,
logs, references, and constraints:

<task-input>
$ARGUMENTS
</task-input>

Read repository instructions and run a read-only Unity preflight before any
Editor mutation. Preserve the established composition model inside each bounded
context. Existing ServiceLocator/container usage may remain there; otherwise
use the repository's accepted Onity policy for genuinely new greenfield work.
Do not introduce new Zenject/Extenject, VContainer, UniRx, R3, or MessagePipe
usage, and do not add Onity or another package without explicit authorization.

Keep MonoBehaviours thin, plain C# logic testable, and naming consistent with
the canonical `m_`/`s_`/`k_` policy when no narrower convention exists. Declare
allowed paths, forbidden paths, and one writer for every serialized asset.
Verify changed behavior with focused tests and Unity compilation evidence.
