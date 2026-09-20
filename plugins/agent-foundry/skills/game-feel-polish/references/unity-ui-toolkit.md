# Liquid UI with Unity UI Toolkit

Use for code-drawn menus, animated HUDs and Liquid UI-style controls. This is an
original Unity adaptation guide, not a drop-in port or a new UI framework.

## Rendering and input

Use VisualElement.generateVisualContent with MeshGenerationContext.painter2D
or the mesh API for skewed plates, shadows and custom fills. Draw current
presentation state; advance animation outside the drawing callback. Call
MarkDirtyRepaint when drawing state changes. Use contentRect/resolved layout
and skip zero-sized geometry. Do not retain the drawing context or allocate a
new material, texture or managed vertex array each repaint.

Keep labels as native text elements for shaping, localization and wrapping.
Use USS for layout, theme tokens and supported transitions. The Godot source's
avoidance of Theme/StyleBox does not mean Unity styles cannot animate. Separate
stable layout/hit targets from moving decoration; decoration should ignore picking.

Prefer native Button activation semantics with custom visuals. A custom input
element needs focusability, pointer capture/release, cancel, keyboard/gamepad
submission and disabled checks. Exit, capture loss and detach cancel a press.
Route accepted input through one command to avoid double-submitting click and
navigation events. Disabled controls never execute gameplay; do not re-enable
one to reproduce the source refusal animation. Use the project's Input System
and runtime panel event setup; no legacy Input polling.

## Widget recipes

| Widget | Presentation model | Unity behavior |
| --- | --- | --- |
| Button | select, press, intro, refusal | Compose channels in one update; hover and focus drive selection; retain readable disabled/focus states |
| Menu | order, intro style, stagger slot | Source styles: slide, drop, rise, pop, flip, fade. Separate order/style; cancel pending arrivals on close; restore focus on reopen |
| Counter | target, display, tint, scale | Update text when formatted value changes; retarget from current display; finish exactly at target; support decrease and zero |
| Bar | target, front, ghost, hold deadline | Clamp normalized display; handle nonpositive maximum; loss holds/drains ghost; gain animates display; cancel obsolete drains |
| Toast stack | bounded entries, expiry, offsets | Source cap 5 as a starting point; retire oldest, cancel callbacks, assign reuse generation; retain essential text with motion off |
| Tooltip | owner, anchor, delay, visibility | Show on focus and hover; dismiss on cancel/focus loss; clamp to panel bounds and support long localized content |
| Backdrop | palette blend, decorative clock | Source has five palette transitions; suspend hidden/detached updates; reduced motion freezes a readable palette |
| Palette | semantic colors, typography | Preserve contrast, focus and disabled tokens; use project fonts without importing upstream assets |

UI Toolkit has no RectTransform.anchoredPosition, CanvasGroup or Image.fillAmount.
Map presentation channels to style transforms, opacity, clipping or generated
geometry. Approximate a requested flip with a deliberate 2D collapse/expand unless
a real 3D surface is in scope. Prefer flex layout; add manual reflow only as needed.

## Lifetime and motion

Register callbacks once, release external subscriptions on DetachFromPanelEvent,
and restore them once on attachment. Pause scheduled work when idle/detached.
Use a reuse generation so an old expiry cannot remove a new pooled toast.
Cancel animation and restore owned visual state on disable/recycle. Use unscaled
elapsed time for UI motion and bounded deltas after long stalls.

Motion-off snaps counters/bars to current targets, stops bobbing and intros,
and preserves text, focus and notifications. Honor existing mute/reduced-motion
preferences. A visual A/B toggle is not permission to hide essential feedback.

## Acceptance scenarios

- Twenty rapid presses with hover/focus changes: one action per accepted
  activation and no stale scale, offset or opacity after settling.
- Close during stagger, reopen, resize, detach/reattach: no late callbacks,
  duplicate subscriptions, off-screen tooltip or lost focus.
- Retarget counter/bar during animation, including decrease, zero maximum and
  motion toggle: correct final display without changing the model.
- Overflow toast cap, reuse an entry, then expire old deadlines: the new entry
  survives to its own deadline and live count remains bounded.
- Mouse, touch where targeted, keyboard and gamepad: matching commands and
  visible focus; disabled controls never activate.
- Supported aspect ratios, panel scales and localized text lengths remain usable.
  Profile idle/active widgets after warm-up in the target player.

## Sources and limits

Reviewed upstream commit: 91311f7c4535ca29619add25a1ff72b0f9c6fa1b on 2026-09-20:
[Miisan's Liquid UI Kit](https://github.com/Miisan-png/godot-liquid-ui/tree/91311f7c4535ca29619add25a1ff72b0f9c6fa1b).
Compare scripts/ui and scripts/core only when needed. Upstream README declares
MIT; bundled audio/font/icon licenses are separate. This guide ships none of
those assets. Preserve the repository THIRD_PARTY_NOTICES.md when redistributing.
Sliders, checkboxes, dropdowns, tabs and modals are roadmap items, not source
widgets implemented at that commit; design them separately if requested.

Check APIs against the target Unity version:

- [Custom visual generation](https://docs.unity.com/en-us/engine/6000.6/script-reference/unityengine/uielements/visualelement/generatevisualcontent)
- [VisualElement and repaint](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/uielements/visualelement)
- [Navigation events](https://docs.unity.com/en-us/engine/6000.7/manual/uitoolkits/uielements/uie-events/reference/uie-navigation-events)

These API references do not establish a tested minimum version for this guide.
