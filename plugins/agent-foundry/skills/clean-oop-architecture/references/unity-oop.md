# Unity OOP Architecture

## Unity Boundary Pattern

Separate Unity lifecycle from domain rules:

```csharp
public sealed class PlayerMovementBehaviour : MonoBehaviour
{
    [SerializeField] private CharacterController m_controller;
    [SerializeField] private MovementConfig m_config;

    private PlayerMovementService m_movement;

    private void Awake()
    {
        m_movement = new PlayerMovementService(m_config);
    }

    private void Update()
    {
        var input = ReadInput();
        var delta = m_movement.CalculateDelta(input, Time.deltaTime);
        m_controller.Move(delta);
    }
}
```

`PlayerMovementService` is testable plain C#; the MonoBehaviour only adapts
Unity APIs.

## ScriptableObject Data

Use ScriptableObjects for authored/tunable data:

- MovementConfig
- WeaponDefinition
- AbilityDefinition
- EnemyArchetype
- EconomyTuning

Do not put mutable runtime player state in shared ScriptableObject assets unless
the project has an intentional runtime clone pattern.

## Dependency Injection

Follow the existing project composition model first:

- If the target bounded context owns an established `ServiceLocator`, use its
  interfaces and registration pattern. Do not create another locator or add new
  global access points.
- Otherwise prefer Onity for new Unity dependency injection, reactive state, and
  typed events.
- If Onity is not installed, propose adding
  `https://github.com/furkantokkan/Onity.git#upm` and ask before changing
  package files unless the user explicitly asked to install dependencies.
- Do not start new Zenject/Extenject, VContainer, UniRx, R3, or MessagePipe
  usage. Existing usage stays inside its owning bounded context when migration
  is outside the current task.

Without Onity or locator:

- Use explicit bootstrap components.
- Pass dependencies into constructors for plain C# services.
- Use serialized references for scene objects.

With Onity:

- Bind interfaces to implementations in `MonoInstaller` or the existing project
  composition root.
- Use `OnityEventHub` or `IMessageBroker` for typed cross-system events.
- Use `Subject<T>` or `ReactiveProperty<T>` only for real state streams.
- Dispose subscriptions with `IDisposable`, `AddTo(Component)`, or the project
  lifetime pattern.
- Avoid resolving from Onity deep inside domain code.

## Events

Use events to decouple systems, but keep ownership clear:

- Gameplay service emits domain event.
- UI listens and updates display.
- Audio/VFX listen and play feedback.

Avoid event chains where nobody owns the final state.

## Anti-Patterns

- `GameManager.Instance` as a god object.
- UI button directly mutates inventory/currency.
- Firebase SDK calls inside combat, inventory, or movement systems.
- `Update` methods polling everything because ownership is unclear.
- MonoBehaviour inheritance trees for gameplay variants.
