---
paths:
  - "Assets/Game/Core/**/*.cs"
  - "Assets/Game/Infrastructure/**/*.cs"
  - "Assets/Game/Editor/**/*.cs"
  - "Packages/**/*.cs"
---

# Engine Code Rules

- Engine-facing code must keep a clean boundary: adapt engine APIs to project
  abstractions without leaking engine-specific details into domain/gameplay policy.
- Public engine services should expose small, role-specific contracts that are
  mockable in tests.
- Keep hot-path optimization compatible with readability: isolate performance
  tricks behind well-named methods and document non-obvious constraints.
- Hot paths must avoid managed allocations; pre-allocate, pool, reuse, and verify
  with profiler evidence.
- Unity API calls are main-thread-only unless the pinned API documentation
  explicitly states otherwise.
- Profile before and after performance changes using the same scenario.
- Core and infrastructure adapters must not depend on feature UI or gameplay
  implementation assemblies.
- Stable cross-assembly public APIs require usage documentation. Breaking public
  contract changes require an approved migration plan.
- Dispose native collections, handles, subscriptions, and other owned resources
  deterministically.
- Before writing engine API code, consult
  `docs/engine-reference/unity/VERSION.md` and pinned package documentation.

## Examples

**Correct** (zero-alloc hot path):

```csharp
private readonly Collider[] m_nearbyCache = new Collider[64];

private void FixedUpdate()
{
    int count = Physics.OverlapSphereNonAlloc(
        transform.position,
        m_radius,
        m_nearbyCache,
        m_layerMask);

    UpdateNearbyTargets(m_nearbyCache, count);
}
```

**Incorrect** (allocating in hot path):

```csharp
private void FixedUpdate()
{
    Collider[] nearby = Physics.OverlapSphere(transform.position, m_radius);
    // VIOLATION: allocates a new array on every physics update.
}
```
