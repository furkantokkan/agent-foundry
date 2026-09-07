# Code Smells And Refactoring Moves

## Long Method

Symptoms:

- Hard to name the method precisely.
- Mixed validation, calculation, persistence, UI, and logging.
- Deep nesting.

Moves:

- Extract method by intent.
- Replace temp with query.
- Introduce parameter object.
- Move side effects to boundary methods.

## Large Class

Symptoms:

- Many unrelated fields.
- Methods use different subsets of fields.
- Class name ends in `Manager` and owns multiple systems.

Moves:

- Extract class by responsibility.
- Move method to the data owner.
- Split Unity adapter from domain service.

## Feature Envy

Symptoms:

- A method reads another object's data more than its own.

Moves:

- Move method to envied class.
- Introduce domain service if behavior depends on multiple peers.

## Shotgun Surgery

Symptoms:

- One behavior change requires edits in many files.

Moves:

- Centralize policy.
- Introduce event/command.
- Replace duplicated conditionals with a strategy or table.

## Primitive Obsession

Symptoms:

- Repeated `int currency`, `string itemId`, `float health` rules everywhere.

Moves:

- Introduce value objects where constraints matter.
- Use typed IDs for cross-system boundaries.

## Inappropriate Singleton

Symptoms:

- Static access hides dependencies.
- Tests require global state reset.
- Scene order controls correctness.

Moves:

- Constructor injection for pure C#.
- Serialized references or scene bootstrap for Unity adapters.
- Existing ServiceLocator registration or Onity installer/composition root.
