# Unity MCP identity review

This is a manual review of the documented protocol for PR #2's wrong-project
selection finding. It does not claim a live Unity or MCP execution test.

## Review criteria

The requested project root and complete version are read from the repository.
Discovery/registration evidence must bind both values to one full instance
ID/session before selection. Selection is followed by pinned project-info
readback before Editor-state queries, tests, or mutations.

| Scenario | Required result |
| --- | --- |
| Only connected Editor belongs to a different project | No selection or Editor work. |
| Two projects share a basename, or one path prefixes another | Canonical absolute roots must match exactly; names/prefixes do not qualify. |
| Same project path but different patch version or suffix | No selection; full version must match ProjectVersion.txt. |
| HTTP discovery has name/hash/version but no path | Require independent same-instance/session path proof; otherwise stop before selection. |
| Candidate path/version is missing, stale, or cannot be canonicalized | No selection; obtain fresh read-only evidence. |
| More than one matching candidate/session remains | Report ambiguity; do not choose the first candidate. |
| One proven candidate is available | Select its full discovered ID explicitly, even if it is the only Editor. |
| Selection response or project/info readback differs | Stop before Editor-state reads or further operations. |
| Editor restarts, reconnects, reloads, or routing/instances change | Invalidate proof and repeat discovery, matching, pinning, and readback. |
| Pre-Unity-6 CLI reports no instances, but MCP proof succeeds | Accept gated MCP evidence; do not take file-only fallback or block only because CLI status failed. |
| Unity 6+ CLI reports no instances | Diagnose CLI/Pipeline; no automatic legacy MCP permission. |
| Repository version is unavailable or below MCP's supported range | Do not infer the gate or support from a CLI error. |
| Source-only acceptance needs no live Editor | Report live evidence unavailable and use the pinned file lane without claiming Editor verification. |
| Required acceptance needs live state but identity is unproven | Return BLOCKED; raw YAML/file edits cannot bypass that boundary. |

## Evidence and scope

- [Copilot finding](https://github.com/furkantokkan/agent-foundry/pull/2#discussion_r4092262047).
- [Canonical identity gate](../../plugins/agent-foundry/skills/unity-cli/SKILL.md#exact-mcp-identity-gate).
- [Preflight](../../plugins/agent-foundry/skills/unity-cli/SKILL.md) applies
  the gate before Editor inspection or file-only fallback.
- MCP for Unity v10.2.0
  [HTTP instance discovery](https://github.com/CoplayDev/unity-mcp/blob/v10.2.0/Server/src/services/resources/unity_instances.py)
  omits the absolute path; its
  [project-info resource](https://github.com/CoplayDev/unity-mcp/blob/v10.2.0/Server/src/services/resources/project_info.py)
  is active-instance scoped and therefore cannot prove a candidate before selection.
- Installed Unity CLI 1.0.0-beta.11 help describes `status --project-path`
  as a case-insensitive substring filter, requiring a separate exact comparison.

Package verification uses `python scripts/validate.py --refresh`, then
`python scripts/validate.py`, local Markdown target/anchor checks, and
`git diff --check`. These validate the distributed instructions and manifests,
not live Editor routing or the behavior of a future agent.
