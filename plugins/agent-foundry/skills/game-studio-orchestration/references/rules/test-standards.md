---
paths:
  - "Assets/Tests/**/*.cs"
  - "Assets/Game/**/Tests/**/*.cs"
---

# Test Standards

- Test naming: `Method_Scenario_ExpectedResult` or the established assembly convention
- Every test must have a clear arrange/act/assert structure
- Unit tests must not depend on external state (filesystem, network, database)
- Integration tests must clean up after themselves
- Performance tests must specify acceptable thresholds and fail if exceeded
- Test data must be defined in the test or in dedicated fixtures, never shared mutable state
- Mock external dependencies — tests should be fast and deterministic
- Every bug fix must have a regression test that would have caught the original bug

## Examples

**Correct** (Unity Test Framework + Arrange/Act/Assert):

```csharp
[Test]
public void TakeDamage_PositiveDamage_ReducesHealth()
{
    // Arrange
    var health = new Health(100);

    // Act
    health.TakeDamage(25);

    // Assert
    Assert.That(health.Current, Is.EqualTo(75));
}
```

**Incorrect**:

```csharp
[Test]
public void Test1()
{
    var health = new Health(100);
    health.TakeDamage(25);
    Assert.That(health.Current, Is.LessThan(100));
    // VIOLATION: vague name and imprecise expected result.
}
```
