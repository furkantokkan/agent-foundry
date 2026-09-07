---
description: Run a read-only Unity repository, Editor, automation, ownership, and verification readiness check.
argument-hint: '[repository-path] [proposed task or paths]'
---

# Unity Preflight

Use the `unity-preflight` Codex skill for this request.

<preflight-input>
$ARGUMENTS
</preflight-input>

Do not mutate files, Editor state, Play Mode, tests, permissions, scenes, or
assets. Return `READY`, `READY WITH WARNINGS`, or `BLOCKED` with exact evidence.
