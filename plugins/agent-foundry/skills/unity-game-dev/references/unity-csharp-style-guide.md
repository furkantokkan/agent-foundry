# Unity C# Style Guide

Use the repository's canonical Unity style guide. If no approved ADR or style
guide explicitly selects another convention, use these defaults.

## Defaults

- Target Unity 6.3 LTS when this template's Unity reference is in use.
- Use the new Input System, UI Toolkit for new runtime UI, and URP by default.
- Unless told otherwise, do not add legacy fallback implementations for old
  Unity systems in new code. Prefer one current-stack implementation. Keep
  legacy support only when the repository already depends on it, production
  compatibility requires it, or the user explicitly asks for migration support.
- Prefer the target bounded context's established ServiceLocator. If none
  exists there, prefer Onity for greenfield dependency injection, typed events,
  and reactive state. Use UniTask for sequential async/coroutine replacement
  when installed. Do not introduce new Zenject/Extenject, VContainer, UniRx,
  R3, or MessagePipe usage; existing usage stays inside its owning context when
  migration is outside the task.
- For frequent spawn/despawn, use `UnityEngine.Pool.ObjectPool<T>` or the
  existing project pool.

## Dependency Resolution

1. If the target bounded context has an established ServiceLocator, use its
   existing interfaces and registration pattern. Do not introduce another
   locator.
2. Otherwise prefer Onity for new Unity DI, reactive state, and typed events.
3. If Onity is installed, use its installers, bindings, event hub/message broker,
   reactive types, and disposal pattern.
4. If Onity is not installed, propose adding
   `https://github.com/furkantokkan/Onity.git#upm` and ask before changing
   package files unless the user explicitly asked to install dependencies.
5. Do not start new Zenject/Extenject, VContainer, UniRx, R3, or MessagePipe
   usage. Existing usage stays inside its owning bounded context when migration
   is outside the current task.

Never resolve dependencies from deep domain code. Resolve at composition roots,
installers, lifetime scopes, factories, or MonoBehaviour adapters.

## Formatting and Organization

- Use Allman braces and keep lines under roughly 120-140 characters.
- Use explicit access modifiers.
- Organize classes: usings, namespace, fields, properties, events, Unity
  lifecycle methods, public methods, private methods, nested types.
- Lifecycle order: `Awake`, `OnEnable`, `Start`, `OnDisable`, `OnDestroy`,
  `FixedUpdate`, `Update`, `LateUpdate`.
- Use `#region` sparingly, mainly for Animation Event Methods or Input Event
  Methods that Unity calls externally.

## Naming

- Types, methods, properties, namespaces, enum values, files, and folders:
  `PascalCase`.
- Code symbols use clear English. Do not introduce Turkish, mixed-language,
  vague, or over-formal names.
- Private instance fields: `m_camelCase`.
- Private static fields: `s_camelCase`.
- Constants: `k_camelCase`.
- Locals and parameters: `camelCase`.
- Boolean fields/properties/methods use `is`, `has`, or `can`.
- Methods use verbs: `ApplyDamage`, `SetMovementInput`, `ChangeHealth`,
  `CalculateDamage`, `CreatePlayer`.
- Prefer simple, direct verbs such as `Set`, `Get`, `Add`, `Remove`, `Create`,
  `Update`, `Load`, `Save`, `Open`, `Close`, `Start`, `Stop`, `Enable`,
  `Disable`, `Show`, `Hide`, `Apply`, `Calculate`, and `Validate`.
- Avoid inflated verbs such as `Ensure`, `Perform`, `Execute`, `Process`, or
  `Manage` when a simpler verb states the action. Use `Ensure` only for an
  idempotent guarantee such as get-or-create, repair-if-missing, or invariant
  validation.
- Async methods end with `Async`; coroutine methods end with `Co` when
  coroutines are used.

## Unity Rules

- Keep MonoBehaviours thin and focused on lifecycle, serialization, scene wiring,
  and Unity API adaptation.
- Put gameplay/domain rules in plain C# classes that can be tested without
  scenes, Firebase, UI, or platform APIs.
- Use `[SerializeField] private` for Inspector fields and expose state through
  properties when needed.
- Use `[RequireComponent]` for mandatory component dependencies.
- Cache component and visual tree references outside hot paths.
- Avoid allocations and scene-wide queries in `Update`, physics callbacks,
  rendering callbacks, and UI loops.
- Read input in `Update`; apply physics in `FixedUpdate` if needed.

## Async, Events, and Reactive Flow

- Prefer UniTask over new coroutines when UniTask is installed and the workflow
  is sequential async work: delays, frame waits, scene/asset/web loads, UI click
  waits, or parallel async composition.
- Pass `CancellationToken` as the last argument in UniTask methods and tie
  MonoBehaviour work to `destroyCancellationToken` or
  `GetCancellationTokenOnDestroy`.
- Keep coroutines when existing APIs or legacy behavior require exact coroutine
  timing; do not convert every `IEnumerator` mechanically.
- Prefer direct dependency calls when one object intentionally commands another.
- Use C# events for small local notifications with clear lifetime.
- Use Onity messaging for typed cross-system pub/sub and request/response when
  no established ServiceLocator/event pattern exists.
- Use Onity reactive types for ongoing state, UI binding, debounce/throttle,
  combination, and frame/time-based reactive flows.
- Dispose Onity subscriptions through `IDisposable`, `AddTo(Component)`, or the
  project's lifetime pattern.

## Data, Events, and UI Toolkit

- Use ScriptableObjects for authored static configuration, not mutable runtime
  player/session state. Use `DataSO` suffix for data assets.
- Use enums for mutually exclusive states. Avoid strings/ints for state.
- Centralize animation parameter, tag, layer, sorting layer, and input action
  names as constants.
- Subscribe in `OnEnable` and unsubscribe in `OnDisable`.
- Use UnityEvent only when callbacks must be assigned in the Inspector.
- Use BEM-style kebab-case for UXML/USS names and classes, for example
  `shop-panel__buy-button--disabled`.
- Keep USS selectors flat and toggle classes from C# for state.

## Comments and Exceptions

- Comments explain intent, constraints, or non-obvious tradeoffs. Do not comment
  obvious code line by line.
- Use `[Tooltip]`, `[Header]`, and `[Space]` for Inspector context.
- Use try/catch for external failures such as file I/O, network, Firebase, and
  platform APIs. Do not use exceptions for ordinary internal control flow.
