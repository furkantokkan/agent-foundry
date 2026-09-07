# Unity Patterns

## Architecture

- Game-specific rules should live in plain C# services where possible.
- MonoBehaviours should adapt Unity lifecycle/events to domain services.
- ScriptableObjects hold authored data, tuning values, item definitions,
  ability definitions, event channels, and editor-friendly config.
- Keep UI, gameplay, persistence, and networking/Firebase access separated.
- Follow the target bounded context's composition model. If it owns an
  established ServiceLocator, use its contracts and registration pattern.
  Otherwise prefer Onity for greenfield dependency injection, reactive state,
  and typed events. Do not start new Zenject/Extenject, VContainer, UniRx, R3,
  or MessagePipe usage. Existing usage remains inside its owning bounded context
  when migration is outside the current task.

## Unity 6 Defaults

- Render pipeline: URP for most cross-platform games; HDRP only for high-end
  visual targets; avoid Built-in for new projects.
- Input: Input System package and `.inputactions` assets.
- UI: UI Toolkit for screen-space UI; UGUI for world-space UI or unsupported
  animation cases.
- Assets: Addressables for runtime loading and content updates.
- Tests: Unity Test Framework with EditMode and PlayMode tests.
- Legacy fallback code: unless told otherwise, do not add duplicate old-system
  implementations for new features. If a legacy path exists, either work within
  it intentionally or plan a migration; do not keep both paths alive without a
  concrete compatibility requirement.

## C# Conventions

- Types, methods, properties: `PascalCase`
- Private fields: `m_camelCase`
- Private static fields: `s_camelCase`
- Locals and parameters: `camelCase`
- Constants: `k_camelCase`
- Inspector fields: `[SerializeField] private`
- Public APIs: XML doc comments when they are consumed outside the assembly

## Hot Path Rules

- No LINQ in hot paths unless profiling proves it is harmless.
- No string concatenation in per-frame loops.
- Use `Physics.*NonAlloc` variants for repeated physics queries.
- Pool projectiles, effects, floating UI, and frequently spawned entities.
- Use `UnityEngine.Pool.ObjectPool<T>` or an existing project pool.
- Profile before and after performance changes.

## Async

- If UniTask is present, prefer it for sequential async flows, coroutine
  replacement, PlayerLoop waits, and async composition. If it is not present,
  use Unity `Awaitable` or standard `async`/`await` based on the local Unity
  version and project convention.
- Use Onity messaging for cross-system typed pub/sub, event aggregation, and
  request/response when no established ServiceLocator/event pattern exists.
- Use Onity reactive types for reactive state streams, UI/domain observation,
  debounce/throttle, and frame/time-based streams when a real stream/state need
  exists.
- Tie cancellation to object lifetime (`destroyCancellationToken` on newer
  Unity versions, or project-standard cancellation source).
- Do not fire-and-forget without explicit exception handling.
- Avoid blocking the main thread on `Task.Result`, `.Wait()`, or sync waits.

## Addressables

- Track every handle and release it.
- Load by stable address or label, not file path.
- Group by loading context, not asset type.
- Preload gameplay-critical assets during loading screens.
- Use the Addressables Analyze tool for dependency and bundle problems.

## UI

- UI must not own gameplay state.
- UI sends commands/events; game systems update state; UI observes state.
- Support keyboard/mouse and gamepad when the target platform includes PC or
  console.
- Localize user-facing strings.
- Avoid querying the visual tree every frame; cache references.
- Use BEM-style kebab-case names/classes in UXML and USS, and centralize queried
  names as C# constants.
