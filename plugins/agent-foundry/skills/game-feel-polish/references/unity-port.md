# Unity implementation guide

Adapt behavior, not Godot APIs. Inspect ProjectVersion.txt, package versions,
the render pipeline and existing owners first. Use UI Toolkit for new
screen-space UI; preserve UGUI within an existing UGUI bounded context.
The names below describe responsibilities, not supplied or compiled C# types.

## Ownership and scope

Keep gameplay results separate from presentation. Extend existing feedback
services and the established ServiceLocator, otherwise the project's approved
composition mechanism. Do not install another tween, DI, audio or render stack.
Use typed requests and the repository's C# naming conventions (otherwise
m_camelCase instance fields, s_camelCase static fields, k_camelCase constants).
Implement only requested channels. Config can begin as plain C# data; new
ScriptableObject assets, scene wiring, renderer settings, packages and Input
Actions changes require target approval.

## Source mapping

| Source | Unity adaptation | Invariant |
| --- | --- | --- |
| juice.gd, juice_config.gd | Existing feedback service and typed settings | One enable/intensity policy; no gameplay mutations |
| juice_tween.gd | Existing tween library or bounded unscaled animation driver | Replace one channel at a time; restore owned rest state |
| juice_time.gd | Hitstop/slowmo requests to the time owner | Pause dominates; no unconditional reset to 1 |
| shake_camera_2d.gd | Rig offset layer or installed Cinemachine integration | Offset affects the rendered camera without fighting follow |
| hit_flash.gd | Supported shader property or existing sprite tint channel | Preserve existing properties; restore owned contribution |
| damage_numbers.gd | Bounded pool in the existing world-label/UI stack | Convert world coordinates to the correct panel/canvas |
| juice_sfx.gd, sfx_bank.gd, sfx_library.gd | Typed bank data and capped AudioSource pool | No immediate repeat; explicit build-included references |
| screen_fx.gd | Pipeline-specific screen effect adapter | Optional; exclude the pass when inactive |
| juice_palette.gd | Semantic palette and project typography | Native text shaping and localization |
| juice_button.gd, juice_menu.gd | UI Toolkit controls and stagger controller | One activation path across input devices |
| juice_counter.gd, juice_bar.gd | Displayed values and ghost-fill state | Never animate authoritative data |
| juice_toast.gd, toast_layer.gd | Bounded notification presenter | Essential text survives motion-off |
| juice_tooltip.gd, juice_backdrop.gd | Focus-aware overlay and decorative element | Clamp tooltip; suspend hidden decorative updates |

Read unity-ui-toolkit.md for widget implementation and acceptance scenarios.

## Time, camera and cancellation

Use an unscaled monotonic clock for deadlines. Extend hitstop with
end = max(existingEnd, now + duration); a shorter request cannot shorten it.
The time service resolves pause, hitstop and slowmo precedence. Removing feel
requests must preserve active pause and other slowmo requests. If no time owner
exists, agree on that public contract before introducing one. Never independently
write Time.timeScale from multiple components. Change fixedDeltaTime only through
the owning physics/time policy; restore its baseline even if timeScale already
equals the desired value.

Trauma is additive and clamped to [0,1]; scale noise by trauma squared and decay
with unscaled delta. Apply it to a transform that moves the camera: moving an
empty child below a Camera does not move its parent. With Cinemachine use the
installed version's extension/impulse mechanism, not a second transform writer.
Keep zoom as an owned contribution and remove it on cancellation and completion.

Unregister listeners and cancel timers/tweens on disable, detach and pool return.
Handle focus loss and scene unload through the project's pause policy. Release
only owned rumble, voices, camera offsets and post-processing contributions.

## Animation and audiovisual feedback

Capture rest values after layout/binding is valid. Rebase on intentional layout
changes, not from an animated intermediate value. Track cancellation by target
and channel; avoid static caches retaining destroyed objects. Suppress obsolete
completion callbacks. Source punch timing is 22% attack and 78% settle;
tuning-numbers.md contains source baselines, not universal Unity measurements.

For flash, check the shader contract. Merge existing MaterialPropertyBlock values
and coordinate the writer; profile batching implications in the target pipeline.
Never use renderer.material per hit. Use a tint route only where the project
already supports that renderer/material.

Use explicit build-included references or the project's Addressables catalog
for audio, not AssetDatabase or runtime directory scans. Handle empty banks,
single-clip banks, missing assets and pool saturation. No-repeat selection must
terminate with one clip. Stop/recycle before changing a reused voice's pitch.
Deduplicate per bank using unscaled time; source defaults are 25 ms and 0.92-1.08
pitch. Pool damage labels and specify world-to-panel/canvas conversion.

## Screen looks

OFF, SUBTLE, ARCADE, HANDHELD and BROKEN are source preset names, not Unity APIs.
Use the installed pipeline/version's full-screen route. Do not copy a Godot
screen-texture shader into ShaderLab or promise identical output. URP RenderGraph
and compatibility routes differ; target the installed mode only. Specify whether
UI participates: overlay UI is not automatically part of a camera post pass.
Supply an unscaled clock if grain must continue during hitstop. Reduced motion
disables disruptive effects. Measure bandwidth and target-device performance.

## Verification boundary

EditMode: deadline overlap, cancellation, counter/bar target changes, bank edge
cases, caps and reuse. PlayMode/manual: rapid activation, paused UI, detach/reattach,
camera ownership, scene unload, motion-off and keyboard/gamepad parity. Verify
shader/asset inclusion in a built player and measure allocations after warm-up.
This guide is not a tested runtime package; report unavailable Unity checks.
