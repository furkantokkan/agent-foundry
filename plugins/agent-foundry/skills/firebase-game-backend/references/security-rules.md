# Firebase Security Rules

## Baseline

Start closed:

```firestore
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

Open only the paths and operations the feature needs.

## Ownership Pattern

```firestore
match /users/{userId} {
  allow read, update: if request.auth != null && request.auth.uid == userId;
  allow create: if request.auth != null && request.auth.uid == userId;

  match /saves/{slotId} {
    allow read, write: if request.auth != null && request.auth.uid == userId;
  }
}
```

## Validation Pattern

Validate schema, type, and bounds:

```firestore
allow write: if request.auth.uid == userId
  && request.resource.data.keys().hasOnly(['displayName', 'updatedAt'])
  && request.resource.data.displayName is string
  && request.resource.data.displayName.size() >= 3
  && request.resource.data.displayName.size() <= 24;
```

## Important Rule

Security rules are not filters. If a rule only allows reading documents where
`ownerUid == request.auth.uid`, the query must include that constraint.

## High-Risk Areas

- Public collection reads with private fields mixed in the same document.
- Client-writable currency, inventory, XP, or leaderboard scores.
- Rules that allow `update` without checking changed keys.
- Admin SDK assumptions: Admin/server SDKs bypass Firebase Security Rules.
- Queries added in code without matching rules and indexes.

## Testing

Use rules tests for every path that stores player-owned, economy, leaderboard,
UGC, or moderation-sensitive data.
