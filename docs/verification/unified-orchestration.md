# Unified orchestration and readiness migration

- `agent-orchestration` is the sole scheduler; the legacy studio entry forwards raw arguments in the same invocation.
- Role, hook, rule, and template resources remain under the legacy studio folder as domain references.
- `unity-cli` owns project readiness, including exact identity, instructions, dirty work, ownership, Editor state, and verification readiness; standalone `unity-preflight` is removed.
- Existing lifecycle skills retain locks, defects, verification, and current caller-authorized closure policy.
- Other Avenox skills, runtimes, machine paths, and private task state are outside this publication.

## Forward scenarios for independent review

| Input | Required route |
| --- | --- |
| One web button text fix | Current agent and relevant domain procedure; no forced fan-out. |
| Independent tracked tasks, one Unity 2022 Editor | Separate writer worktrees; sequential roles per task; one exact-identity MCP Editor queue. |
| Two tasks own the same asset | Known owner runs; successor waits and revalidates after stable handoff/release. |
| Legacy studio command with quoted repo/flags | Arguments preserved; unified tracked profile, no recursive scheduler. |
| Initial empty-ledger task passes | Existing lifecycle owner applies current authorized closure policy; no scheduler-written closure. |
| Existing defects fail verification | task-cycle retains original defect IDs and required fresh evidence. |
| Quota source missing | Unknown capacity; bounded useful work, no credential scanner or paid fallback. |
| Quiet CLI session with pending tool | Inspect exact status; no latest-session resume or duplicate writer. |
| Missing serialized-target approval | Read-only readiness allowed; protected write waits for target authorization. |
| Project uses another issue system | Preserve it; no production contract migration forced by orchestration. |
| Unified source missing through legacy alias | Report exact missing path and stop; no cached-scheduler fallback. |

Static package/link checks and decision simulations verify instruction consistency. They do not prove live Unity behavior or external agent execution.

## Verified on 2026-09-27

- Package refresh and standalone validation pass: 93 core skills, 94 commands,
  seven command aliases, three roles, and 451 export hashes across all plugins.
- Independent review confirmed the scenarios above and complete readiness
  migration. Its stale Codex metadata route and attribution-path findings were
  repaired and rechecked.
- The validator rejects a simulated retired route in Codex YAML without writing
  to the package. Active command and skill Markdown/YAML contain no old route.
- Relative references resolve, excluding two unchanged illustrative D-001
  links in task-cycle. Git whitespace checks pass.
