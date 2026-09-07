# Firebase Stack For Games

## Common Product Mapping

- Auth: anonymous accounts, platform auth, email/password, account linking.
- Firestore: player profiles, saves, inventory snapshots, economy state,
  guilds, async social features, admin-managed config.
- Realtime Database: low-latency presence or simple realtime state when
  Firestore is not a fit.
- Cloud Functions: trusted mutations, validation, scheduled jobs, leaderboard
  updates, purchase verification, moderation hooks.
- Storage: user-generated images, replays, save backups, downloadable content
  metadata. Use rules and size/type checks.
- Remote Config: feature flags, tuning values, rollout controls.
- Analytics/Crashlytics: funnels, errors, retention, economy balancing signals.
- App Check: reduce abuse from non-genuine clients; do not treat it as a full
  anti-cheat solution.

## Client vs Trusted Boundary

Safe on client:

- Read own profile/save data allowed by rules.
- Request auth.
- Submit intent-like writes that rules can validate.
- Fetch Remote Config.
- Log analytics events.

Requires trusted code:

- Grant currency/items/rewards.
- Verify purchases.
- Write global leaderboard ranks.
- Moderate public content.
- Execute matchmaking assignments.
- Anything that trusts client-reported score, damage, time, or inventory.

## Firestore Modeling

Prefer explicit ownership paths:

```text
users/{uid}
users/{uid}/saves/{slotId}
users/{uid}/inventory/{itemInstanceId}
leaderboards/{seasonId}/entries/{uid}
publicProfiles/{uid}
```

Avoid large unbounded documents. Use subcollections for growing data. Add
indexes intentionally and keep query shapes aligned with security rules.

## Local Development

Use Emulator Suite for:

- Auth test users
- Firestore rules tests
- Function integration tests
- Storage rules tests

Never test destructive writes against production by default.
