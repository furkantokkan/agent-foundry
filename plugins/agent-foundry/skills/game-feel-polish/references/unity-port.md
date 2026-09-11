# Unity port guide

The kit's structure maps one-to-one onto Unity. Keep the same ownership: one
hub, one config asset, one switch, and presentation state separate from
gameplay state. Follow the repository's architecture rules first: an
established ServiceLocator takes precedence for registration; otherwise use
the project's preferred composition option. Do not introduce a second
tween, audio, or DI stack for feel. If the project already ships the More
Mountains Feel package, use `unity-feel-interactions` and route the hub's
calls through `MMF_Player` sequences instead of hand-rolled tweens.

## Mapping

| Kit system | Unity equivalent | Notes |
| --- | --- | --- |
| `Juice` autoload | One `JuiceHub` MonoBehaviour (or plain class) registered with the existing ServiceLocator | `Enabled`, `Intensity`, `Impact()`, `Silence()`; survives scene loads if feel must continue across them |
| `JuiceConfig` resource | `JuiceConfig : ScriptableObject` | Same groups and defaults from `tuning-numbers.md`; designers edit the asset |
| `ShakeCamera2D` | `TraumaShaker` on a child of the camera rig, or a Cinemachine Impulse Listener | Never fight the follow camera; shake a child transform or use the impulse system |
| `JuiceTime` | `FeelTime` owning `Time.timeScale` | Measure with `Time.unscaledTime`; restore `fixedDeltaTime` proportionally when slowing |
| `JuiceTween` | Project tween library (DOTween, PrimeTween, LitMotion) or a small coroutine helper | Unscaled time for UI punches so they keep moving during hitstop |
| `HitFlash` + shader | `MaterialPropertyBlock` with `_FlashColor` / `_FlashAmount` on a shared shader | Fall back to tinting `SpriteRenderer.color` when the renderer owns a material without the property |
| `DamageNumbers` | Pool of `TMP_Text` under a world-space or screen-space canvas | Same arc, pop, hold, fade timings |
| `ScreenFX` + CRT shader | URP full-screen pass (Fullscreen Shader Graph or a Renderer Feature) | Disable the feature when every uniform is zero; feed `_Clock` from unscaled time |
| `JuiceSfx`, `SfxBank`, `SfxLibrary` | `SfxBank : ScriptableObject`, `SfxLibrary : ScriptableObject`, pooled `AudioSource`s | Per-source pitch needs pooled sources; `PlayOneShot` shares the source pitch |
| `ToastLayer` | UGUI or UI Toolkit stack with tweened reflow | Cap 5, retire oldest, tween `anchoredPosition.y` |
| `JuiceCounter`, `JuiceBar` | Presentation components that tween a displayed value and a ghost fill | `Image.fillAmount` for fill and ghost; never tween the model |
| `JuiceMenu` | Stagger controller over `CanvasGroup` alpha plus `RectTransform` offset per intro style | Keep order separate from style; seed random slots |
| Joypad rumble | Input System `Gamepad.SetMotorSpeeds(weak, strong)` with an unscaled stop timer | Reset motors in `Silence()` and on disable |

## Hub

```csharp
public sealed class JuiceHub : MonoBehaviour
{
    [SerializeField] private JuiceConfig config;
    [SerializeField] private FeelTime feelTime;
    [SerializeField] private TraumaShaker shaker;
    [SerializeField] private ScreenFeel screen;
    [SerializeField] private DamageNumberPool numbers;
    [SerializeField] private SfxPlayer sfx;
    [SerializeField] private ToastStack toasts;

    private bool enabledFlag = true;
    private float intensity = 1f;

    public bool Enabled
    {
        get => enabledFlag;
        set
        {
            if (enabledFlag == value) return;
            enabledFlag = value;
            if (!enabledFlag) Silence();
        }
    }

    public float Intensity
    {
        get => intensity;
        set => intensity = Mathf.Clamp(value, 0f, 2f);
    }

    // Same ratios as the kit. Gameplay calls this with a tier strength.
    public void Impact(Vector3 worldPosition, float strength = 0.5f)
    {
        if (!Enabled) return;
        strength = Mathf.Clamp01(strength);
        ShakeAt(worldPosition, Mathf.Lerp(0.18f, 0.75f, strength));
        feelTime.Hitstop(Mathf.Lerp(0.035f, 0.13f, strength));
        if (strength > 0.25f) screen.Flash(new Color(1f, 1f, 1f, Mathf.Lerp(0f, 0.4f, strength)), 0.1f);
        if (strength > 0.45f)
        {
            screen.Chromatic(Mathf.Lerp(0f, 0.009f, strength) * intensity);
            shaker.ZoomPunch(Mathf.Lerp(0f, 0.05f, strength) * intensity);
        }
        Rumble(Mathf.Lerp(0.15f, 0.7f, strength), Mathf.Lerp(0.2f, 0.9f, strength), Mathf.Lerp(0.1f, 0.3f, strength));
        sfx.Play(strength > 0.5f ? "hit_heavy" : "hit_light", worldPosition);
    }

    public void ShakeAt(Vector3 worldPosition, float amount, float radius = 6f)
    {
        if (!Enabled || shaker == null) return;
        float falloff = 1f - Mathf.Clamp01(Vector3.Distance(shaker.transform.position, worldPosition) / Mathf.Max(radius, 0.01f));
        if (falloff <= 0f) return;
        shaker.AddTrauma(amount * falloff * falloff * intensity);
    }

    public void Silence()
    {
        feelTime.ResetScale();
        shaker.ResetPose();
        screen.ResetPulses();
        numbers.Clear();
        sfx.StopAll();
        toasts.Clear();
        StopRumble();
    }
}
```

Radius is in world units; 6 units is a stand-in for the kit's 600 px at
100 px per unit. Tune it to the camera size.

## Camera

```csharp
public sealed class TraumaShaker : MonoBehaviour
{
    [SerializeField] private Vector2 maxOffset = new Vector2(0.26f, 0.18f); // world units for an orthographic camera
    [SerializeField] private float maxRollDegrees = 3.4f;                   // 0.06 rad
    [SerializeField] private float decay = 2.4f;
    [SerializeField] private float frequency = 42f;
    [SerializeField] private float power = 2f;

    private float trauma;
    private float noiseTime;
    private float zoomOffset;
    private Vector3 basePosition;
    private Quaternion baseRotation;
    private Camera cam;
    private float baseSize;

    public void AddTrauma(float amount) => trauma = Mathf.Clamp01(trauma + amount);

    private void Awake()
    {
        cam = GetComponentInParent<Camera>();
        baseSize = cam != null && cam.orthographic ? cam.orthographicSize : 0f;
        Rebase();
    }

    public void Rebase()
    {
        basePosition = transform.localPosition;
        baseRotation = transform.localRotation;
    }

    public void ResetPose()
    {
        trauma = 0f;
        zoomOffset = 0f;
        transform.localPosition = basePosition;
        transform.localRotation = baseRotation;
    }

    private void LateUpdate()
    {
        float dt = Mathf.Min(Time.unscaledDeltaTime, 0.1f); // keeps moving during hitstop, never flings after a stall
        if (trauma <= 0f && Mathf.Approximately(zoomOffset, 0f))
        {
            transform.localPosition = basePosition;
            transform.localRotation = baseRotation;
            return;
        }
        trauma = Mathf.Max(trauma - decay * dt, 0f);
        noiseTime += dt * frequency;
        float amount = Mathf.Pow(trauma, power);
        float x = (Mathf.PerlinNoise(noiseTime, 0f) * 2f - 1f) * maxOffset.x * amount;
        float y = (Mathf.PerlinNoise(0f, noiseTime) * 2f - 1f) * maxOffset.y * amount;
        float roll = (Mathf.PerlinNoise(noiseTime, 100f) * 2f - 1f) * maxRollDegrees * amount;
        transform.localPosition = basePosition + new Vector3(x, y, 0f);
        transform.localRotation = baseRotation * Quaternion.Euler(0f, 0f, roll);
        if (cam != null && cam.orthographic) cam.orthographicSize = baseSize / (1f + zoomOffset);
    }
}
```

`ZoomPunch(amount, duration)` tweens `zoomOffset` out over 25 % of the
duration and back over 75 % with an elastic curve, using unscaled time. The
recoil kick is a damped spring (`accel = -120 * kick - 14 * velocity`)
added to the position. With Cinemachine, replace the shaker with an Impulse
Source per hit tier and keep the same trauma-to-strength mapping in the hub.

## Time

```csharp
public sealed class FeelTime : MonoBehaviour
{
    private float baseFixedDelta;
    private float hitstopEnd;
    private float hitstopScale;
    private bool hitstopActive;
    private bool slowmoActive;
    private float slowmoStart, slowmoScale = 1f, blendIn, hold, blendOut;

    private void Awake() => baseFixedDelta = Time.fixedDeltaTime;

    public void Hitstop(float duration = 0.08f, float scale = 0f)
    {
        if (duration <= 0f) return;
        float end = Time.unscaledTime + duration;
        if (end <= hitstopEnd) return;          // a shorter hitstop never cuts a longer one
        hitstopEnd = end;
        hitstopScale = scale;
        hitstopActive = true;
        Apply();
    }

    public void Slowmo(float scale = 0.35f, float duration = 0.6f, float blendInSeconds = 0.05f, float blendOutSeconds = 0.25f)
    {
        slowmoScale = Mathf.Max(scale, 0.01f);
        slowmoStart = Time.unscaledTime;
        blendIn = blendInSeconds; hold = duration; blendOut = blendOutSeconds;
        slowmoActive = true;
        Apply();
    }

    public void ResetScale()
    {
        hitstopActive = false;
        slowmoActive = false;
        Apply();
    }

    private void Update()
    {
        if (!hitstopActive && !slowmoActive) return;
        if (hitstopActive && Time.unscaledTime >= hitstopEnd) hitstopActive = false;
        if (slowmoActive && Time.unscaledTime - slowmoStart >= blendIn + hold + blendOut) slowmoActive = false;
        Apply();
    }

    private void OnDisable() => ResetScale();

    private void Apply()
    {
        float target = slowmoActive ? CurrentSlowmoScale() : 1f;
        if (hitstopActive) target = hitstopScale;   // hitstop always beats slowmo
        if (Mathf.Abs(Time.timeScale - target) < 0.001f) return;
        Time.timeScale = target;
        Time.fixedDeltaTime = baseFixedDelta * Mathf.Max(target, 0.01f); // keep physics steps proportional
    }

    private float CurrentSlowmoScale()
    {
        float elapsed = Time.unscaledTime - slowmoStart;
        if (elapsed < blendIn) return Mathf.Lerp(1f, slowmoScale, Mathf.SmoothStep(0f, 1f, elapsed / Mathf.Max(blendIn, 0.001f)));
        if (elapsed < blendIn + hold) return slowmoScale;
        if (blendOut <= 0f) return 1f;
        return Mathf.Lerp(slowmoScale, 1f, Mathf.SmoothStep(0f, 1f, Mathf.Clamp01((elapsed - blendIn - hold) / blendOut)));
    }
}
```

Restore the scale in `OnDisable`, on scene unload, and on application pause
if the project pauses through time scale. If another system already owns
`Time.timeScale` (a pause menu), route hitstop through that owner instead of
writing the property from two places.

## Tweens

Use the project's tween library when one exists; the important parts are the
shape and the rest-state cache. A minimal coroutine version:

```csharp
public static class FeelTween
{
    private static readonly Dictionary<Transform, Vector3> RestScale = new Dictionary<Transform, Vector3>();
    private static readonly Dictionary<Transform, Coroutine> Running = new Dictionary<Transform, Coroutine>();

    public static void PunchScale(MonoBehaviour host, Transform target, float amount = 0.25f, float duration = 0.32f)
    {
        if (target == null) return;
        if (!RestScale.TryGetValue(target, out Vector3 rest)) RestScale[target] = rest = target.localScale;
        if (Running.TryGetValue(target, out Coroutine previous) && previous != null) host.StopCoroutine(previous);
        Running[target] = host.StartCoroutine(Punch(target, rest, amount, duration));
    }

    private static IEnumerator Punch(Transform target, Vector3 rest, float amount, float duration)
    {
        float outTime = duration * 0.22f, backTime = duration * 0.78f, t = 0f;
        Vector3 peak = rest * (1f + amount);
        while (t < outTime)
        {
            t += Time.unscaledDeltaTime;
            target.localScale = Vector3.LerpUnclamped(rest, peak, EaseOutQuad(Mathf.Clamp01(t / outTime)));
            yield return null;
        }
        t = 0f;
        while (t < backTime)
        {
            t += Time.unscaledDeltaTime;
            target.localScale = Vector3.LerpUnclamped(peak, rest, EaseOutElastic(Mathf.Clamp01(t / backTime)));
            yield return null;
        }
        target.localScale = rest;
    }

    public static void Restore(Transform target)
    {
        if (target != null && RestScale.TryGetValue(target, out Vector3 rest)) target.localScale = rest;
    }

    private static float EaseOutQuad(float x) => 1f - (1f - x) * (1f - x);

    private static float EaseOutElastic(float x)
    {
        const float c4 = (2f * Mathf.PI) / 3f;
        if (x <= 0f) return 0f;
        if (x >= 1f) return 1f;
        return Mathf.Pow(2f, -10f * x) * Mathf.Sin((x * 10f - 0.75f) * c4) + 1f;
    }
}
```

Clear cache entries when the target is destroyed (or key the cache by
instance id and prune on `OnDestroy`). With DOTween, `DOPunchScale` is
close but symmetric; build the two-phase shape with a `Sequence` of
`DOScale(peak, 0.22 * d).SetEase(Ease.OutQuad)` then `DOScale(rest, 0.78 *
d).SetEase(Ease.OutElastic)` and `SetUpdate(true)` for unscaled time.

## Hit flash

Shader (URP Sprite Unlit or a Shader Graph): `color.rgb = lerp(color.rgb,
_FlashColor.rgb, _FlashAmount * _FlashColor.a)`; leave alpha untouched.

```csharp
public sealed class HitFlash : MonoBehaviour
{
    private static readonly int FlashAmount = Shader.PropertyToID("_FlashAmount");
    private static readonly int FlashColor = Shader.PropertyToID("_FlashColor");
    private Renderer target;
    private MaterialPropertyBlock block;
    private Coroutine running;

    public void Flash(Color color, float duration = 0.09f)
    {
        if (target == null) target = GetComponent<Renderer>();
        if (!target.sharedMaterial.HasProperty(FlashAmount)) { FallbackTint(color, duration); return; }
        block ??= new MaterialPropertyBlock();
        if (running != null) StopCoroutine(running);
        running = StartCoroutine(Run(color, duration));
    }

    private IEnumerator Run(Color color, float duration)
    {
        Set(color, 1f);
        yield return new WaitForSecondsRealtime(duration * 0.34f);   // hold, then fade
        float t = 0f, fade = duration * 0.66f;
        while (t < fade)
        {
            t += Time.unscaledDeltaTime;
            float x = Mathf.Clamp01(t / fade);
            Set(color, 1f - (1f - (1f - x) * (1f - x)));
            yield return null;
        }
        Set(color, 0f);
    }

    private void Set(Color color, float amount)
    {
        target.GetPropertyBlock(block);
        block.SetColor(FlashColor, color);
        block.SetFloat(FlashAmount, amount);
        target.SetPropertyBlock(block);
    }
}
```

`FallbackTint` lerps `SpriteRenderer.color` toward the flash colour and
back, the same as the kit's modulate fallback. Never instantiate a material
per hit.

## Damage numbers

Pool `TMP_Text` instances (cap 64) under one canvas. Convert the world
position once at spawn, then animate in canvas space: horizontal drift
random in plus or minus 34 units, vertical `-rise * t + 0.5 * 420 * t * t`,
scale from 0.6 (crit 0.4) to 1.1 (crit 1.35) over 16 % of the lifetime with
an overshoot curve then to 1.0 over 20 %, hold opaque 30 %, fade 34 %,
return to pool. Use unscaled time when the numbers must keep moving during
hitstop.

## Sound

```csharp
[CreateAssetMenu(menuName = "Feel/Sfx Bank")]
public sealed class SfxBank : ScriptableObject
{
    public AudioClip[] takes;
    [Range(-40f, 12f)] public float volumeDb;
    public Vector2 pitchRange = new Vector2(0.92f, 1.08f);
    [System.NonSerialized] private int lastIndex = -1;

    public AudioClip Pick()
    {
        if (takes == null || takes.Length == 0) return null;
        if (takes.Length == 1) return takes[0];
        int index = Random.Range(0, takes.Length);
        if (index == lastIndex) index = (index + 1 + Random.Range(0, takes.Length - 1)) % takes.Length;
        lastIndex = index;
        return takes[index];
    }

    public float PickPitch() => Random.Range(pitchRange.x, pitchRange.y);
}
```

`SfxPlayer` holds a pool of 24 `AudioSource`s (spatialBlend 1 for
positional, 0 for flat), a per-bank last-played time using
`Time.unscaledTime`, a 25 ms dedupe window, oldest-voice stealing when the
pool is full, and a mixer-group fallback when the configured group is
missing. Convert dB with `Mathf.Pow(10f, db / 20f)` for `AudioSource.volume`.
Check the licence of every clip before wiring it; the kit's Kenney sounds
are CC0 but are not part of this skill.

## Toasts, counters, bars, menus

- Toast stack: cap 5, retire the oldest, tween each remaining toast's
  `anchoredPosition.y` to its slot over 0.28 s with an ease-out cubic. Size
  the plate from the text (`TMP_Text.preferredWidth` plus padding).
- Counter: keep `displayedValue` separate from the model; roll duration is
  `clamp(0.55 * clamp(|delta| / max(|previous|, 1), 0.15, 2), 0.12, 1.1)`;
  punch scale 1.22 back over 0.4 s elastic; tint gain or loss colour back
  over 0.3 s (faster than the scale).
- Bar: fill `Image.fillAmount` over 0.16 s; ghost `Image` holds 0.25 s then
  drains over 0.45 s on a loss, leads and flashes on a gain; rattle the
  container by `(sin(t * 96), cos(t * 77)) * strength * 5` px.
- Menu: compute the delay per row with the kit's stagger orders
  (`SEQUENTIAL`, `REVERSE`, `CENTRE_OUT`, `EDGES_IN`, seeded `RANDOM`,
  `TOGETHER`) at 0.06 s per step; apply the intro style as a `CanvasGroup`
  alpha plus an offset or scale on the `RectTransform`; clamp scale at zero
  when the overshoot curve dips negative.

## Screen look

Implement the CRT pass as one URP full-screen material with the same
uniforms and order as the kit's shader (curvature, warp, aberration, bloom,
scanlines, mask, grain, flicker, saturation, brightness, vignette). Drive
it from a `ScreenFeel` component that tweens look values (0.45 s cubic
ease-out cross-fade) and pulses (chromatic 0.22 s, vignette 0.4 s, warp
0.35 s), and disables the renderer feature when every value is zero. Feed
`_Clock` from `Time.unscaledTime` so grain moves during hitstop. Keep a
full-screen `Image` for flashes and fades.

## Accessibility and verification

- Read the project's reduced-motion or screen-shake setting from its
  settings service and skip shake, zoom, flash, time-scale changes, and
  rumble when it is on; keep a static cue.
- Keep amplitudes, durations, and curves in the config asset, not in
  gameplay scripts.
- Measure allocations after warm-up in a busy scene (`unity-optimization`);
  pooled sources and labels avoid per-hit allocation, but coroutine-based
  tweens allocate on start, so prefer the project's tween library in
  high-frequency paths.
- Run the checklist in `polish-checklist.md` in a built player as well as
  in the Editor.
