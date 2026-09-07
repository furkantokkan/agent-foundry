---
description: Profile, diagnose, and optimize a Unity performance issue with measured evidence.
argument-hint: [performance-task]
---

# Unity Optimization

Use the `unity-optimization` Codex skill and `unity-game-dev` for project
context. Add `clean-oop-architecture` only when the measured fix requires an
architecture or refactoring decision.

Treat this as one raw request:

<task-input>
$ARGUMENTS
</task-input>

Run a read-only Unity preflight. Reproduce and measure before editing when
practical; classify CPU, GC, GPU/rendering, UI, physics, loading, memory, or
thermal/battery cost. Change only the measured hot path and report comparable
before/after evidence, changed files, and residual risk.
