# Polish checklist

Use this file in Phase 2 (audit), Phase 4 (implementation review), and
Phase 5 (verification) of `game-feel-polish`.

## Audit table (Phase 2)

One row per player action in scope. Fill "now" from the code, fill "plan"
with the smallest set that makes the tier read.

| Action | Tier | On-object | Camera | Screen | Time | Audio | Haptic | UI text | Now | Plan |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| e.g. light attack lands | solid hit | hit flash, punch | shake 0.45 | none | hitstop 0.09 | hit_light | weak 0.15 | damage number | flash only | + shake, hitstop, number |

Channel key:

- On-object: punch scale, squash and stretch, hit flash, punch rotation,
  position shake, pop in or out.
- Camera: trauma shake with distance falloff, recoil kick, zoom punch.
- Screen: white flash, chromatic aberration, vignette pulse, warp, glitch,
  look sting (BROKEN), fade to or from.
- Time: hitstop (scale 0, 0.03 to 0.13 s), slow motion (0.2 to 0.35 scale,
  0.4 to 0.6 s with blend in and out).
- Audio: bank name plus volume offset. Hover about -10 dB, press about -4 dB,
  refusal about -6 dB, world hits at 0 dB.
- Haptic: weak and strong motor plus duration.
- UI text: damage number (crit flag, colour), counter roll, toast (colour,
  hold), tooltip.

## Implementation review (Phase 4)

Hub and configuration:

- [ ] One hub routes scoped effects through existing time, camera, screen,
      audio and UI owners. No second tween, audio, or DI stack added.
- [ ] `enabled` resets every system when turned off; `intensity` (0 to 2)
      multiplies every amount.
- [ ] Every default lives in one config resource; no magic numbers in
      gameplay code.
- [ ] `impact(position, strength)` exists and gameplay calls it with a tier
      strength instead of hand-composing effects.
- [ ] Widgets work with the hub missing (skip sound and shake only).
- [ ] Reduced-motion preference respected: shake, zoom, flash, time-scale
      changes, and rumble skipped; a static success or failure cue remains.

Camera and time:

- [ ] Shake is trauma-based, additive, clamped, squared; noise-driven offset
      and roll; decays by real time; delta clamped to 0.1 s.
- [ ] Hitstop and slowmo timed by the wall clock; hitstop wins over slowmo;
      a longer hitstop extends, a shorter one does not cut.
- [ ] Reset, scene change and hub disable release only feel time requests,
      preserving active pause/slowmo and the physics owner's baseline.

Tweens and sprites:

- [ ] Rest state recorded per node per channel; previous tween killed
      before a new one; `restore()` available.
- [ ] Impact tweens are asymmetric (about 20 % out, 80 % settle).
- [ ] Hit flash uses a shared shader material; a node with its own material
      falls back to a modulate flash instead of losing its material.
- [ ] Pivot centred before scaling controls.

Text and sound:

- [ ] Damage numbers pooled (cap 64); held opaque before fading; crit uses
      bigger size, longer life, warmer colour.
- [ ] Sound banks have 2 to 4 takes; no immediate repeat; pitch range about
      0.92 to 1.08; dedupe window 25 ms; voices capped and recycled oldest
      first; bus falls back when missing.
- [ ] Asset lists baked into a resource, not scanned at runtime.

Widgets:

- [ ] Separate tweens per channel (select, press, intro, refusal).
- [ ] Menu stagger order is separate from intro style; random slots seeded.
- [ ] Counter roll time scales with relative magnitude; tint returns faster
      than scale.
- [ ] Bar ghost holds then drains on loss; leads and flashes on gain; rattle
      scaled to the loss.
- [ ] Toasts capped; retired oldest first; the stack reflows with a tween.
- [ ] Screen pass is one combined shader; the quad hides when every
      parameter is zero; the clock uniform comes from script.

## Verification (Phase 5)

Evidence, not assertions. Capture a short clip or intermediate frames; a
static end-state screenshot cannot prove timing.

- [ ] A/B toggle: same screen with juice on and off. Note each effect that
      changes nothing visible and remove it.
- [ ] Spam test: 20 rapid presses or hits. No node ends at the wrong scale,
      rotation, or position; no stale time requests remain; no audio clipping.
- [ ] Pause, focus loss, and scene change during hitstop and during slowmo
      preserve the time owner's resolved state, including an active pause.
- [ ] Shake and screen grain keep moving during hitstop.
- [ ] Busy scene: numbers, voices, and toasts stay within caps; allocations
      measured after warm-up.
- [ ] Reduced-motion mode: no shake, zoom, flash, time change, or rumble; a
      static cue still confirms success and refusal.
- [ ] Gamepad and keyboard navigation trigger the same hover and press
      feedback as the mouse.
- [ ] Exported or built player tested, not only the editor (baked resources,
      shader compile, audio bus names).
- [ ] Performance: the full-screen pass is hidden when the look is OFF and
      no pulse is active; frame time compared before and after on the target
      device.

## Report template

```text
Scope: <feature / menu / HUD>, engine <name + version>, reduced-motion: <yes/no>
Hub: <existing / added>, config: <path>
Actions (before -> after):
| Action | Tier | Channels before | Channels after | Config values |
Evidence:
- A/B: <clip or frames>
- Spam / pause / scene-change: <result>
- Caps and allocations: <numbers>
- Built player: <yes/no, platform>
Residual risk: <what was not verified>
```
