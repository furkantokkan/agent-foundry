# Tuning numbers

Defaults from the Liquid UI Kit. Everything below lives in one config
resource (`JuiceConfig`) or in a widget's exported properties, so a designer
changes them in the inspector. Change one number at a time and A/B it.

## Impact tiers

Trauma passed to `Juice.shake()`:

| Trauma | Reads as |
| --- | --- |
| 0.10 to 0.15 | UI click |
| 0.20 | pickup |
| 0.30 | light hit |
| 0.45 | solid hit |
| 0.75 | critical |
| 0.80 to 0.85 | explosion, overload |

Hitstop length in seconds:

| Seconds | Reads as |
| --- | --- |
| 0.03 | light hit, UI press |
| 0.08 | config default |
| 0.09 | heavy hit (the useful one) |
| 0.12 to 0.13 | kill, overload |
| 0.20 | starts to feel like the game froze |

`impact(position, strength)` composite (strength 0 to 1):

| Channel | Mapping |
| --- | --- |
| Shake (with distance falloff, radius 600 px) | lerp(0.18, 0.75, strength) |
| Hitstop | lerp(0.035, 0.13, strength) s |
| Screen flash, only when strength > 0.25 | white, alpha lerp(0.0, 0.4, strength), 0.1 s |
| Chromatic aberration, only when strength > 0.45 | lerp(0.0, 0.009, strength) |
| Zoom punch, only when strength > 0.45 | lerp(0.0, 0.05, strength) |
| Rumble weak / strong / duration | lerp(0.15, 0.7) / lerp(0.2, 0.9) / lerp(0.1, 0.3) s |
| Sound bank | `hit_heavy` when strength > 0.5, else `hit_light` |

Distance falloff for `shake_at`: `falloff = 1 - clamp(distance / radius)`,
applied squared (`amount * falloff * falloff`).

## JuiceConfig defaults

| Group | Property | Default |
| --- | --- | --- |
| Master | enabled | true |
| Master | master_intensity | 1.0 (range 0 to 2) |
| Screen shake | shake_max_offset | (26, 18) px |
| Screen shake | shake_max_roll | 0.06 rad |
| Screen shake | shake_decay | 2.4 per second |
| Screen shake | shake_frequency | 42 |
| Screen shake | shake_power | 2.0 (trauma exponent) |
| Hitstop | hitstop_scale | 0.0 |
| Hitstop | hitstop_duration | 0.08 s |
| Slow motion | slowmo_scale | 0.35 |
| Slow motion | slowmo_duration | 0.6 s |
| Slow motion | slowmo_blend_in | 0.05 s |
| Slow motion | slowmo_blend_out | 0.25 s |
| Punch | punch_amount | 0.25 (scale +25 %) |
| Punch | punch_duration | 0.32 s |
| Punch | squash_amount | 0.3 |
| Screen effects | flash_color | white, alpha 0.55 |
| Screen effects | flash_duration | 0.12 s |
| Screen effects | chromatic_amount | 0.006 |
| Screen effects | chromatic_duration | 0.22 s |
| Hit flash | hit_flash_color | white |
| Hit flash | hit_flash_duration | 0.09 s |
| Damage numbers | damage_number_lifetime | 0.9 s (crit x1.25) |
| Damage numbers | damage_number_rise | 130 px/s initial (crit x1.3) |
| Damage numbers | damage_number_spread | 34 px horizontal drift |
| Damage numbers | damage_number_color | (1.0, 0.96, 0.85) |
| Damage numbers | damage_number_crit_color | (1.0, 0.72, 0.22) |
| Rumble | rumble_weak / rumble_strong / rumble_duration | 0.35 / 0.55 / 0.18 s |
| Audio | sfx_bus | Master (falls back to Master when the bus is missing) |
| Audio | pitch_variation | (0.92, 1.08) |
| Audio | sfx_dedupe_ms | 25 ms per bank |
| Audio | sfx_voice_count | 24 players per kind (positional and flat) |

## Camera

| Property | Default | Note |
| --- | --- | --- |
| Noise | simplex, frequency 1.0, random seed | offset x, offset y, and roll sample three noise lanes |
| Real-time delta | on (`ignore_time_scale`) | clamp dt to 0.1 s so a stall cannot fling the spring |
| Kick spring | stiffness 120, damping 14 | `kick(direction, 12)` adds `direction * strength * 10` to velocity |
| Zoom punch | amount 0.06, duration 0.28 s | 25 % out quad ease-out, 75 % back elastic ease-out |

## Tween helpers

| Helper | Shape |
| --- | --- |
| punch_scale (0.25, 0.32 s) | out 22 % quad ease-out to rest x (1 + amount), back 78 % elastic ease-out |
| squash_stretch (0.3, 0.36 s, axis) | out 20 % quad, back 80 % elastic; stretch = (1 + a) along the axis, 1 / (1 + a) across it |
| pop_in (0.4 s, from 0) | scale from rest x from to rest, back ease-out |
| pop_out (0.25 s) | scale to zero, back ease-in, optional `queue_free` |
| punch_rotation (8 deg, 0.4 s) | out 20 % quad, back 80 % elastic |
| shake_position (6 px, 0.3 s) | random offset scaled by (1 - t), then settle to rest |
| flash_modulate (white, 0.12 s) | to colour in 30 %, back to rest in 70 % |

## Hit flash

Whitens for 0.09 s: hold full for 34 % of the duration, then fade to 0 over
66 % with quad ease-out. The shader mixes toward the colour (not additive)
and never touches alpha, so the flash reads the same on dark and bright
sprites and never leaks outside the silhouette.

## Damage numbers

| Property | Value |
| --- | --- |
| Pool limit | 64 labels; beyond that, free instead of pool |
| Font size | 22 (crit 32); outline 6 (crit 8), outline colour black at 0.85 alpha |
| Start scale | 0.6 (crit 0.4) |
| Pop | to 1.1 (crit 1.35) over 16 % of lifetime with back ease-out, then to 1.0 over 20 % quad ease-out |
| Motion | y = -rise * t + 0.5 * 420 * t^2 (gravity arc), x drift random in +-spread |
| Fade | hold opaque for 30 % of lifetime, then fade alpha over 34 % |

Fading from the start makes the number unreadable while it still matters.

## Screen look presets

| Look | curvature | scanlines | mask | grain | flicker | bloom | brightness | saturation | vignette |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OFF | 0 | 0 | 0 | 0 | 0 | 0 | 1.0 | 1.0 | 0 |
| SUBTLE | 0.03 | 0.07 | 0.06 | 0.035 | 0 | 0.18 | 1.02 | 1.0 | 0.18 |
| ARCADE | 0.22 | 0.26 | 0.34 | 0.06 | 0.25 | 0.5 | 1.1 | 1.12 | 0.32 |
| HANDHELD | 0 | 0.1 | 0.55 | 0.02 | 0 | 0.1 | 1.05 | 0.72 | 0.22 |
| BROKEN | 0.38 | 0.4 | 0.45 | 0.22 | 0.8 | 0.7 | 1.0 | 0.65 | 0.5 |

`set_look()` cross-fades every value over 0.45 s (cubic ease-out). BROKEN
works as a sting: snap to it in about 0.08 s on a failure, hold about half a
second, fade back over 0.5 s.

Pulses layered on the look: chromatic 0.006 over 0.22 s (quint ease-out),
vignette pulse 0.5 over 0.4 s (quad ease-out), warp 0.5 over 0.35 s (quint
ease-out). `glitch(strength, 0.3 s)` = warp 0.5 x strength + chromatic
0.012 x strength + a pale blue flash at 0.16 x strength alpha for 40 % of the
duration.

## UI widgets

| Widget | Property | Default |
| --- | --- | --- |
| JuiceButton | skew / shadow_offset | 20 px / (7, 7) px |
| JuiceButton | select_slide / select_grow / press_squash | 24 px / 0.07 / 0.10 |
| JuiceButton | select tween | 0.22 s back ease-out |
| JuiceButton | press tween | 0.06 s in, 0.22 s out back ease-out; shadow shrinks to 25 % while pressed |
| JuiceButton | refusal shake | amount 1 to 0 over 0.45 s elastic; two sines at 74 Hz x 9 px and 131 Hz x 4 px |
| JuiceButton | intro / outro | 0.45 s back ease-out over 520 px travel / 0.3 s back ease-in over 620 px |
| JuiceButton | juicy_press | shake 0.1 + hitstop 0.03 on press |
| JuiceButton | sounds | hover `click` at -10 dB, press `confirm` at -4 dB, blocked `error` at -6 dB |
| JuiceMenu | stagger | 0.06 s per step; outro uses 60 % of the intro delay |
| JuiceCounter | roll_time / min / max | 0.55 s / 0.12 s / 1.1 s |
| JuiceCounter | roll duration | roll_time x clamp(magnitude / max(abs(previous), 1), 0.15, 2.0), clamped to min and max |
| JuiceCounter | punch | scale 1 + 0.22, back over 0.4 s elastic; tint returns over 0.3 s quad (faster than scale) |
| JuiceBar | fill_time | 0.16 s quad ease-out |
| JuiceBar | ghost_delay / ghost_time | 0.25 s hold, then 0.45 s cubic ease-in-out drain |
| JuiceBar | loss rattle | strength clamp((previous - value) x 3, 0.2, 1.0) decaying over 0.4 s; 5 px at 96 Hz and 77 Hz |
| JuiceBar | gain pulse | fill lerps to gain colour and back over 0.35 s |
| JuiceToast | in / hold / out | 0.24 s back ease-out (slides 90 px, grows 0.86 to 1.0) / 1.4 s / 0.26 s back ease-in |
| JuiceToast | rattle on entry | 0.5 s decay; 6 px at 88 Hz and 71 Hz |
| ToastLayer | slot height / margin / max visible | 56 px / (26, 26) px / 5, oldest retired first |
| ToastLayer | reflow | 0.28 s cubic ease-out on position y |
| JuiceTooltip | show / hide | 0.22 s back ease-out rising 14 px / 0.14 s quad ease-in |
| JuiceTooltip | bob | sin(t x 2.6) x float_height 6 px x 0.5 while open |
| JuiceBackdrop | palette cycle | 22 s per palette, last 45 % of the period cross-fades |

## Palette

INK 101426, CREAM f5efdc, GOLD ffc233, PINK ff4f8b, CYAN 4fd6ff, MINT 6ee7a0,
RED ff5c5c. Accent wheel by index: GOLD, CYAN, PINK, MINT, RED. Gain colour
MINT, loss colour RED, crit GOLD.
