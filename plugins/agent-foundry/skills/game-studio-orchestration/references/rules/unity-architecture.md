# Canonical Unity Architecture Policy

## Authority

This file is the authoritative source for Unity naming, dependency injection,
messaging, and reactive-state decisions in this repository. If an agent, skill,
template, user-level fallback, or reference document conflicts with this file,
follow this file and report the conflict. Changes require an approved ADR.

## Naming

- Private instance fields MUST use `m_camelCase`.
- Private static fields MUST use `s_camelCase`.
- Constants MUST use `k_camelCase`.
- Public types and members MUST use `PascalCase`.
- Parameters and local variables MUST use `camelCase`.
- Do not rename unrelated code only to normalize naming.

## Domain Boundaries

- Plain C# domain code MUST receive dependencies through constructors or method
  parameters.
- Domain code MUST NOT resolve from Onity, a ServiceLocator, or another
  container.
- Resolve dependencies only in installers, bootstrappers, factories, or other
  composition roots.
- Keep MonoBehaviours focused on lifecycle, serialization, scene wiring, and
  Unity API adaptation.

## Composition Policy

1. Preserve the established composition model inside an existing bounded
   context. Do not introduce a second locator or container into that context.
2. Existing ServiceLocator/container integrations MAY remain and MAY be extended
   only inside their current bounded context when required by an approved story.
3. New greenfield systems MUST use Onity unless an accepted ADR selects another
   project stack.
4. Do not introduce new Zenject, Extenject, VContainer, UniRx, R3, or
   MessagePipe usage.
5. Do not add, remove, or upgrade architecture packages without explicit
   approval.

## Onity Boundaries

- Bind dependencies in Onity installers or the approved project composition
  root.
- Use Onity messaging for new typed cross-system pub/sub or request/response.
- Use Onity reactive types only for genuine ongoing state streams.
- Dispose subscriptions through the project lifetime policy.
- Prefer direct calls or local C# events when they express ownership more
  clearly than messaging or reactive streams.

## Existing Frameworks

Existing Zenject, Extenject, VContainer, UniRx, R3, MessagePipe, or
ServiceLocator code MAY remain in established systems. Do not expand those
frameworks into new systems and do not migrate them incidentally. Migration
requires a dedicated story, characterization tests, a bounded scope, and an
accepted ADR.

## Decision Gate

Stop and request an architecture decision when a change would add a package,
mix containers in one feature, cross a bounded-context dependency boundary,
change a public contract, or contradict an accepted ADR.
