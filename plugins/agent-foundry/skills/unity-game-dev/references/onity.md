# Onity For Unity

Use this reference when a Unity task needs dependency injection, reactive state,
or typed events and the target bounded context does not already have an
established ServiceLocator pattern.

## Default Choice

- If the target bounded context owns an established `ServiceLocator`, use its
  existing interfaces and registration pattern.
- Otherwise prefer Onity for new Unity DI, reactive state, and typed events.
- Do not start new Zenject/Extenject, VContainer, UniRx, R3, or MessagePipe
  usage. Existing usage stays inside its owning bounded context when migration
  is outside the current task.
- If Onity is not installed, propose adding it and ask before modifying
  `Packages/manifest.json` or package files unless the user explicitly asked to
  install dependencies.

## What Onity Replaces

Onity is intended as one Unity package for:

- DI: `Onity.DI`, replacing Zenject/VContainer for new work.
- Reactive state: `Onity.Reactive`, replacing UniRx/R3 for new work.
- Typed events: `Onity.Messaging`, replacing MessagePipe/UniRx MessageBroker for
  new work.

## Install Notes

Recommended UPM git URL:

```text
https://github.com/furkantokkan/Onity.git#upm
```

Manifest dependency:

```json
"com.onity.framework": "https://github.com/furkantokkan/Onity.git#upm"
```

Onity's Unity layer requires ZLinq. If the project does not already restore
ZLinq, install it through the project's existing NuGet/NuGetForUnity workflow.

## Usage Rules

- Prefer constructor injection for plain C# domain/services.
- Bind services in a `MonoInstaller` or existing project composition root.
- Use `OnityEventHub` or `IMessageBroker` for typed cross-system events.
- Use `Subject<T>` or `ReactiveProperty<T>` for actual state streams.
- Dispose every subscription with `IDisposable`, `AddTo(Component)`, or the
  project's lifetime/disposal pattern.
- Keep domain logic in engine-free assemblies where possible; Onity core APIs
  are designed to support scene-free EditMode tests.

## Sources

- https://github.com/furkantokkan/Onity
- https://furkantokkan.github.io/Onity
