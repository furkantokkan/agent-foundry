---
description: Legacy-only epic-to-story workflow; task-first repositories use create-task directly and do not create duplicate story files.
argument-hint: [task]
---

# /create-stories

Use the `create-stories` Codex skill for this request. If this workflow references
Claude-only agents, treat those names as role guidance and follow Codex's active
skills, global instructions, and local repository rules.

User arguments: $ARGUMENTS

If repository authority selects the canonical task-first workflow, stop without
writing story files and route each independently closable outcome to
`create-task`. Continue only for an explicitly legacy story repository.
