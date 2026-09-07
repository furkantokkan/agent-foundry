---
paths:
  - "Assets/Game/UI/**/*.cs"
  - "Assets/Game/UI/**/*.uxml"
  - "Assets/Game/UI/**/*.uss"
---

# UI Code Rules

- UI code must stay thin: render state, collect intent, and delegate commands to
  application/gameplay services. Do not put gameplay rules in views.
- UI dependencies should be explicit and replaceable for tests. Avoid reaching
  directly into global game state.
- UI must NEVER own or directly modify game state — display only, use commands/events to request changes
- All UI text must go through the localization system — no hardcoded user-facing strings
- Support both keyboard/mouse AND gamepad input for all interactive elements
- All animations must be skippable and respect user motion/accessibility preferences
- UI sounds trigger through the audio event system, not directly
- UI must never block the game thread
- Scalable text and colorblind modes are mandatory, not optional
- Test all screens at minimum and maximum supported resolutions
- Use UI Toolkit for screen-space menus and HUDs when it fits the feature.
  Preserve uGUI for existing UI, world-space UI, keyframed animation, or other
  use cases selected by the approved UI architecture.
- UI Toolkit does not automatically replace uGUI; record the chosen system in
  the screen or UI architecture specification.
