# Liquid UI juice systems (Godot 4)

Condensed from Miisan's Liquid UI Kit (`godot-liquid-ui`, MIT; see the
repository `THIRD_PARTY_NOTICES.md`). The excerpts keep the algorithms, the
defaults, and the reasons behind them. Editor plumbing, `@tool` redraw
setters, and most `_draw()` polygon code are described rather than copied.
Target: Godot 4.7, no plugins or addons. Indentation is shown with spaces;
Godot accepts spaces or tabs as long as one file is consistent.

## Layout and setup

| File | Class | Role |
| --- | --- | --- |
| `scripts/core/juice.gd` | autoload `Juice` | Hub. Every effect is a call here. |
| `scripts/core/juice_config.gd` | `JuiceConfig` | Every tunable in one resource (`assets/juice_config.tres`). |
| `scripts/core/shake_camera_2d.gd` | `ShakeCamera2D` | Trauma shake, recoil kick, zoom punch on a Camera2D. |
| `scripts/core/juice_time.gd` | `JuiceTime` | Hitstop and slow motion; owns `Engine.time_scale`. |
| `scripts/core/juice_tween.gd` | `JuiceTween` | Static punch, squash, pop, rotation, shake, flash helpers. |
| `scripts/core/hit_flash.gd` + `assets/shaders/hit_flash.gdshader` | `HitFlash` | Whitens a sprite for a few frames. |
| `scripts/core/damage_numbers.gd` | `DamageNumbers` | Pooled floating combat text. |
| `scripts/core/screen_fx.gd` + `assets/shaders/crt.gdshader` | `ScreenFX` | CRT look presets, screen flash, fades, pulses. |
| `scripts/core/juice_sfx.gd`, `sfx_bank.gd`, `sfx_library.gd` | `JuiceSfx`, `SfxBank`, `SfxLibrary` | Pooled, pitch-varied, de-duplicated sound playback. |
| `scripts/ui/juice_button.gd` | `JuiceButton` | Skewed plate button with four animation channels. |
| `scripts/ui/juice_menu.gd` | `JuiceMenu` | Deals buttons in on a stagger; keyboard and mouse. |
| `scripts/ui/juice_counter.gd` | `JuiceCounter` | Number that rolls to its value and punches on change. |
| `scripts/ui/juice_bar.gd` | `JuiceBar` | Progress bar with a ghost fill that lags a loss. |
| `scripts/ui/juice_toast.gd`, `toast_layer.gd` | `JuiceToast`, `ToastLayer` | Notification plates that stack and reflow. |
| `scripts/ui/juice_tooltip.gd` | `JuiceTooltip` | Floating hover tip that bobs while open. |
| `scripts/ui/juice_backdrop.gd` | `JuiceBackdrop` | Drawn sky, stars, sun, parallax ridges; palette cycle. |
| `scripts/ui/juice_palette.gd` | `JuicePalette` | Colours and the font. |

Setup:

1. Copy `scripts/` and `assets/` into the project.
2. Project Settings > Autoload: add `scripts/core/juice.gd` as `Juice`.
3. Put `shake_camera_2d.gd` on the Camera2D that should shake.
4. Edit numbers in `assets/juice_config.tres` from the inspector.
5. Sound banks are one folder per bank under `assets/audio/sfx/`; the bank
   list is baked into `assets/sfx_library.tres`. Rebuild that resource when
   folders change: scanning `res://` at runtime works in the editor and
   fails in an exported build.

Widgets are `@tool` scripts and draw live in the editor. They ignore Godot's
Theme system: colours and fonts come from exported properties and
`JuicePalette`, not from a theme.

## 1. The hub (`Juice` autoload)

Everything goes through here. `enabled = false` kills every effect at once,
which is how you check whether an effect is doing anything or only costing
frames.

```gdscript
extends Node

signal enabled_changed(is_enabled: bool)

const CONFIG_PATH := "res://assets/juice_config.tres"
# Autoloads sit before the main scene in the tree; without this every damage
# number would draw behind the game.
const WORLD_Z_INDEX := 100

var enabled: bool = true:
    set(value):
        if enabled == value:
            return
        enabled = value
        if not enabled:
            _silence()
        enabled_changed.emit(enabled)

var intensity: float = 1.0:
    set(value):
        intensity = clampf(value, 0.0, 2.0)

var config: JuiceConfig
var time: JuiceTime
var screen: ScreenFX
var numbers: DamageNumbers
var sfx: JuiceSfx
var toasts: ToastLayer
var world: Node2D
var _cameras: Array[ShakeCamera2D] = []


func _ready() -> void:
    process_mode = Node.PROCESS_MODE_ALWAYS  # keeps working while paused
    config = _load_config()  # JuiceConfig.new() with a warning when missing
    enabled = config.enabled
    intensity = config.master_intensity

    time = JuiceTime.new()
    time.setup(config)
    add_child(time)

    world = Node2D.new()
    world.z_index = WORLD_Z_INDEX
    add_child(world)

    numbers = DamageNumbers.new()
    numbers.setup(config)
    world.add_child(numbers)

    sfx = JuiceSfx.new()
    add_child(sfx)
    sfx.setup(config)

    toasts = ToastLayer.new()
    add_child(toasts)

    screen = ScreenFX.new()
    add_child(screen)


# Fires shake, hitstop, flash and sound together with the ratios already
# tuned. Start with this one.
func impact(world_position: Vector2, strength: float = 0.5) -> void:
    if not enabled:
        return
    strength = clampf(strength, 0.0, 1.0)

    shake_at(world_position, lerpf(0.18, 0.75, strength))
    hitstop(lerpf(0.035, 0.13, strength))

    # Screen-wide effects only open up past a threshold so ordinary hits do
    # not wash out the big ones.
    if strength > 0.25:
        flash(Color(1, 1, 1, lerpf(0.0, 0.4, strength)), 0.1)
    if strength > 0.45:
        chromatic(lerpf(0.0, 0.009, strength))
        zoom_punch(lerpf(0.0, 0.05, strength))
    rumble(lerpf(0.15, 0.7, strength), lerpf(0.2, 0.9, strength), lerpf(0.1, 0.3, strength))
    play_sfx(&"hit_heavy" if strength > 0.5 else &"hit_light", world_position)


func get_camera() -> ShakeCamera2D:
    _cameras = _cameras.filter(func(c: ShakeCamera2D) -> bool: return is_instance_valid(c))
    if _cameras.is_empty():
        return null
    var active := get_viewport().get_camera_2d()
    return active if active is ShakeCamera2D else _cameras.back()


func shake(amount: float = 0.4) -> void:
    if not enabled:
        return
    var camera := get_camera()
    if camera != null:
        camera.add_trauma(amount * intensity)


func shake_at(world_position: Vector2, amount: float = 0.5, radius: float = 600.0) -> void:
    if not enabled:
        return
    var camera := get_camera()
    if camera == null:
        return
    var distance := camera.global_position.distance_to(world_position)
    var falloff := 1.0 - clampf(distance / maxf(radius, 1.0), 0.0, 1.0)
    if falloff <= 0.0:
        return
    camera.add_trauma(amount * falloff * falloff * intensity)


func punch(node: CanvasItem, amount: float = -1.0, duration: float = -1.0) -> void:
    if not enabled:
        return
    if amount < 0.0:
        amount = config.punch_amount
    if duration < 0.0:
        duration = config.punch_duration
    JuiceTween.punch_scale(node, amount * intensity, duration)


func pop_out(node: CanvasItem, duration: float = 0.25, free_when_done: bool = false) -> void:
    if not enabled:
        if free_when_done and is_instance_valid(node):
            node.queue_free()  # disabling juice must never leak a node
        return
    JuiceTween.pop_out(node, duration, free_when_done)


func rumble(weak: float = -1.0, strong: float = -1.0, duration: float = -1.0) -> void:
    if not enabled:
        return
    if weak < 0.0:
        weak = config.rumble_weak
    if strong < 0.0:
        strong = config.rumble_strong
    if duration < 0.0:
        duration = config.rumble_duration
    for device in Input.get_connected_joypads():
        Input.start_joy_vibration(device, clampf(weak * intensity, 0.0, 1.0),
            clampf(strong * intensity, 0.0, 1.0), duration)


func _silence() -> void:
    time.reset()
    for camera in _cameras:
        if is_instance_valid(camera):
            camera.reset()
    screen.reset()
    numbers.clear()
    sfx.stop_all()
    toasts.clear()
    stop_rumble()
```

Full call list, all guarded by `enabled` unless noted, with amounts
multiplied by `intensity` and `-1.0` meaning "use the config default":

| Call | Delegates to |
| --- | --- |
| `shake(amount)`, `shake_at(pos, amount, radius)`, `kick(direction, strength)`, `zoom_punch(amount, duration)` | `ShakeCamera2D` |
| `hitstop(duration, scale)`, `slowmo(scale, duration)` | `JuiceTime` |
| `punch(node)`, `squash(node, amount, axis)`, `pop_in(node)`, `pop_out(node, duration, free)` | `JuiceTween` |
| `hit_flash(node, color, duration)` | `HitFlash` |
| `damage_number(pos, value, crit, color)` | `DamageNumbers` (returns the Label) |
| `toast(message, color, hold, icon)` | `ToastLayer` (returns the toast) |
| `flash(color, duration)`, `chromatic(amount, duration)`, `vignette(amount, duration)`, `warp(amount, duration)`, `glitch(strength, duration)` | `ScreenFX` pulses |
| `set_look(look, duration)`, `fade_to(color, duration)`, `fade_from(color, duration)` | `ScreenFX`; these run even when disabled because they are presentation state, not juice |
| `play_sfx(bank, position, volume_offset_db)` | `JuiceSfx` (null position = non-positional) |
| `rumble(weak, strong, duration)`, `stop_rumble()` | `Input` joypad vibration |

`ShakeCamera2D` registers itself with the hub in `_ready` and unregisters in
`_exit_tree`; the hub prefers the viewport's active camera when it is a
`ShakeCamera2D`.

## 2. Config (`JuiceConfig`)

A `@tool` `Resource` with `@export_group` sections: Master (enabled,
master_intensity), Screen Shake, Hitstop, Slow Motion, Punch / Squash &
Stretch, Screen Effects, Hit Flash, Damage Numbers, Rumble, Audio. Defaults
are listed in `tuning-numbers.md`. Every system receives the config through
`setup(config)`; nothing reads numbers from code constants.

## 3. Camera (`ShakeCamera2D`)

Takes trauma rather than "shake for N seconds at strength S". Overlapping
hits add up into one shake instead of fighting, and trauma is squared before
use so small hits stay subtle while big ones still slam.

```gdscript
class_name ShakeCamera2D
extends Camera2D

@export var max_offset: Vector2 = Vector2(26.0, 18.0)
@export_range(0.0, 0.5, 0.001) var max_roll: float = 0.06
@export_range(0.1, 10.0, 0.05) var decay: float = 2.4
@export_range(1.0, 120.0, 1.0) var frequency: float = 42.0
@export_range(1.0, 4.0, 0.1) var shake_power: float = 2.0
@export var ignore_time_scale: bool = true

@export_group("Recoil Kick")
@export_range(1.0, 400.0, 1.0) var kick_stiffness: float = 120.0
@export_range(1.0, 60.0, 0.5) var kick_damping: float = 14.0

var trauma: float = 0.0:
    set(value):
        trauma = clampf(value, 0.0, 1.0)

var _noise := FastNoiseLite.new()  # TYPE_SIMPLEX, frequency 1.0, random seed
var _noise_time: float = 0.0
var _base_offset: Vector2
var _base_rotation: float
var _base_zoom: Vector2
var _kick: Vector2 = Vector2.ZERO
var _kick_velocity: Vector2 = Vector2.ZERO
var _zoom_offset: float = 0.0
var _last_real_ms: int = 0


func _ready() -> void:
    _noise.noise_type = FastNoiseLite.TYPE_SIMPLEX
    _noise.frequency = 1.0
    _noise.seed = randi()
    rebase()
    _last_real_ms = Time.get_ticks_msec()
    var juice := get_node_or_null(^"/root/Juice")
    if juice != null:
        juice.register_camera(self)


func add_trauma(amount: float) -> void:
    trauma = trauma + amount


func kick(direction: Vector2, strength: float = 12.0) -> void:
    _kick_velocity += direction.normalized() * strength * 10.0


func zoom_punch(amount: float = 0.06, duration: float = 0.28) -> void:
    var tween := create_tween()
    tween.tween_property(self, "_zoom_offset", amount, duration * 0.25) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    tween.tween_property(self, "_zoom_offset", 0.0, duration * 0.75) \
        .set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)


func reset() -> void:
    trauma = 0.0
    _kick = Vector2.ZERO
    _kick_velocity = Vector2.ZERO
    _zoom_offset = 0.0
    offset = _base_offset
    rotation = _base_rotation
    zoom = _base_zoom


func rebase() -> void:  # call after you move the camera deliberately
    _base_offset = offset
    _base_rotation = rotation
    _base_zoom = zoom


func _process(delta: float) -> void:
    var real_now := Time.get_ticks_msec()
    var real_delta := float(real_now - _last_real_ms) / 1000.0
    _last_real_ms = real_now

    var dt := real_delta if ignore_time_scale else delta
    dt = minf(dt, 0.1)  # a long stall would otherwise fling the spring

    _update_kick(dt)

    if trauma <= 0.0:
        if _kick.is_zero_approx() and is_zero_approx(_zoom_offset):
            offset = _base_offset + _kick
            rotation = _base_rotation
            zoom = _base_zoom
            return
    else:
        trauma = maxf(trauma - decay * dt, 0.0)

    _noise_time += dt * frequency

    var amount := pow(trauma, shake_power)
    var shake_offset := Vector2(
        max_offset.x * amount * _noise.get_noise_2d(_noise_time, 0.0),
        max_offset.y * amount * _noise.get_noise_2d(0.0, _noise_time))

    offset = _base_offset + shake_offset + _kick
    rotation = _base_rotation + max_roll * amount * _noise.get_noise_2d(_noise_time, 100.0)
    zoom = _base_zoom * (1.0 + _zoom_offset)


func _update_kick(dt: float) -> void:  # damped spring back to zero
    if _kick.is_zero_approx() and _kick_velocity.is_zero_approx():
        return
    var accel := -kick_stiffness * _kick - kick_damping * _kick_velocity
    _kick_velocity += accel * dt
    _kick += _kick_velocity * dt
    if _kick.length_squared() < 0.01 and _kick_velocity.length_squared() < 0.01:
        _kick = Vector2.ZERO
        _kick_velocity = Vector2.ZERO
```

## 4. Time (`JuiceTime`)

Owns `Engine.time_scale`. Hitstop always beats slow motion: a hit landing
during bullet time should still read as a hit.

```gdscript
class_name JuiceTime
extends Node

signal hitstop_started(duration: float)
signal hitstop_ended()
signal slowmo_started(scale: float)
signal slowmo_ended()

var _config: JuiceConfig
var _hitstop_end_ms: int = 0
var _hitstop_scale: float = 0.0
var _hitstop_active: bool = false
var _slowmo_active: bool = false
var _slowmo_start_ms: int = 0
var _slowmo_scale: float = 1.0
var _slowmo_blend_in_ms: int = 0
var _slowmo_hold_ms: int = 0
var _slowmo_blend_out_ms: int = 0


func hitstop(duration: float = -1.0, scale: float = -1.0) -> void:
    if duration < 0.0:
        duration = _config.hitstop_duration
    if scale < 0.0:
        scale = _config.hitstop_scale
    if duration <= 0.0:
        return
    var end_ms := Time.get_ticks_msec() + int(duration * 1000.0)
    if end_ms <= _hitstop_end_ms:
        return  # a shorter hitstop never cuts a longer one
    _hitstop_end_ms = end_ms
    _hitstop_scale = scale
    if not _hitstop_active:
        _hitstop_active = true
        hitstop_started.emit(duration)
    _apply()


func slowmo(scale: float = -1.0, duration: float = -1.0,
        blend_in: float = -1.0, blend_out: float = -1.0) -> void:
    # -1 resolves to config: 0.35, 0.6 s, 0.05 s, 0.25 s
    _slowmo_scale = maxf(scale, 0.01)
    _slowmo_start_ms = Time.get_ticks_msec()
    _slowmo_blend_in_ms = int(blend_in * 1000.0)
    _slowmo_hold_ms = int(duration * 1000.0)
    _slowmo_blend_out_ms = int(blend_out * 1000.0)
    if not _slowmo_active:
        _slowmo_active = true
        slowmo_started.emit(_slowmo_scale)
    _apply()


func reset() -> void:
    var was_hitstop := _hitstop_active
    var was_slowmo := _slowmo_active
    _hitstop_active = false
    _hitstop_end_ms = 0
    _slowmo_active = false
    Engine.time_scale = 1.0
    if was_hitstop:
        hitstop_ended.emit()
    if was_slowmo:
        slowmo_ended.emit()


# Timed off the system clock, not delta. delta is scaled by time_scale, so a
# freeze written against it would freeze its own countdown.
func _process(_delta: float) -> void:
    if not (_hitstop_active or _slowmo_active):
        return
    var now := Time.get_ticks_msec()
    if _hitstop_active and now >= _hitstop_end_ms:
        _hitstop_active = false
        hitstop_ended.emit()
    if _slowmo_active:
        var total := _slowmo_blend_in_ms + _slowmo_hold_ms + _slowmo_blend_out_ms
        if now - _slowmo_start_ms >= total:
            _slowmo_active = false
            slowmo_ended.emit()
    _apply()


func _apply() -> void:
    var target := 1.0
    if _slowmo_active:
        target = _current_slowmo_scale()
    if _hitstop_active:
        target = _hitstop_scale
    if absf(Engine.time_scale - target) > 0.001:
        Engine.time_scale = target


func _current_slowmo_scale() -> float:
    var elapsed := Time.get_ticks_msec() - _slowmo_start_ms
    if elapsed < _slowmo_blend_in_ms:
        var t := float(elapsed) / float(maxi(_slowmo_blend_in_ms, 1))
        return lerpf(1.0, _slowmo_scale, smoothstep(0.0, 1.0, t))
    var hold_end := _slowmo_blend_in_ms + _slowmo_hold_ms
    if elapsed < hold_end:
        return _slowmo_scale
    if _slowmo_blend_out_ms <= 0:
        return 1.0
    var t_out := float(elapsed - hold_end) / float(_slowmo_blend_out_ms)
    return lerpf(_slowmo_scale, 1.0, smoothstep(0.0, 1.0, clampf(t_out, 0.0, 1.0)))
```

`_process` still runs when `Engine.time_scale` is 0 (delta becomes 0, the
callback does not stop), which is why the countdown must use the clock.

## 5. Tween helpers (`JuiceTween`)

Static helpers for any `CanvasItem`. They record the node's resting values
the first time they touch it and always return there, so spamming punches
can never leave something stuck at the wrong size.

```gdscript
class_name JuiceTween
extends RefCounted

const _META_REST_SCALE := &"_juice_rest_scale"
const _META_REST_ROTATION := &"_juice_rest_rotation"
const _META_REST_POSITION := &"_juice_rest_position"
const _META_REST_MODULATE := &"_juice_rest_modulate"


static func punch_scale(node: CanvasItem, amount: float = 0.25, duration: float = 0.32) -> Tween:
    if not _can_juice(node):
        return null
    var rest := _rest_scale(node)
    _kill(node, &"scale")

    var tween := node.create_tween()
    node.set_meta(&"_juice_tween_scale", tween)
    # Fast out, slow settle. An even in and out reads as a wobble, not an impact.
    tween.tween_property(node, ^"scale", rest * (1.0 + amount), duration * 0.22) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    tween.tween_property(node, ^"scale", rest, duration * 0.78) \
        .set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
    return tween


static func squash_stretch(node: CanvasItem, amount: float = 0.3,
        duration: float = 0.36, axis: Vector2 = Vector2.RIGHT) -> Tween:
    if not _can_juice(node):
        return null
    var rest := _rest_scale(node)
    _kill(node, &"scale")

    var a := absf(axis.normalized().x)
    var stretch := Vector2(
        lerpf(1.0 / (1.0 + amount), 1.0 + amount, a),
        lerpf(1.0 + amount, 1.0 / (1.0 + amount), a))

    var tween := node.create_tween()
    node.set_meta(&"_juice_tween_scale", tween)
    tween.tween_property(node, ^"scale", rest * stretch, duration * 0.2) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    tween.tween_property(node, ^"scale", rest, duration * 0.8) \
        .set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
    return tween


static func pop_in(node: CanvasItem, duration: float = 0.4, from: float = 0.0) -> Tween:
    if not _can_juice(node):
        return null
    var rest := _rest_scale(node)
    _kill(node, &"scale")
    node.scale = rest * from
    var tween := node.create_tween()
    node.set_meta(&"_juice_tween_scale", tween)
    tween.tween_property(node, ^"scale", rest, duration) \
        .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    return tween


static func pop_out(node: CanvasItem, duration: float = 0.25, free_when_done: bool = false) -> Tween:
    if not is_instance_valid(node):
        return null
    _rest_scale(node)
    _kill(node, &"scale")
    var tween := node.create_tween()
    node.set_meta(&"_juice_tween_scale", tween)
    tween.tween_property(node, ^"scale", Vector2.ZERO, duration) \
        .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
    if free_when_done:
        tween.tween_callback(node.queue_free)
    return tween


static func punch_rotation(node: CanvasItem, angle_degrees: float = 8.0, duration: float = 0.4) -> Tween:
    # same 20 % quad out / 80 % elastic back shape on rotation
    ...


static func shake_position(node: CanvasItem, strength: float = 6.0, duration: float = 0.3) -> Tween:
    if not _can_juice(node):
        return null
    var rest: Vector2 = _rest(node, _META_REST_POSITION, node.position)
    _kill(node, &"position")
    var step := func(t: float) -> void:
        if is_instance_valid(node):
            node.position = rest + Vector2(randf_range(-strength, strength),
                randf_range(-strength, strength)) * (1.0 - t)
    var settle := func() -> void:
        if is_instance_valid(node):
            node.position = rest
    var tween := node.create_tween()
    node.set_meta(&"_juice_tween_position", tween)
    tween.tween_method(step, 0.0, 1.0, duration)
    tween.tween_callback(settle)
    return tween


static func flash_modulate(node: CanvasItem, color: Color = Color.WHITE, duration: float = 0.12) -> Tween:
    # to colour in 30 % of the duration, back to the rest modulate in 70 %
    ...


static func center_pivot(control: Control) -> void:
    if is_instance_valid(control):
        control.pivot_offset = control.size * 0.5


static func restore(node: CanvasItem) -> void:
    if not is_instance_valid(node):
        return
    for key in [&"scale", &"rotation", &"position", &"modulate"]:
        _kill(node, key)
    if node.has_meta(_META_REST_SCALE):
        node.scale = node.get_meta(_META_REST_SCALE)
    if node.has_meta(_META_REST_ROTATION):
        node.rotation = node.get_meta(_META_REST_ROTATION)
    if node.has_meta(_META_REST_POSITION):
        node.position = node.get_meta(_META_REST_POSITION)
    if node.has_meta(_META_REST_MODULATE):
        node.modulate = node.get_meta(_META_REST_MODULATE)


static func _can_juice(node: CanvasItem) -> bool:
    if not is_instance_valid(node) or not node.is_inside_tree():
        return false
    var juice := node.get_node_or_null(^"/root/Juice")
    return juice == null or juice.enabled  # works without the autoload


static func _rest_scale(node: CanvasItem) -> Vector2:
    return _rest(node, _META_REST_SCALE, node.scale)


static func _rest(node: CanvasItem, meta: StringName, fallback: Variant) -> Variant:
    if not node.has_meta(meta):
        node.set_meta(meta, fallback)
    return node.get_meta(meta)


static func _kill(node: CanvasItem, key: StringName) -> void:
    var meta := StringName("_juice_tween_" + key)
    if not node.has_meta(meta):
        return
    var previous: Tween = node.get_meta(meta)
    if is_instance_valid(previous) and previous.is_valid():
        previous.kill()
    node.remove_meta(meta)
```

Call `center_pivot()` on a Control before scaling it, otherwise it grows
from its top-left corner.

## 6. Hit flash (`HitFlash`)

The cheapest effect in the kit for how much it sells an impact. It mixes the
sprite toward a colour without touching alpha, so the flash never leaks
outside the silhouette and reads the same on dark and bright sprites.

```glsl
// assets/shaders/hit_flash.gdshader
shader_type canvas_item;

uniform vec4 flash_color : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float flash_amount : hint_range(0.0, 1.0) = 0.0;

void fragment() {
    COLOR.rgb = mix(COLOR.rgb, flash_color.rgb, flash_amount * flash_color.a);
}
```

```gdscript
class_name HitFlash
extends RefCounted

const SHADER_PATH := "res://assets/shaders/hit_flash.gdshader"
const _META_MATERIAL := &"_juice_flash_material"
const _META_FOREIGN := &"_juice_flash_foreign_material"

static var _shader: Shader


static func flash(node: CanvasItem, color: Color = Color.WHITE, duration: float = 0.09) -> Tween:
    if not is_instance_valid(node) or not node.is_inside_tree():
        return null
    var material := _ensure_material(node)
    if material == null:
        return JuiceTween.flash_modulate(node, color, duration)  # keep a foreign material intact

    material.set_shader_parameter(&"flash_color", color)
    material.set_shader_parameter(&"flash_amount", 1.0)

    var tween := node.create_tween()
    tween.tween_interval(duration * 0.34)  # hold full white, then fade
    tween.tween_method(_set_amount.bind(material), 1.0, 0.0, duration * 0.66) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    return tween


static func _ensure_material(node: CanvasItem) -> ShaderMaterial:
    if node.has_meta(_META_FOREIGN):
        return null
    if node.has_meta(_META_MATERIAL):
        var existing = node.get_meta(_META_MATERIAL)
        if existing is ShaderMaterial and node.material == existing:
            return existing
        node.remove_meta(_META_MATERIAL)
    # The node already has its own material: fall back rather than overwrite.
    if node.material != null:
        node.set_meta(_META_FOREIGN, true)
        return null
    if _shader == null:
        if not ResourceLoader.exists(SHADER_PATH):
            node.set_meta(_META_FOREIGN, true)
            return null
        _shader = load(SHADER_PATH)
    var material := ShaderMaterial.new()
    material.shader = _shader
    node.material = material
    node.set_meta(_META_MATERIAL, material)
    return material
```

`clear(node)` removes the kit's material; `clear_cache()` drops the shared
shader (the hub calls it in `_exit_tree`).

## 7. Damage numbers (`DamageNumbers`)

Labels are pooled because a busy fight throws a lot of these, and allocating
a Label plus a Tween per hit stutters on exactly the frames you care about.

```gdscript
class_name DamageNumbers
extends Node2D

const _POOL_LIMIT := 64
const _GRAVITY := 420.0

var _config: JuiceConfig
var _pool: Array[Label] = []


func spawn(world_position: Vector2, text: String, crit: bool = false,
        color_override: Variant = null) -> Label:
    var label := _acquire()
    label.text = text
    label.add_theme_font_size_override(&"font_size", 32 if crit else 22)
    label.add_theme_constant_override(&"outline_size", 8 if crit else 6)
    label.add_theme_color_override(&"font_outline_color", Color(0, 0, 0, 0.85))
    var color: Color = color_override if color_override is Color \
        else (_config.damage_number_crit_color if crit else _config.damage_number_color)
    label.add_theme_color_override(&"font_color", color)

    label.reset_size()
    label.pivot_offset = label.size * 0.5
    var start := world_position - label.size * 0.5
    label.position = start
    label.scale = Vector2.ONE * (0.4 if crit else 0.6)
    label.modulate = Color(1, 1, 1, 1)
    label.visible = true
    _animate(label, start, crit)
    return label


func _animate(label: Label, start: Vector2, crit: bool) -> void:
    var lifetime: float = _config.damage_number_lifetime * (1.25 if crit else 1.0)
    var rise: float = _config.damage_number_rise * (1.3 if crit else 1.0)
    var drift := randf_range(-_config.damage_number_spread, _config.damage_number_spread)

    var tween := label.create_tween()
    tween.set_parallel(true)

    var travel := func(t: float) -> void:  # rise, then fall under gravity
        if is_instance_valid(label):
            var elapsed := t * lifetime
            label.position = start + Vector2(drift * t,
                -rise * elapsed + 0.5 * _GRAVITY * elapsed * elapsed)
    tween.tween_method(travel, 0.0, 1.0, lifetime)

    tween.tween_property(label, ^"scale", Vector2.ONE * (1.35 if crit else 1.1), lifetime * 0.16) \
        .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    tween.chain().tween_property(label, ^"scale", Vector2.ONE, lifetime * 0.2) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

    tween.set_parallel(false)
    # Held opaque for most of its life and only faded at the end. Fading from
    # the start makes the number unreadable while it still matters.
    tween.tween_interval(lifetime * 0.3)
    tween.tween_property(label, ^"modulate:a", 0.0, lifetime * 0.34)
    tween.tween_callback(_release.bind(label))


func _acquire() -> Label:
    while not _pool.is_empty():
        var pooled: Label = _pool.pop_back()
        if is_instance_valid(pooled):
            return pooled
    var label := Label.new()
    label.mouse_filter = Control.MOUSE_FILTER_IGNORE
    label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    label.z_index = 100
    add_child(label)
    return label


func _release(label: Label) -> void:
    if not is_instance_valid(label):
        return
    label.visible = false
    if _pool.size() < _POOL_LIMIT:
        if label not in _pool:
            _pool.append(label)
    else:
        label.queue_free()
```

`clear()` releases every child label (used by the hub's `_silence`).

## 8. Screen effects (`ScreenFX`)

A `CanvasLayer` at layer 100 that the hub builds; you never place it in a
scene. Two kinds of value live here. The look (curvature, scanlines, grain)
you set once and leave; the pulses (aberration, vignette, warp) are tweened
per hit and add on top of the look.

```gdscript
class_name ScreenFX
extends CanvasLayer

enum Look { OFF, SUBTLE, ARCADE, HANDHELD, BROKEN }
signal look_changed(look: Look)

var _flash: ColorRect      # full-rect, mouse ignore; screen flash and fades
var _quad: ColorRect       # full-rect quad carrying the CRT ShaderMaterial
var _material: ShaderMaterial
var _look_tween: Tween

# Look values (setters call _push): crt_curvature, crt_scanlines, crt_mask,
# crt_grain, crt_flicker, crt_bloom, crt_brightness (1.0), crt_saturation (1.0),
# crt_vignette. Pulse values: pulse_aberration, pulse_vignette, pulse_warp.


func _process(_delta: float) -> void:
    if _material != null and _quad.visible:
        # Fed from script instead of shader TIME so grain keeps moving during
        # a hitstop. A frozen screen with frozen grain looks like a crash.
        _material.set_shader_parameter(&"clock", Time.get_ticks_msec() / 1000.0)


func set_look(look: Look, duration: float = 0.45) -> void:
    current_look = look
    var values := _look_values(look)  # preset table, see tuning-numbers.md
    if _look_tween != null and _look_tween.is_valid():
        _look_tween.kill()
    if duration <= 0.0:
        for key in values:
            set(key, values[key])
        look_changed.emit(look)
        return
    _look_tween = create_tween().set_parallel(true)
    for key in values:
        _look_tween.tween_property(self, NodePath(key), values[key], duration) \
            .set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
    _look_tween.chain().tween_callback(func() -> void: look_changed.emit(look))


func flash(color: Color = Color(1, 1, 1, 0.55), duration: float = 0.12) -> Tween:
    _flash.color = color
    var tween := create_tween()
    tween.tween_property(_flash, ^"color:a", 0.0, duration) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    return tween


func chromatic(amount: float = 0.006, duration: float = 0.22) -> Tween:
    pulse_aberration = amount
    var tween := create_tween()
    tween.tween_property(self, ^"pulse_aberration", 0.0, duration) \
        .set_trans(Tween.TRANS_QUINT).set_ease(Tween.EASE_OUT)
    return tween
# vignette_pulse(0.5, 0.4 s, quad out) and warp(0.5, 0.35 s, quint out) follow the same shape.


func glitch(strength: float = 1.0, duration: float = 0.3) -> void:
    warp(0.5 * strength, duration)
    chromatic(0.012 * strength, duration)
    flash(Color(0.7, 0.9, 1.0, 0.16 * strength), duration * 0.4)


func fade_to(color: Color = Color.BLACK, duration: float = 0.4) -> Tween:
    _flash.color = Color(color.r, color.g, color.b, _flash.color.a)
    var tween := create_tween()
    tween.tween_property(_flash, ^"color:a", color.a, duration)
    return tween
# fade_from(color, duration) sets the colour and tweens alpha to 0.


func reset() -> void:
    _flash.color = Color(1, 1, 1, 0)
    pulse_aberration = 0.0
    pulse_vignette = 0.0
    pulse_warp = 0.0


func _push() -> void:
    if _material == null or _quad == null:
        return
    _material.set_shader_parameter(&"curvature", crt_curvature)
    _material.set_shader_parameter(&"scanline_strength", crt_scanlines)
    _material.set_shader_parameter(&"mask_strength", crt_mask)
    _material.set_shader_parameter(&"grain", crt_grain)
    _material.set_shader_parameter(&"flicker", crt_flicker)
    _material.set_shader_parameter(&"bloom", crt_bloom)
    _material.set_shader_parameter(&"brightness", crt_brightness)
    _material.set_shader_parameter(&"saturation", crt_saturation)
    _material.set_shader_parameter(&"aberration", pulse_aberration)
    _material.set_shader_parameter(&"vignette", clampf(crt_vignette + pulse_vignette, 0.0, 1.0))
    _material.set_shader_parameter(&"warp", pulse_warp)
    # Hide the quad entirely when nothing is on. It is a full-screen pass
    # that reads the screen texture, not something to leave running for free.
    _quad.visible = (
        crt_curvature > 0.001 or crt_scanlines > 0.001 or crt_mask > 0.001
        or crt_grain > 0.001 or crt_flicker > 0.001 or crt_bloom > 0.001
        or crt_vignette > 0.001 or pulse_aberration > 0.0001
        or pulse_vignette > 0.001 or pulse_warp > 0.001
        or absf(crt_brightness - 1.0) > 0.001 or absf(crt_saturation - 1.0) > 0.001)
```

The CRT shader (`crt.gdshader`, `canvas_item`) does everything in one pass
because every extra full-screen pass re-reads the whole screen texture.
Uniforms: `screen_texture` (hint_screen_texture), `noise_texture`,
`curvature`, `scanline_strength`, `scanline_count` (540), `mask_strength`,
`grain`, `flicker`, `bloom`, `brightness`, `saturation`, `border_color`,
`aberration`, `vignette`, `vignette_color`, `warp`, `clock`. Order inside
`fragment()`:

1. Curve UV (`uv * 2 - 1`, push by `abs(uv.yx) / (6, 4)` squared times
   curvature, back to 0..1).
2. Warp: `uv.x += sin(uv.y * 80 + clock * 14) * sin(uv.y * 13 - clock * 5) * warp * 0.02`.
3. Outside 0..1 after curving: output `border_color`.
4. Chromatic aberration: sample R at `uv - offset * aberration`, G at `uv`,
   B at `uv + offset * aberration` where `offset = uv - 0.5`.
5. Bloom: average of four diagonal taps at 2 texels, `max(sum - 0.55, 0) * bloom`.
6. Scanlines: `color *= 1 - strength * (0.5 + 0.5 * sin(uv.y * count * PI))`.
7. Phosphor mask: per-column RGB tint (1.25 on the matching channel, 0.86
   elsewhere) mixed in by `mask_strength`.
8. Grain: noise texture sampled at `uv * 3 + fract(clock * (1.7, 2.3))`,
   centred and added at `grain * 0.25`.
9. Flicker: `color *= 1 - flicker * 0.06 * (0.5 + 0.5 * sin(clock * 96))`.
10. Saturation mix toward luma, then brightness multiply.
11. Vignette: mix toward `vignette_color` by `smoothstep(0.35, 1.0, length(offset) * 1.414) * vignette`.

## 9. Sound (`JuiceSfx`, `SfxBank`, `SfxLibrary`)

Pools the players, randomises pitch slightly, and drops duplicate sounds
fired within a few milliseconds of each other. Identical samples starting on
the same frame sum to double amplitude and clip.

```gdscript
@tool
class_name SfxBank
extends Resource

@export var streams: Array[AudioStream] = []
@export_range(-40.0, 12.0, 0.5) var volume_db: float = 0.0
@export var pitch_range: Vector2 = Vector2(0.92, 1.08)

var _last_index: int = -1


func pick() -> AudioStream:
    if streams.is_empty():
        return null
    if streams.size() == 1:
        return streams[0]
    # True random repeats far more often than players expect, and a repeat is
    # exactly the thing that gives away a canned sound.
    var index := randi() % streams.size()
    if index == _last_index:
        index = (index + 1 + randi() % (streams.size() - 1)) % streams.size()
    _last_index = index
    return streams[index]


func pick_pitch() -> float:
    return randf_range(pitch_range.x, pitch_range.y)
```

`SfxLibrary` is a `Resource` with `@export var banks: Dictionary` mapping
`StringName` to `SfxBank`, plus `get_bank`, `has_bank`, `bank_names`,
`add_bank`. It is baked into `assets/sfx_library.tres`. Bundled bank names:
`click`, `confirm`, `error`, `explode`, `footstep`, `hit_heavy`, `hit_light`,
`hit_metal`, `pickup` (two to four takes each).

```gdscript
class_name JuiceSfx
extends Node

const LIBRARY_PATH := "res://assets/sfx_library.tres"

var library: SfxLibrary
var _config: JuiceConfig
var _positional: Array[AudioStreamPlayer2D] = []
var _flat: Array[AudioStreamPlayer] = []
var _last_played_ms: Dictionary = {}


func play(bank_name: StringName, position: Variant = null,
        volume_offset_db: float = 0.0, force: bool = false) -> Node:
    var bank := library.get_bank(bank_name)
    if bank == null or bank.is_empty():
        return null
    if not force and _is_duplicate(bank_name):
        return null
    var stream := bank.pick()
    _last_played_ms[bank_name] = Time.get_ticks_msec()
    var pitch := bank.pick_pitch()
    var volume := bank.volume_db + volume_offset_db

    if position is Vector2:
        var player := _acquire_positional()
        player.stream = stream
        player.pitch_scale = pitch
        player.volume_db = volume
        player.global_position = position
        player.play()
        return player
    var flat := _acquire_flat()
    flat.stream = stream
    flat.pitch_scale = pitch
    flat.volume_db = volume
    flat.play()
    return flat


func _is_duplicate(bank_name: StringName) -> bool:
    var window: float = _config.sfx_dedupe_ms  # 25 ms
    if window <= 0.0:
        return false
    var last: int = _last_played_ms.get(bank_name, -100000)
    return Time.get_ticks_msec() - last < int(window)


func _acquire_flat() -> AudioStreamPlayer:  # _acquire_positional mirrors this
    for player in _flat:
        if is_instance_valid(player) and not player.playing:
            return player
    if _flat.size() >= _config.sfx_voice_count:  # 24: steal the oldest voice
        var oldest: AudioStreamPlayer = _flat.pop_front()
        _flat.append(oldest)
        return oldest
    var created := AudioStreamPlayer.new()
    created.bus = _bus()  # config bus, or Master when that bus does not exist
    created.process_mode = Node.PROCESS_MODE_ALWAYS
    add_child(created)
    _flat.append(created)
    return created
```

`stop_all()` stops every pooled player (hub `_silence`).

## 10. UI widgets

All widgets draw in `_draw()` from polygons and text, sized from their own
content, with a skewed plate shape:

```gdscript
var shape := PackedVector2Array([
    Vector2(skew, 0.0), Vector2(box.x, 0.0),
    Vector2(box.x - skew, box.y), Vector2(0.0, box.y)])
# transform around the centre: centre + (point - centre) * scale + offset
# draw the same shape offset by shadow_offset in shadow_color first
```

### JuiceButton

Four animation channels, each on its own tween so they overlap without
fighting: select (hover), press, intro (entrance) and shake (refusal when a
disabled button is pressed).

```gdscript
enum IntroStyle { SLIDE, DROP, RISE, POP, FLIP, FADE }
signal pressed
signal hovered

var select_amount := 0.0   # 0..1, hover / focus
var press_amount := 0.0    # 0..1, press squash
var intro_amount := 1.0    # 0..1, entrance (overshoots with BACK ease)
var shake_amount := 0.0    # 1..0, refusal rattle


func set_selected(value: bool) -> void:
    if selected == value:
        return
    selected = value
    if value and is_inside_tree() and intro_amount > 0.5 and not disabled:
        Juice.play_sfx(hover_sound, null, -10.0)
    _kill(_select_tween)
    _select_tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    _select_tween.tween_property(self, ^"select_amount", 1.0 if value else 0.0, 0.22)


func press() -> void:
    if disabled:
        _refuse()
        return
    _kill(_press_tween)
    _press_tween = create_tween()
    _press_tween.tween_property(self, ^"press_amount", 1.0, 0.06)
    _press_tween.tween_property(self, ^"press_amount", 0.0, 0.22) \
        .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    Juice.play_sfx(press_sound, null, -4.0)
    if juicy_press:
        Juice.shake(0.1)
        Juice.hitstop(0.03)
    pressed.emit()


func _refuse() -> void:
    _kill(_shake_tween)
    shake_amount = 1.0
    _shake_tween = create_tween()
    _shake_tween.tween_property(self, ^"shake_amount", 0.0, 0.45) \
        .set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
    Juice.play_sfx(blocked_sound, null, -6.0)


func play_intro(delay: float = 0.0, from_left: bool = true) -> void:
    _kill(_intro_tween)
    _from_side = -1.0 if from_left else 1.0
    _travel = intro_travel  # 520 px
    intro_amount = 0.0
    _intro_tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    _intro_tween.tween_interval(delay)
    _intro_tween.tween_property(self, ^"intro_amount", 1.0, 0.45)


func play_outro(delay: float = 0.0, to_left: bool = false) -> float:
    # same, exit_travel 620 px, BACK ease-in, 0.3 s; returns delay + 0.3
    ...
```

In `_draw()`: `grow = 1 + select_amount * select_grow - press_amount *
press_squash`, `slide = select_amount * select_slide` plus, while shaking,
`sin(t * 74) * shake * 9 + sin(t * 131) * shake * 4`; the shadow offset
shrinks by `press_amount * 0.75`; fill lerps idle to selected colour by
`select_amount`; disabled draws the disabled fill with half-alpha text. The
entrance transform per style, with `away = 1 - intro_amount`:

| Style | Transform |
| --- | --- |
| SLIDE | offset.x = away * travel * side |
| DROP | offset.y = -away * vertical_travel (240) |
| RISE | offset.y = away * vertical_travel |
| POP | scale = max(intro_amount, 0) (BACK ease dips below 0; a negative scale would mirror the polygon) |
| FLIP | scale.x = max(intro_amount, 0) |
| FADE | offset.y = away * 12 |

Alpha is always `clamp(intro_amount, 0, 1)`. Mouse click and `ui_accept`
both call `press()`; hover emits `hovered`; focus enter/exit call
`set_selected`.

### JuiceMenu

A `VBoxContainer` that holds `JuiceButton`s, deals them in on a stagger, and
handles keyboard and mouse. Style is how a row enters; order is which row
goes first. They are separate settings because the same slide dealt
centre-out feels nothing like the same slide dealt top to bottom.

```gdscript
enum StaggerOrder { SEQUENTIAL, REVERSE, CENTRE_OUT, EDGES_IN, RANDOM, TOGETHER }
@export var stagger: float = 0.06


func _delay_for(at: int) -> float:
    var count := _buttons.size()
    if count <= 1 or stagger <= 0.0:
        return 0.0
    var step := 0.0
    match stagger_order:
        StaggerOrder.SEQUENTIAL:
            step = float(at)
        StaggerOrder.REVERSE:
            step = float(count - 1 - at)
        StaggerOrder.CENTRE_OUT:
            step = absf(float(at) - float(count - 1) * 0.5)
        StaggerOrder.EDGES_IN:
            var middle := float(count - 1) * 0.5
            step = middle - absf(float(at) - middle)
        StaggerOrder.RANDOM:
            # Seeded off the index so a row keeps its slot between replays.
            # A fresh randf() every time just looks broken.
            step = float(posmod(at * 7919, maxi(count, 1)))
        StaggerOrder.TOGETHER:
            step = 0.0
    return stagger * step


func play_intro(from_left: bool = true) -> void:
    visible = true
    index = 0
    _refresh_selection()
    for i in _buttons.size():
        _buttons[i].intro_style = intro_style
        _buttons[i].play_intro(_delay_for(i), from_left)


func play_outro(to_left: bool = false) -> float:
    set_process_unhandled_input(false)
    var last := 0.0
    for i in _buttons.size():
        last = maxf(last, _buttons[i].play_outro(_delay_for(i) * 0.6, to_left))
    if last > 0.0:
        await get_tree().create_timer(last).timeout
    visible = false
    return last
```

`ui_up` / `ui_down` move the index (wrapping by default), `ui_accept`
activates; hovering a button selects it; `activated(id, index)` and
`selection_changed(index)` signals drive the game.

### JuiceCounter

A number that counts up instead of snapping. Both the roll time and the
punch scale with how big the change was, so +5 and +5000 do not look the
same.

```gdscript
func set_value(new_value: float, immediate: bool = false) -> void:
    var previous := _value
    _value = new_value
    if not is_inside_tree() or immediate or is_equal_approx(previous, new_value):
        _displayed = new_value
        return
    _kill(_roll_tween)
    var magnitude := absf(new_value - previous)
    var reference := maxf(absf(previous), 1.0)
    var duration := clampf(roll_time * clampf(magnitude / reference, 0.15, 2.0),
        min_roll_time, max_roll_time)
    _roll_tween = create_tween()
    _roll_tween.tween_property(self, ^"_displayed", new_value, duration) \
        .set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
    _roll_tween.tween_callback(func() -> void: reached.emit(new_value))
    _react(new_value > previous)


func _react(is_gain: bool) -> void:
    _kill(_punch_tween)
    _scale = 1.0 + punch  # 0.22
    _tint = gain_color if is_gain else loss_color
    _punch_tween = create_tween().set_parallel(true)
    _punch_tween.tween_property(self, ^"_scale", 1.0, 0.4) \
        .set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
    # Colour comes back faster than the scale so the flash punctuates instead
    # of leaving the number permanently tinted.
    _punch_tween.tween_property(self, ^"_tint", color, 0.3) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
```

The exported `value` property has a setter that calls `set_value()` on a
backing `_value`; `set_value()` must never assign to `value` or it recurses.
Formatting: prefix, suffix, whole numbers with digit grouping, or `decimals`.

### JuiceBar

A progress bar with a ghost fill that lags behind a loss. That trailing band
is the whole point: it shows how much you just took while you can still react
to it.

```gdscript
func set_value(new_value: float, immediate: bool = false) -> void:
    var previous := _value
    _value = clampf(new_value, 0.0, 1.0)
    if not is_inside_tree() or immediate:
        _fill = _value
        _ghost = _value
        return
    if is_equal_approx(previous, _value):
        return
    _kill(_fill_tween)
    _kill(_ghost_tween)
    _fill_tween = create_tween()
    _fill_tween.tween_property(self, ^"_fill", _value, fill_time) \
        .set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
    # On a loss the ghost holds where it was, waits, then drains. On a gain it
    # leads so the new stretch flashes bright as it fills.
    if _value < previous:
        _ghost_tween = create_tween()
        _ghost_tween.tween_interval(ghost_delay)
        _ghost_tween.tween_property(self, ^"_ghost", _value, ghost_time) \
            .set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_IN_OUT)
        if shake_on_loss:
            _rattle(clampf((previous - _value) * 3.0, 0.2, 1.0))
    else:
        _ghost = _value
        _pulse()
    if _value <= 0.001:
        emptied.emit()
    elif _value >= 0.999:
        filled.emit()
```

Draw order: track, ghost slice (only when `_ghost > _fill`), fill slice
(lerped toward `gain_color` by `_flash`), optional segment notches, border
polyline. The whole bar is offset by `(sin(t * 96), cos(t * 77)) * _shake *
5` while rattling.

### JuiceToast and ToastLayer

One notification plate pops in, rattles, holds, slides out, and frees
itself. It sizes itself from its own text in `_draw` because the plate is
skewed and a container would lay out the bounding box, not the shape.

```gdscript
func play() -> void:  # JuiceToast
    _kill(_tween)
    amount = 0.0
    shake = 1.0
    _tween = create_tween()
    _tween.tween_property(self, ^"amount", 1.0, 0.24) \
        .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    _tween.parallel().tween_property(self, ^"shake", 0.0, 0.5)
    _tween.tween_interval(hold)  # 1.4 s
    _tween.tween_property(self, ^"amount", 0.0, 0.26) \
        .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
    _tween.tween_callback(func() -> void: finished.emit())
```

`ToastLayer` (a `CanvasLayer` at layer 80, `PROCESS_MODE_ALWAYS`) stacks them
in the top-right corner. When one in the middle expires the others slide into
the gap instead of snapping, which is most of the difference between this and
a homemade notification stack.

```gdscript
const SLOT_HEIGHT := 56.0
const MARGIN := Vector2(26.0, 26.0)
const MAX_VISIBLE := 5


func push(message: String, color: Color = JuicePalette.PINK,
        hold: float = 1.4, icon: Texture2D = null) -> JuiceToast:
    if _toasts.size() >= MAX_VISIBLE:
        _retire(_toasts[0])
    var toast := JuiceToast.new()
    toast.message = message
    toast.plate = color
    toast.hold = hold
    toast.icon = icon
    toast.size = Vector2(toast.measured_width(), SLOT_HEIGHT)
    toast.position = _slot_position(toast, _toasts.size())
    add_child(toast)
    _toasts.append(toast)
    toast.finished.connect(_retire.bind(toast))
    toast.play()
    _reflow()
    return toast


func _slot_position(toast: JuiceToast, index: int) -> Vector2:
    var screen := get_viewport().get_visible_rect().size
    return Vector2(screen.x - toast.size.x - MARGIN.x, MARGIN.y + index * SLOT_HEIGHT)


func _reflow() -> void:
    for i in _toasts.size():
        var toast := _toasts[i]
        var target := _slot_position(toast, i)
        toast.position.x = target.x
        if absf(toast.position.y - target.y) < 0.5:
            continue
        var tween := toast.create_tween()
        tween.tween_property(toast, ^"position:y", target.y, 0.28) \
            .set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
```

Positions are plain top-left offsets: anchored Controls read position
relative to the anchor, which breaks once a toast is sized from its own
text.

### JuiceTooltip

One instance serves a whole screen: `show_for(text, anchor_rect)` centres
the tip above the hovered control, rises 14 px while fading in (0.22 s back
ease-out), and bobs by `sin(t * 2.6) * float_height * 0.5` while open;
`hide_tip()` fades in 0.14 s (quad ease-in). The plate is nudged back on
screen when the anchor sits near an edge. Parent it last so it draws over
everything and give it `z_index = 200`.

### JuiceBackdrop

A drawn sky gradient, twinkling stars, sun with a glow texture, parallax
ridges built from three seeded sine waves per layer, and passing poles. It
cycles through five palettes (DUSK, NIGHT, EMBER, DAWN, NEON) every 22 s:
hold a palette for the first 55 % of the period, then cross-fade every
colour with `smoothstep` over the remaining 45 %, so each palette gets time
to be looked at instead of being permanently mid-transition. Stars fade out
as the sky brightens (`visibility = 1 - luminance * 5`).

### JuicePalette

Colour constants (INK, CREAM, GOLD, PINK, CYAN, MINT, RED, NIGHT_HIGH,
NIGHT_MID, NIGHT_LOW), a cached `font()` (Bungee when present, otherwise
`ThemeDB.fallback_font`), and `accent(index)` cycling GOLD, CYAN, PINK, MINT,
RED. Change these and the whole kit changes with them.

## 11. Composition examples (from the demo)

| Action | Calls |
| --- | --- |
| Strike (normal) | `damage_number(at, damage)`, `impact(at, 0.45)`, counter and bar updates |
| Strike (crit) | `damage_number(at, damage, true)`, `impact(at, 0.75)`, `toast("CRITICAL", GOLD, 1.0)` |
| Health below 30 % | `vignette(0.35, 0.5)` |
| Down | `toast("DOWN", RED, 2.0)`, `slowmo(0.25, 0.4)`, `vignette(0.6, 0.9)` |
| Collect | `play_sfx("pickup")`, `shake(0.2)`, `flash(mint at alpha 0.14, 0.18)`, `toast("+2,500", MINT, 1.2)` |
| Glitch | `glitch(1.0, 0.4)`, `play_sfx("error")`, `toast("SIGNAL LOST", RED, 1.6)`, `set_look(BROKEN, 0.08)`, wait 0.55 s, `set_look(previous, 0.5)` |
| Overload | `slowmo(0.2, 0.5)`, `hitstop(0.12)`, `shake(0.8)`, `zoom_punch(0.08, 0.5)`, `flash(warm white 0.35, 0.25)`, `chromatic(0.014, 0.5)`, `vignette(0.5, 0.7)`, `play_sfx("explode")`, `toast("OVERLOAD", GOLD, 2.0)` |
| Link hover | `punch(row, 0.12, 0.35)`, `play_sfx("click", null, -14)`, tooltip `show_for` |
| Link click | `punch(row, 0.3, 0.4)`, `play_sfx("confirm", null, -4)`, `toast(...)` |
| Title | `JuiceTween.pop_in(title, 0.6)` then a looping 4 px sine breathe over 2.2 s each way |
| Toggle juice (J key) | `Juice.enabled = not Juice.enabled`; status label reads "same logic, no feel" when off |

Note how the routine action (a normal strike) uses `impact` at 0.45, which
stays below the flash and aberration thresholds, and the rare ones open the
screen-wide channels. That contrast is what makes the big hits read.
