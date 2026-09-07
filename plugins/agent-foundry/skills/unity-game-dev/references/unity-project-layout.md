# Unity Project Layout

Prefer the existing layout when working in an established project. For new
Unity projects, use this baseline unless the user asks for another convention.

```text
Assets/
  Scripts/
    Core/
    Gameplay/
    UI/
    Infrastructure/
    Firebase/
    Editor/
  Tests/
    EditMode/
    PlayMode/
  Data/
    ScriptableObjects/
  Art/
  Audio/
  UI/
  Addressables/
Packages/
  manifest.json
ProjectSettings/
```

## Assembly Definitions

Use `.asmdef` files to keep compile boundaries explicit:

- `Game.Core`
- `Game.Gameplay`
- `Game.UI`
- `Game.Infrastructure`
- `Game.Firebase`
- `Game.Editor`
- `Game.Tests.EditMode`
- `Game.Tests.PlayMode`

Tests should reference the assemblies they test, not the other way around.

## Tests

Use Unity Test Framework:

- EditMode: pure C# logic, formulas, validators, serializers, state machines.
- PlayMode: scene integration, physics, MonoBehaviour lifecycle, UI interaction.
- For API clients, use EditMode tests for endpoint constants, request DTO
  serialization, response DTO parsing, result/error-code mapping, and retry or
  idempotency behavior that can be tested without scenes.

Place tests in:

```text
Assets/Tests/EditMode/
Assets/Tests/PlayMode/
```

For CI, prefer `game-ci/unity-test-runner` or the project's existing Unity
batchmode pipeline.

## Firebase in Unity

Keep Firebase code behind interfaces:

- `IAuthService`
- `ICloudSaveService`
- `ILeaderboardService`
- `IRemoteConfigService`
- `IAnalyticsService`

Gameplay systems should not import Firebase namespaces directly.
