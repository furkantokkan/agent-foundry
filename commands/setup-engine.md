---
description: Configure the project's game engine and version. Pins the engine in CLAUDE.md, detects knowledge gaps, and populates engine reference docs via WebSearch when the version is beyond the LLM's training data.
argument-hint: [task]
---

# /setup-engine

Use the `setup-engine` Codex skill for this request. If this workflow references
Claude-only agents, treat those names as role guidance and follow Codex's active
skills, global instructions, and local repository rules.

User arguments: $ARGUMENTS