# Unity Interaction Pattern Library: [Game Title]

> **Status**: Draft | Stable | Under Revision
> **Author/Owner**: [ux-designer / UI owner]
> **Last Updated**: [YYYY-MM-DD]
> **Unity Version**: [from ProjectSettings/ProjectVersion.txt]
> **UI Boundary**: [UI Toolkit | justified existing UGUI context]
> **Runtime Assembly**: [name/path]
> **Serialized Asset Owner**: [one active writer or none]
> **Related**: art bible, accessibility requirements, screen UX specs, UI ADR

This document is the canonical behavioral contract for reusable player-facing
interactions. Screen specs reference pattern IDs instead of redefining hover,
focus, navigation, cancellation, feedback, and accessibility behavior.

## 1. Governance

- New screen-space UI defaults to UI Toolkit when it fits the approved UI ADR.
  Existing UGUI contexts may remain when migration is outside scope or a
  feature requires capabilities justified by the ADR.
- UI code does not own game/domain state. It binds to typed presentation/service
  boundaries and issues explicit commands/events.
- Runtime code must not reference Editor/test assemblies.
- Scenes, prefabs, UXML/USS assets, PanelSettings, localization tables, Input
  Actions, and UI ScriptableObjects have exactly one active writer.
- A Stable pattern change requires a usage audit, UX approval, regression plan,
  and explicit serialized ownership before implementation.

## 2. Pattern Catalog

| ID | Pattern | Purpose | Used In | Status | Owner |
|---|---|---|---|---|---|
| BTN-PRIMARY | Primary Button | One main screen action | [screens] | Draft | [owner] |
| BTN-SECONDARY | Secondary Button | Alternative/cancel action | [screens] | Draft | [owner] |
| BTN-DESTRUCTIVE | Destructive Button | Irreversible action with confirmation | [screens] | Draft | [owner] |
| TOGGLE | Toggle | Binary preference/state selection | [screens] | Draft | [owner] |
| SLIDER | Slider | Bounded continuous value | [screens] | Draft | [owner] |
| SELECT | Dropdown/Select | Discrete choice | [screens] | Draft | [owner] |
| LIST-ITEM | List Item | Selectable virtualized row | [screens] | Draft | [owner] |
| GRID-ITEM | Grid Item | Two-dimensional selectable cell | [screens] | Draft | [owner] |
| MODAL | Modal Dialog | Blocking decision with focus trap | [screens] | Draft | [owner] |
| TOOLTIP | Tooltip | Context on hover/focus | [screens] | Draft | [owner] |
| TOAST | Toast | Non-blocking status feedback | [screens] | Draft | [owner] |
| PROGRESS | Progress Indicator | Determinate/indeterminate progress | [screens] | Draft | [owner] |
| TEXT-INPUT | Text Input | Validated player text entry | [screens] | Draft | [owner] |
| TAB-BAR | Tab Bar | Local screen navigation | [screens] | Draft | [owner] |
| DRAG-DROP | Drag and Drop | Pointer/touch move with non-drag alternative | [screens] | Draft | [owner] |

## 3. Pattern Contract Template

Create one subsection per catalog row.

### [ID] — [Pattern Name]

**Intent:** [player goal]

**Inputs:** Pointer | Keyboard | Gamepad | Touch | Assistive technology

**States:** Default | Hovered | Focused | Pressed | Disabled | Busy | Error

| Trigger | Guard | State/command | Visual | Audio/Haptic | Announcement |
|---|---|---|---|---|---|
| [input] | [precondition] | [typed action] | [feedback] | [feedback] | [accessible name/state/result] |

**Navigation and focus**

- Initial focus: [deterministic element/rule]
- Directional/tab order: [logical order; no unreachable element]
- Submit: [action]
- Cancel/back: [destination and state restoration]
- Modal behavior: [focus trap and return target]
- Dynamic content: [focus preservation/fallback]

**Validation and failure**

- Disabled is not the only explanation; expose the reason when needed.
- Destructive actions require confirmation and a safe default focus.
- Async actions expose busy/cancel/error/retry state and suppress duplicate submit.

**Accessibility**

- Accessible name, role, value/state, hint, and result announcement: [contract]
- Text scale/reflow behavior: [minimum/maximum and clipping rule]
- Non-color/non-audio alternatives: [contract]
- Reduced motion/flashing behavior: [contract]
- Hold/repeated/precision input alternative: [contract]

**Unity implementation notes**

- UI Toolkit: name the `VisualElement` hierarchy, USS classes, event callbacks,
  binding/lifecycle disposal, and focus/navigation behavior.
- Existing UGUI exception: name the owning canvas/prefab/component and ADR.
- Do not use per-frame polling for state that can be pushed through the approved
  typed boundary. Avoid repeated queries, closure churn, string formatting, and
  rebuilding large trees. Use virtualization for large lists.
- Localized text uses the approved Unity Localization/String Table boundary;
  do not hardcode player-facing strings.

**Tests/evidence**

- EditMode: [plain presenter/format/validation behavior]
- PlayMode/integration: [focus, lifecycle, binding, navigation when needed]
- Accessibility/manual: [keyboard/gamepad/touch/screen-reader/platform checks]
- Performance: [Profiler marker/budget and representative content size]

## 4. Global Navigation Contract

| Context | Keyboard | Gamepad | Touch/Pointer | Expected result |
|---|---|---|---|---|
| Move focus | Tab/arrows | D-pad/stick | hover/tap | Deterministic reachable focus |
| Submit | Enter/Space | Submit action | click/tap | One action only |
| Cancel/back | Escape | Cancel action | explicit Back | Returns to documented parent |
| Page/section | Page keys | bumpers/triggers if approved | swipe/buttons | Same content/order |

Input uses the project's Input System action maps and does not read legacy
`Input.*`. Rebinding, device change, and last-input prompts must not destroy
current focus or duplicate callbacks.

## 5. Loading, Empty, Error, and Offline States

Every data-driven screen specifies:

| State | Content | Available actions | Focus target | Announcement |
|---|---|---|---|---|
| Loading | [skeleton/progress] | [cancel if safe] | [target] | [message] |
| Empty | [reason/help] | [primary recovery] | [target] | [message] |
| Error | [stable error copy/code] | [retry/back] | [target] | [message] |
| Offline | [cached/limited state] | [reconnect/back] | [target] | [message] |

## 6. Visual/Audio/Motion Tokens

Reference tokens from the design/art system rather than embedding values:

- Color and contrast tokens: [links]
- Typography and text scale tokens: [links]
- Spacing, target size, safe-area, and responsive breakpoints: [links]
- Focus, selected, disabled, error, and destructive states: [links]
- UI audio event IDs and haptic policy: [links]
- Motion duration/easing and reduced-motion replacements: [links]

## 7. Performance Budgets

| Scenario | Representative size/device | Budget | Profiler marker/evidence |
|---|---|---|---|
| Screen open | [content/device] | [CPU/frame/alloc] | [artifact] |
| Scroll large list | [N rows/device] | [frame/alloc] | [artifact] |
| Rapid navigation | [rate/device] | [no duplicate events] | [artifact] |
| Localization/text scale | [locale/scale] | [layout budget] | [artifact] |

Budgets require measured Editor/device/build evidence. Inspection alone is
`NOT MEASURED`.

## 8. Acceptance Matrix

| Pattern ID | Screen | Requirement/AC | Test/evidence | Executed result | Owner |
|---|---|---|---|---|---|
| [ID] | [screen] | [AC] | `Assets/Tests/...::Method` or dated evidence | PASS/FAIL/NOT RUN | [owner] |

## 9. Change History

| Date | Pattern | Change | Usage impact | Approval | Verification |
|---|---|---|---|---|---|
| [date] | [ID] | [summary] | [screens] | [owner] | [artifacts] |

Open questions that change public UI contracts, input actions, localization
schema, assemblies, or serialized ownership become ADR/story decisions before
implementation.
