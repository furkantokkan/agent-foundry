---
paths:
  - "Assets/Game/Data/**"
  - "Assets/AddressableAssetsData/**"
---

# Data File Rules

- JSON files must be valid and schema-checked when they are part of the runtime
  or build pipeline.
- JSON naming follows the owning system's documented convention; Unity-authored
  ScriptableObject assets use the project's `PascalCase` asset convention.
- Every data file must have a documented schema (either JSON Schema or documented in the corresponding design doc)
- Numeric values must include comments or companion docs explaining what the numbers mean
- Use consistent key naming: camelCase for keys within JSON files
- No orphaned data entries — every entry must be referenced by code or another data file
- Version data files when making breaking schema changes
- Include sensible defaults for all optional fields

## Examples

**Correct** naming and structure (`combat_enemies.json`):

```json
{
  "goblin": {
    "baseHealth": 50,
    "baseDamage": 8,
    "moveSpeed": 3.5,
    "lootTable": "loot_goblin_common"
  },
  "goblin_chief": {
    "baseHealth": 150,
    "baseDamage": 20,
    "moveSpeed": 2.8,
    "lootTable": "loot_goblin_rare"
  }
}
```

**Incorrect** (`EnemyData.json`, when the owning JSON convention requires snake case):

```json
{
  "Goblin": { "hp": 50 }
}
```

Violations: inconsistent filename/key convention and missing required schema fields.
