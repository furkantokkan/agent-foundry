# Cysharp Packages

Use this reference before using or recommending Cysharp packages in Unity/C#.
Do not add packages automatically. Prefer packages already installed in the
project; ask before adding or changing dependencies.

## Snapshot

Latest NuGet versions checked on 2026-05-20:

- `UniTask` 2.5.11
- `R3` 1.3.1
- `MessagePipe` 1.8.1
- `ZLinq` 1.5.6
- `ZString` 2.6.0
- `MemoryPack` 1.21.4
- `MagicOnion` 7.10.0

## Selection Rules

- Use built-in Unity/.NET APIs for simple code.
- Use an installed Cysharp package when it is already the local convention.
- In the target bounded context, keep its established ServiceLocator contracts.
  Otherwise use Onity for greenfield Unity DI/reactive/events work. Do not
  extend R3 or MessagePipe beyond a context that already owns that stack when
  migration is outside scope.
- Propose adding a package only for concrete complexity, allocation, async,
  serialization, or networking problems.
- Ask before adding packages, changing versions, or adding NuGetForUnity/UPM git
  dependencies.
- Pin versions in production projects and update dependency docs/ADRs.

## Import Checklist

- Check `Packages/manifest.json` and `Packages/packages-lock.json` for
  `com.cysharp.*` Unity packages.
- Check NuGetForUnity package files and `.csproj` references for NuGet packages.
- Check existing `using` directives and `.asmdef` references before adding new
  imports.
- Use UPM git URLs for Unity packages and NuGetForUnity for NuGet parts. Do not
  copy DLLs manually unless the official package docs require it.
- In `.asmdef` projects, add explicit references to imported package assemblies.
- Pin versions in production and run Unity compile/tests after import.

## Best-case Selection

- **Direct injected call**: one object intentionally commands another.
- **C# event**: small local notification with obvious lifetime.
- **UniTask**: sequential async/coroutine replacement, delays, frame waits,
  scene/asset/web loads, UI click waits, or parallel async composition.
- **Onity Messaging**: preferred typed cross-system pub/sub and request/response
  for new work when no established ServiceLocator/event pattern exists.
- **Onity Reactive**: preferred ongoing state streams, UI binding,
  debounce/throttle, combine-latest, and frame/time-based streams for new work.
- **MessagePipe/R3**: use only inside the target bounded context that already
  owns it, or for explicitly requested migration/compatibility work.

## Package Roles

- **UniTask**: allocation-conscious Unity async/await and PlayerLoop-tied async
  flows. Prefer over new coroutines when installed and cancellation/readability
  improves.
- **MessagePipe**: established-stack pub/sub, event aggregator, and mediator.
  Use only inside its owning bounded context or for explicit migration work.
- **R3**: established-stack reactive streams and UniRx successor. Use only
  inside its owning bounded context or for explicit migration work.
- **ZLinq**: zero-allocation LINQ-style queries. Use for allocation-sensitive
  query code; prefer plain loops when clearer.
- **ZString**: zero-allocation string building. Use for hot-path UI/log/text
  building, especially TextMeshPro paths.
- **MemoryPack**: high-performance binary serialization. Use for save data,
  network payloads, caches, or shared DTOs when binary format is acceptable.
- **MagicOnion**: code-first RPC/realtime API framework over gRPC. Use for Unity
  client plus .NET backend scenarios; avoid when Firebase/REST is simpler.

## Unity Install Notes

- UniTask UPM:
  `https://github.com/Cysharp/UniTask.git?path=src/UniTask/Assets/Plugins/UniTask`
  Code namespace: `Cysharp.Threading.Tasks`.
- R3 Unity:
  install NuGet `R3`, then
  `https://github.com/Cysharp/R3.git?path=src/R3.Unity/Assets/R3.Unity`
  Code namespace: `R3`.
- MessagePipe Unity:
  install core plus the adapter matching the DI container. Unity requires
  UniTask and explicit message/handler registration for IL2CPP:
  `https://github.com/Cysharp/MessagePipe.git?path=src/MessagePipe.Unity/Assets/Plugins/MessagePipe`
  `https://github.com/Cysharp/MessagePipe.git?path=src/MessagePipe.Unity/Assets/Plugins/MessagePipe.VContainer`
  `https://github.com/Cysharp/MessagePipe.git?path=src/MessagePipe.Unity/Assets/Plugins/MessagePipe.Zenject`
  Code namespace: `MessagePipe`.
- ZLinq Unity:
  install NuGet `ZLinq`, then
  `https://github.com/Cysharp/ZLinq.git?path=src/ZLinq.Unity/Assets/ZLinq.Unity`
  Code namespace: `ZLinq`; call `AsValueEnumerable()`.
- ZString Unity:
  `https://github.com/Cysharp/ZString.git?path=src/ZString.Unity/Assets/Scripts/ZString`
  Code namespace: `Cysharp.Text`.
- MemoryPack Unity:
  install NuGet `MemoryPack`, then
  `https://github.com/Cysharp/MemoryPack.git?path=src/MemoryPack.Unity/Assets/MemoryPack.Unity`
  Code namespace: `MemoryPack`; use `[MemoryPackable] partial` DTOs.
- MagicOnion Unity client:
  install NuGetForUnity, YetAnotherHttpHandler, gRPC libraries,
  `MagicOnion.Client`, then
  `https://github.com/Cysharp/MagicOnion.git?path=src/MagicOnion.Client.Unity/Assets/Scripts/MagicOnion.Client.Unity#{Version}`
  Code namespaces: `MagicOnion`, `MagicOnion.Client`, `Grpc.Net.Client`, and
  `YetAnotherHttpHandler` where channels are created.

## Sources

- https://github.com/Cysharp/UniTask
- https://github.com/Cysharp/R3
- https://github.com/Cysharp/MessagePipe
- https://github.com/Cysharp/ZLinq
- https://github.com/Cysharp/ZString
- https://github.com/Cysharp/MemoryPack
- https://github.com/Cysharp/MagicOnion
- https://cysharp.github.io/MagicOnion/installation/unity
- https://www.nuget.org/profiles/Cysharp
