---
paths:
  - "Assets/Game/Gameplay/**/*.cs"
  - "Assets/Game/Features/**/*.cs"
---

# Gameplay Code Rules

- Gameplay logic must follow Clean Code and SOLID by default: focused classes,
  clear responsibilities, explicit dependencies, and testable domain rules.
- Keep engine, UI, Firebase, save/load, and network details outside core gameplay
  rule code. Use adapters or injected services at those boundaries.
- Do not add broad manager classes that own unrelated systems. Split by domain
  responsibility before the class becomes a dumping ground.
- Authored and tunable gameplay values MUST come from approved configuration or
  data assets. Internal invariants and algorithmic constants may remain named
  constants in code.
- Use the appropriate Unity time source for frame-dependent behavior; keep
  deterministic domain calculations independent from global Unity time where
  practical.
- NO direct references to UI code. Use direct injected commands for intentional
  dependencies and follow `.claude/rules/unity-architecture.md` for cross-system
  messaging or reactive state.
- Add interfaces at real dependency boundaries; do not create one-to-one
  interfaces that hide no variation or testing seam.
- Non-trivial state machines must define valid states and transitions explicitly.
- Separate logic from presentation and test changed rules and important edge cases.
- New or changed expected behavior must include unit tests for the success path
  and important failure paths
- Link the governing story/design/ADR in the story handoff or architecture
  evidence, not repetitive comments on every class.
- No static singletons for game state — use dependency injection

## Examples

**Correct** (data-driven):

```csharp
[SerializeField] private CombatConfigDataSO m_config;

private float CalculateDamage(float multiplier)
{
    return m_config.BaseDamage * multiplier;
}
```

**Incorrect** (hardcoded):

```csharp
private float CalculateDamage(float multiplier)
{
    return 25.0f * multiplier; // VIOLATION: authored tuning value is hardcoded.
}
```
