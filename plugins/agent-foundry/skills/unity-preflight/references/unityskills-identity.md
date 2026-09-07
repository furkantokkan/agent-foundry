# UnitySkills Identity and Permission Notes

Use UnitySkills only when the first-choice Unity MCP connection is unavailable
or points elsewhere. `GET /health` proves REST service health and exposes
permission state; it is not sufficient proof of the open repository.

Use this sequence:

1. Read `GET /health` and record `currentMode`, `panelApprovalRequired`, and
   pending state.
2. Discover or dry-run the read-only `project_get_info` schema when necessary.
3. Execute `project_get_info` and read `result.projectPath` and Unity version.
4. Normalize separators, case, and a trailing `Assets` segment before comparing
   with the exact repository root.
5. If it differs, do not mutate through that service.

Mode is a server-side boundary configured by the user. Do not change it from
preflight or chat. In Approval, FullAuto calls may need a one-shot grant. Auto
executes ordinary writes but still requires agent self-assessment. If Bypass is
reported, do not mutate through UnitySkills; ask the user to switch the panel to
Approval. Bypass must never be treated as task authorization.

PlayMode test runs and test-template creation may be classified NeverInSemi.
Use a user-managed allowlist or Bypass only when the user intentionally chose
that operating profile; never add allowlist entries proactively. Creating tests
also triggers compilation/domain reload and must pass the repository's canonical
folder explicitly instead of accepting UnitySkills defaults.

After any later mutation, use one transport, wait for import/compile/domain
reload to settle, then inspect compilation and Console evidence. That work is
outside read-only preflight.
