# SOLID And OOP Heuristics

## Single Responsibility Principle

A class should have one primary reason to change. Common Unity violations:

- `PlayerController` handles input, movement, animation, combat, audio, UI, and
  saving.
- A MonoBehaviour both owns domain rules and talks directly to Firebase.
- UI widgets mutate gameplay state directly.

Refactor by separating:

- Input reading
- Domain decision/rules
- Unity presentation/lifecycle
- Persistence/backend
- UI view state

## Open/Closed Principle

Use when variants are expected:

- Damage modifiers
- Ability effects
- Item behaviors
- Reward calculators
- Platform-specific services

Avoid premature abstraction for one-off code. A switch is acceptable when the
set is truly closed and easier to reason about.

## Liskov Substitution Principle

Subtypes must honor the base contract. Watch for:

- Overrides that throw `NotSupportedException`.
- Subclasses that require callers to know their concrete type.
- Base interfaces with methods some implementations cannot support.

Prefer role interfaces over deep inheritance.

## Interface Segregation Principle

Interfaces should match caller needs:

```csharp
public interface IDamageable
{
    void ApplyDamage(DamageAmount amount);
}

public interface IHealable
{
    void Heal(HealthAmount amount);
}
```

Avoid fat interfaces such as `ICharacter` with movement, inventory, combat,
dialogue, save, and animation methods.

## Dependency Inversion Principle

High-level gameplay policy should depend on abstractions:

```csharp
public sealed class RewardService
{
    private readonly IInventoryWriter _inventory;
    private readonly IClock _clock;

    public RewardService(IInventoryWriter inventory, IClock clock)
    {
        _inventory = inventory;
        _clock = clock;
    }
}
```

Unity composition can still be explicit:

- Scene installer
- Bootstrap MonoBehaviour
- Existing ServiceLocator registration or Onity installer/composition root
- ScriptableObject service config

Do not hide dependencies behind static service locators unless the project has
an accepted architectural decision for that pattern.
