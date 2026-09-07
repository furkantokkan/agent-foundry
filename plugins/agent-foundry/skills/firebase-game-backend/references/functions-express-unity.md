# Functions Gen2, Express, and Unity API Client

Use this reference when adding or reviewing Firebase Functions that are called
from Unity.

## Default Architecture

- Use JavaScript Cloud Functions Gen2 with an Express app for HTTP APIs.
- Prefer one exported HTTP entrypoint for Unity client gameplay APIs, for
  example `exports.api = onRequest(app)` or the project's wrapper around
  `firebase-functions/v2/https.onRequest`.
- Keep route registration centralized in `functions/index.js` or a nearby router.
  Feature modules should export handlers; they should not create independent
  HTTP functions unless there is a clear deployment/runtime reason.
- Use `express.json()` for JSON request bodies. If the project supports binary
  payloads, add a deliberate raw parser such as MessagePack handling and keep
  JSON as the default client contract.
- Return a consistent envelope: success uses `{ ok: true, code: "ok", ... }`;
  failure uses `{ ok: false, code: "stable_error_code", ... }`.
- Use shared helpers such as `sendResponse`, `readBody`, `requireAuth`,
  `verifyAppCheck`, and `sendError` instead of formatting responses ad hoc.

## Split Decision

Keep routes in the same Unity client API when they share:

- The same Firebase Auth/App Check/client-version middleware.
- The same response envelope and Unity DTO contract.
- Similar runtime options, secrets, memory, timeout, and concurrency needs.
- Similar deployment cadence and blast radius.

Split into a separate Express app/export when a route group has a different
security or runtime profile:

- **Unity client API**: gameplay/auth/config routes called by the game client.
- **Integration API**: server-to-server webhooks or partner calls with HMAC,
  shared-key, IP allowlist, or provider verification instead of player auth.
- **Admin API**: internal tools and admin dashboards with stricter auth and
  audit logging.
- **Debug API**: debug or cheat endpoints that should be disabled or isolated in
  production.
- **Hot-path API**: matchmaking or high-traffic routes needing different
  `minInstances`, `concurrency`, timeout, memory, or cold-start tuning.

Do not split every endpoint into its own function by default. Too many exports
make Unity base URL management, shared middleware, contract testing, and
deployment operations harder. Split by boundary, not by handler count.

When a single `index.js` becomes hard to maintain, first move route groups into
router modules while keeping the same exported app:

```js
const gameplayRoutes = require("./routes/gameplay");
const authRoutes = require("./routes/auth");

app.use("/", gameplayRoutes);
app.use("/auth", authRoutes);
```

## Server Rules

- Unity is an untrusted client. Validate all request fields on the server.
- Privileged operations such as currency, inventory, purchases, rewards,
  leaderboards, and anti-cheat-sensitive progression must run in trusted
  Functions/Admin SDK code.
- Authenticate player endpoints with Firebase ID token bearer headers when the
  route needs a user. Use App Check headers when the project has App Check.
- Keep server-to-server integration endpoints separate from Unity endpoints and
  guard them with integration auth such as shared key, HMAC, or provider-specific
  verification.
- Use stable lower_snake_case error codes; Unity should map those codes to
  `ApiCode` or equivalent enums.
- Add or update focused unit tests for expected behavior when adding routes,
  authorization behavior, economy mutations, or schema validation. Use
  emulator/Postman/Newman tests as integration coverage, not as a replacement
  for handler unit tests.

## Express Route Pattern

```js
"use strict";

const express = require("express");
const { onRequest } = require("firebase-functions/v2/https");
const {
  readBody,
  requireAuth,
  verifyAppCheck,
  sendResponse
} = require("./core/bootstrap");
const { claimRewardHandler } = require("./game/rewards");

const app = express();
app.use(express.json({ limit: "1mb" }));

const routes = [
  ["/claimReward", claimRewardHandler]
];

for (const [path, handler] of routes) {
  app.all(path, handler);
}

app.use((err, req, res, next) => {
  if (res.headersSent) return next(err);
  return sendResponse(req, res, 500, { ok: false, code: "server_error" });
});

exports.api = onRequest({ region: "europe-west1", invoker: "public" }, app);
```

Handlers should be small orchestration functions:

```js
async function claimRewardHandler(req, res) {
  if (req.method !== "POST") {
    return sendResponse(req, res, 405, { ok: false, code: "method_not_allowed" });
  }

  const auth = await requireAuth(req, res);
  if (!auth) return;

  if (!(await verifyAppCheck(req, res))) return;

  const body = readBody(req);
  const rewardId = String(body.rewardId || "").trim();
  if (!rewardId) {
    return sendResponse(req, res, 400, { ok: false, code: "bad_request" });
  }

  const result = await grantReward(auth.uid, rewardId);
  return sendResponse(req, res, 200, { ok: true, code: "ok", reward: result });
}
```

## Unity Client Pattern

- Unity calls Functions through a dedicated API client layer, not directly from
  gameplay systems.
- Keep endpoint names centralized as constants such as `CloudFunctionEndpoint`.
- Use serializable request/response DTOs. Response DTOs should inherit or match a
  common `BaseResponse` shape containing `ok` and `code`.
- Wrap HTTP results in a result envelope carrying request id, original request,
  status, raw body, parsed response, and stable error code.
- Use the repository's established async abstraction. Use UniTask only when it
  is already installed and accepted for the owning bounded context. Do not
  introduce R3 or another reactive package for request streams unless that
  context already owns it or an accepted ADR explicitly selects it.
- Add auth bearer token, App Check token, client version, country/debug headers,
  and content negotiation headers in one transport class.
- Do not let gameplay systems build raw URLs, headers, JSON, or retry logic.

## Contract and Compatibility

- Treat endpoint names, request DTOs, response DTOs, and error codes as a client
  contract.
- Keep a stable error-code registry in Unity, for example `ApiCode`, and update
  it whenever Functions add a new public `code`.
- Preserve backward compatibility for shipped clients. Add optional fields before
  removing or renaming fields.
- Use idempotency tokens for retryable economy, purchase, reward, matchmaking,
  and inventory mutations.
- Keep route names and Unity endpoint constants in sync. Prefer adding a test or
  generated check if the project has many endpoints.
- Version or gate breaking changes with client version policy or Remote Config.

## Expected Behavior Tests

Every new or changed Unity-facing route should have focused unit tests that
assert behavior, not implementation details:

- Success response shape: status code, `{ ok: true, code: "ok" }`, and the
  public DTO fields Unity consumes.
- Method guard: unsupported methods return `method_not_allowed`.
- Auth guard: missing, expired, or mismatched Firebase Auth returns the stable
  auth error code used by the project.
- App Check guard: missing or invalid App Check returns the project-standard
  App Check error when the route requires it.
- Body validation: missing, malformed, or out-of-range fields return
  `bad_request` or the route-specific stable validation code.
- Mutation behavior: rewards, inventory, purchases, economy, and leaderboard
  writes change exactly the expected documents and reject unauthorized changes.
- Retry behavior: retryable mutations use idempotency tokens and do not double
  grant currency, rewards, inventory, or purchase fulfillment.
- Unity contract: every public error `code` is mapped by `ApiCode` or the
  equivalent client enum.

Use the project's existing test runner first. In JavaScript Functions projects,
prefer the existing `npm test` command or `node --test` setup and mock
Firebase/Admin helpers where possible. Emulator/Newman tests are useful for
middleware, routing, and end-to-end validation, but they should not be the only
coverage for business logic.

On the Unity side, add EditMode tests for request DTO serialization, response
DTO parsing, `Result`/`ApiCode` mapping, endpoint constants, and transport
result parsing when the client contract changes. Use PlayMode tests only when
Unity lifecycle, scene wiring, UI, or real engine integration is required.

Minimal Unity shape:

```csharp
public static class CloudFunctionEndpoint
{
    public const string ClaimReward = "claimReward";
}

[Serializable]
public sealed class ClaimRewardReq
{
    public string rewardId;
}

[Serializable]
public sealed class ClaimRewardRes : BaseResponse
{
    public RewardEntry reward;
}

public UniTask<ResultEnvelope<ClaimRewardReq, ClaimRewardRes>> ClaimRewardAsync(
    string rewardId,
    CancellationToken cancellationToken)
{
    var request = new ClaimRewardReq { rewardId = rewardId };
    return RequestAsync<ClaimRewardReq, ClaimRewardRes>(
        CloudFunctionEndpoint.ClaimReward,
        request,
        requiresAuth: true,
        cancellationToken);
}
```

## Add-route Checklist

1. Add the Express route and handler export.
2. Validate method, auth, App Check, request body, and game/app scope.
3. Return the standard `{ ok, code }` envelope through shared response helpers.
4. Add Unity endpoint constant, request DTO, response DTO, and API client method.
5. Add or update expected behavior tests: handler unit tests for success and
   failure paths, emulator/Newman coverage where useful, and Unity EditMode
   client parsing tests when DTOs or error codes change.
6. Add idempotency or duplicate-request handling for retryable mutations.
7. Update Postman/collection docs or API docs when the project uses them.
8. Decide whether the route belongs in the Unity client API, integration API,
   admin API, debug API, or a hot-path API export.
