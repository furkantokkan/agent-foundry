---
description: Run the critical path smoke test gate before QA hand-off. Executes the automated test suite, verifies core functionality, and produces a PASS/FAIL report. Run after a sprint's stories are implemented and before manual QA begins. A failed smoke check means the build is not ready for QA.
argument-hint: [task]
---

# /smoke-check

Use the `smoke-check` Codex skill for this request. If this workflow references
Claude-only agents, treat those names as role guidance and follow Codex's active
skills, global instructions, and local repository rules.

User arguments: $ARGUMENTS