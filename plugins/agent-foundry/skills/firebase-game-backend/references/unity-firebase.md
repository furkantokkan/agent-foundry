# Unity Firebase Integration

## Setup Checks

Verify:

- Firebase Unity SDK packages are installed intentionally.
- Platform config files are present where needed:
  - Android: `google-services.json`
  - iOS: `GoogleService-Info.plist`
- Android/iOS resolver generated dependencies are not hand-edited.
- Initialization checks dependencies before using products.

## Architecture

Hide Firebase behind interfaces:

```csharp
public interface ICloudSaveService
{
    Task<PlayerSave> LoadAsync(string slotId, CancellationToken ct);
    Task SaveAsync(string slotId, PlayerSave save, CancellationToken ct);
}
```

Gameplay code calls the interface. Infrastructure implements it with Firebase.

For Cloud Functions request/response APIs, use a dedicated Unity API client
layer:

- Centralize endpoint constants.
- Define serializable request/response DTOs.
- Send requests through one transport wrapper that owns auth headers, App Check,
  client version, retry, timeout, and parsing.
- Return typed result envelopes to gameplay code.
- Do not scatter raw HTTP URLs, headers, JSON serialization, or retry behavior
  across gameplay systems.

## Unity Lifecycle

- Initialize Firebase during boot/loading, not lazily in gameplay.
- Surface initialization failure clearly.
- Do not block the main thread while waiting for Firebase tasks.
- Marshal results back to the Unity main thread before touching Unity objects.
- Tie async operations to scene/object lifetime cancellation.

## Offline and Error Handling

- Decide whether the game supports offline play.
- Distinguish auth failure, permission denied, network failure, conflict, and
  server validation failure.
- Use retry/backoff for transient failures.
- Never silently discard failed cloud save writes.
