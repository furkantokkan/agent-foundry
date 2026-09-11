---
name: game-feel-polish
description: >-
  Add or tune game feel and UI polish (juice) for a feature, menu, HUD, or hit.
  Covers screen shake, hitstop and slow motion, punch and squash tweens, hit
  flash, pooled damage numbers, toast stacks, animated counters and lag bars,
  staggered menu intros, CRT screen looks, and pooled SFX banks, using the
  Liquid UI juice-kit architecture and its tuned numbers for Godot 4 with a
  Unity port guide. Use when a request says juice, feel, feedback, impact,
  polish this menu/HUD/hit, or asks why an action feels flat.
---

# Game Feel Polish

Polish is feedback layered on top of a committed gameplay result. This skill
gives an agent one architecture for that layer and the numbers that make it
read as impact instead of noise. The systems are adapted from Miisan's Liquid
UI Kit for Godot 4 (MIT, see the repository `THIRD_PARTY_NOTICES.md`); the
same structure ports to Unity.

Use `team-polish` when the request is a multi-role release-hardening pass.
Use `unity-feel-interactions` when the project already uses the More Mountains
Feel package. Use this skill when the request is about how an action feels.

## Rules that hold in every engine

1. **One hub, one switch.** Every effect is a call on one hub (`Juice`
   autoload in Godot, one service in Unity). The hub owns `enabled` and a
   0 to 2 `intensity` multiplier. Turning `enabled` off must reset every
   system at once: time scale, camera, screen pass, pooled labels, voices,
   toasts, rumble. Widgets must still work when the hub is missing; they
   only skip sound and shake.
2. **Feel never decides gameplay.** Fire feedback after the committed
   result. A refused action (a disabled button) gets a refusal shake and an
   error sound; state does not change.
3. **Trauma, not "shake for N seconds".** Overlapping hits add trauma
   (clamped 0 to 1); the camera uses `trauma ^ 2` so small hits stay subtle
   and big ones slam. Decay by real time, not by scaled delta, so the shake
   keeps moving during hitstop.
4. **Wall-clock time for time effects.** Hitstop and slow motion measure
   their own end with the system clock; a freeze timed with scaled delta
   freezes its own countdown. Hitstop beats slow motion. A longer hitstop
   extends a running one; a shorter one never cuts it.
5. **Remember the rest state.** Tween helpers record the node's resting
   scale, rotation, position, and modulate the first time they touch it,
   kill the previous tween on that channel, and always return to rest.
   Spamming a punch can never leave anything stuck at the wrong size.
6. **Fast out, slow settle.** Impact tweens spend about a fifth of their
   time going out (quad ease-out) and the rest coming back (elastic
   ease-out). An even in and out reads as a wobble, not an impact.
7. **Every property is a float you can tween.** Draw widgets from polygons,
   text, and palette colours so hover, press, intro, and refusal are
   separate animated channels with their own tweens. A static style box or
   theme cannot animate.
8. **Sound is randomised and de-duplicated.** Each sound is a bank of
   several takes; never repeat the previous take, vary pitch about 0.92 to
   1.08, and drop a second trigger of the same bank inside 25 ms. Two
   identical samples on one frame double the amplitude and clip.
9. **Pool what fights spawn.** Damage numbers, audio players, and toasts are
   pooled or capped. Allocation on the hit frame is the stutter players
   notice.
10. **Scale everything to impact strength.** One `impact(position,
    strength)` call maps strength to shake, hitstop, flash, aberration, zoom
    punch, rumble, and the sound bank with tuned ratios. Screen-wide effects
    open only above a threshold so routine hits do not wash out big ones.
11. **Prove it with A/B.** Ship a toggle that disables all juice at once and
    compare the same screen with and without. If an effect makes no visible
    difference in that comparison, delete it.

## Workflow

### Phase 1: Read before touching anything

- Repository instructions (`AGENTS.md`, `CLAUDE.md`, path-scoped rules),
  the engine and version, and the project's motion or accessibility
  settings.
- Existing owners of time scale, camera offset, post-processing, tweening,
  and audio playback. Extend the existing owner; never add a second tween,
  audio, or DI stack.
- Existing feel code. If a hub or kill switch already exists, route through
  it instead of adding another.
- Whether the project relies on the engine's theme system. The kit's widgets
  draw themselves and ignore Godot themes; retrofitting a themed UI means
  configuring exported properties instead of inheriting colours.

### Phase 2: Audit the target

List every player action in scope and the feedback channels it has today:
on-object (punch, squash, flash), camera (shake, kick, zoom), screen (flash,
aberration, vignette, warp), time (hitstop, slowmo), audio, haptic, and UI
text (damage number, counter, toast). Classify each action by tier:

| Tier | Example | Shake trauma | Hitstop |
| --- | --- | --- | --- |
| UI click | button press | 0.10 to 0.15 | 0.03 s or none |
| Light hit | pickup, small damage | 0.30 | 0.03 s |
| Solid hit | normal attack landing | 0.45 | 0.09 s |
| Heavy hit or crit | critical, big enemy hit | 0.75 | 0.12 s |
| Kill or explosion | death, overload | 0.85 | 0.13 s |

Above 0.20 s of hitstop the game starts to feel frozen. Write the audit as a
table; the missing channels are the plan.

### Phase 3: Plan the smallest set

- Pick two or three channels per action, not all of them. Reserve
  screen-wide effects (flash, aberration, zoom punch, slowmo) for the top
  tiers.
- Decide ownership: the hub owns time scale, camera trauma, the screen
  pass, the voice pool, the toast stack, and pooled numbers. Widgets call
  the hub and degrade without it.
- Put every tunable in one config resource (Godot `JuiceConfig`, a Unity
  ScriptableObject) so designers change numbers without code edits.
- Respect the project's motion preference. When reduced motion is on, keep
  a static success or failure cue and skip shake, zoom, flash, time-scale
  changes, and rumble. Do not add those silently to a project that already
  has such a setting.

### Phase 4: Implement

Follow `references/juice-systems.md` for the Godot 4 systems and
`references/unity-port.md` for the Unity mapping. Build in this order: hub
and `impact()`, camera, tween helpers and hit flash, sound, UI widgets,
screen look. Keep each system in its own script and each widget's animation
channels on separate tweens so they overlap without fighting. Bake asset
lists (sound banks) into a resource; scanning the resource tree at runtime
works in the editor and fails in exported builds.

Start from the defaults in `references/tuning-numbers.md` and change one
number at a time.

### Phase 5: Verify

Run `references/polish-checklist.md`. Minimum evidence:

- A/B comparison of the same screen with juice on and off.
- Spam test: repeated presses or hits leave no node at the wrong scale,
  rotation, or position, no stuck time scale, and no clipping audio.
- Pause, focus loss, and scene change during an active hitstop or slowmo
  restore the time scale to 1.
- Camera shake keeps moving during hitstop (real-time delta) and screen
  grain keeps moving (clock fed from script, not shader time).
- Damage numbers, voices, and toasts stay within their caps in a busy
  scene; measure allocations after warm-up.
- An exported or built player, not only the editor.

Report changed files, the per-action channel table before and after, the
config values used, the A/B evidence, and residual risk. Report measured
performance and unverified requirements separately.

## Guardrails

- Do not tween gameplay state; tween presentation copies of it (displayed
  value, ghost fill, intro amount).
- Do not let a full-screen post pass run when every parameter is zero; hide
  the quad. Use one combined pass, not one pass per effect.
- Do not copy the kit's bundled assets without checking their licences. Its
  sounds (Kenney, CC0), font (Bungee, OFL), and brand icons (Simple Icons,
  CC0) are not part of this skill.
- Do not use true random for takes or stagger slots; no-repeat or seeded
  selection reads as designed, pure random reads as broken.
- Do not raise tier numbers to "make it feel stronger"; raise contrast by
  lowering routine feedback instead.

## Reference loading

- `references/juice-systems.md`: the kit's systems with condensed source.
- `references/tuning-numbers.md`: every default value in one place.
- `references/unity-port.md`: mapping each system to Unity C#.
- `references/polish-checklist.md`: audit table, verification list, report.

Related skills: `team-polish` for multi-role hardening, `unity-optimization`
for measured performance work, `game-code-review` for review, `ux-review`
for accessibility and HUD validation.
