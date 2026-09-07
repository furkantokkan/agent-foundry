---
description: Validate that a story file is implementation-ready. Checks for embedded GDD requirements, ADR references, engine notes, clear acceptance criteria, and no open design questions. Produces READY / NEEDS WORK / BLOCKED verdict with specific gaps. Use when user says 'is this story ready', 'can I start on this story', 'is story X ready to implement'.
argument-hint: [task]
---

# /story-readiness

Use the `story-readiness` Codex skill for this request. If this workflow references
Claude-only agents, treat those names as role guidance and follow Codex's active
skills, global instructions, and local repository rules.

User arguments: $ARGUMENTS