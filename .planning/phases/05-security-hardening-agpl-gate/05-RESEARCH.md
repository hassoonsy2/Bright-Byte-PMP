# Phase 5: Security Hardening + AGPL Gate - Research

**Researched:** 2026-06-03
**Domain:** Django security hardening, Node.js constant-time auth, telemetry neutralization, AGPL §13 compliance
**Confidence:** HIGH (all key claims verified against source code in this session)

---

## Summary

Phase 5 is the final gate before serving real client data. All four requirements are surgical, file-specific changes with no new external dependencies. The codebase has already been prepared (render.yaml provisions `SECRET_KEY` as `generateValue: true`, `CORS_ALLOWED_ORIGINS` is already wired as an explicit list) but has several insecure fallback paths that remain active when those env vars are absent or incorrectly set. The research locates every exact file and line that needs to change.

**SEC-01 (Django settings):** `SECRET_KEY` falls back to `get_random_secret_key()` (ephemeral per process restart), `ALLOWED_HOSTS` defaults to `"*"`, and `CORS_ALLOW_ALL_ORIGINS = True` is set when `CORS_ALLOWED_ORIGINS` is empty — all three in `apps/api/plane/settings/common.py`. A boot-time guard (settings-import-time `ImproperlyConfigured` or Django system check) must reject these insecure combinations before the process serves traffic.

**SEC-02 (live server timing-safe compare):** `apps/live/src/lib/auth-middleware.ts` line 38 uses `secretKey !== env.LIVE_SERVER_SECRET_KEY` — a plain string inequality. Node's built-in `crypto.timingSafeEqual` (available since Node 6; project runs Node 22) requires `Buffer` inputs of identical byte-length; a length-equality pre-check must accompany it to prevent length-oracle attacks.

**SEC-03 (print/telemetry):** Nine `print()` calls survive in production-reachable code paths (four are unconditional in error/exception paths, four are `if settings.DEBUG`-gated and therefore safe in production). The unconditional ones in `notification_task.py:673`, `deletion_task.py:99`, `storage.py:96`, and `app/views/base.py:79` ("Server Error" branch) need replacing with `logger.*`. The OTLP telemetry in `telemetry_metrics.py` hardcodes `"https://telemetry.plane.so"` as the default endpoint; the `is_telemetry_enabled` flag (Instance model field, default `True`) and the `push-instance-metrics` Celery beat task are the on/off controls — the safest approach is to set `OTLP_ENDPOINT` to an internal/null endpoint in `render.yaml` and ensure `is_telemetry_enabled` defaults to `False` for new instances, so no data phones home without explicit admin opt-in. PostHog event tracking in `event_tracking_task.py` already guards behind `POSTHOG_API_KEY and POSTHOG_HOST` (returns silently when unset) — correct, no env vars to set. Sixteen `plane.so` URLs in frontend components (help links, changelog, forum, bug report) were deferred to Phase 5 by the Phase 1 brand sweep and need replacement or removal.

**SEC-04 (AGPL §13):** No `NOTICE` file exists at the repo root. No source-availability link exists in the deployed app. The AGPL requires network-served software to provide a way for users to obtain the corresponding source. The safest implementation: add a `NOTICE` file (attribution only, not a copyright header), add a `/source` route to `plane.web.urls` serving a redirect to the public repo or a static disclosure page, and link it from the auth-screen footer. `COPYRIGHT.txt` and `LICENSE.txt` MUST remain byte-identical — the CI `copyright-check.yml` runs `addlicense -check -f COPYRIGHT.txt` against all `*.py` / `*.ts` / `*.tsx` files and fails on any edit.

**Primary recommendation:** Execute as four sequential tasks in the order SEC-01 → SEC-02 → SEC-03 → SEC-04. Each is independently committable. No new npm or pip packages are required.

---

<phase_requirements>

## Phase Requirements

| ID     | Description                                                                                                                                                                                          | Research Support                                                                                                                                                               |
| ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| SEC-01 | Django settings hardened — stable `SECRET_KEY`, exact `ALLOWED_HOSTS`, explicit `CORS_ALLOWED_ORIGINS` (https only, no allow-all fallback with credentials); boot-time guard rejects insecure config | Settings files fully located; guard hook site identified (settings-import-time in `common.py`, consistent with existing `ImproperlyConfigured` usage in `plane/utils/host.py`) |
| SEC-02 | Live-server secret comparison is constant-time — `apps/live/src/lib/auth-middleware.ts` uses timing-safe compare (replaces `!==`)                                                                    | Exact line 38 located; `crypto.timingSafeEqual` confirmed available in Node 22; length-safety pattern documented                                                               |
| SEC-03 | `print()` removed from backend data/error paths; telemetry repointed or disabled (no data sent to Plane endpoints)                                                                                   | All 9 print sites catalogued by file:line; telemetry endpoint default and on/off mechanism confirmed; 16 plane.so frontend URLs enumerated                                     |
| SEC-04 | AGPL §13 network source-availability offer live in deployed app; attribution in top-level `NOTICE`/`CHANGES` file; copyright headers and `LICENSE.txt` unchanged                                     | No NOTICE file exists; `plane.web.urls` is the correct injection point for `/source`; CI addlicense mechanics confirmed verbatim                                               |

</phase_requirements>

---

## Architectural Responsibility Map

| Capability                    | Primary Tier                    | Secondary Tier   | Rationale                                                                                                                     |
| ----------------------------- | ------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Boot-time config guard        | API / Backend (settings import) | —                | Django settings are resolved at import time; guard belongs in `common.py` or a `checks.py` registered via `AppConfig.ready()` |
| Constant-time secret compare  | Frontend Server (live server)   | —                | `auth-middleware.ts` runs in `apps/live` Express process; no DB, no browser                                                   |
| Print cleanup                 | API / Backend                   | —                | `print()` calls are in Django views and Celery tasks in `apps/api`                                                            |
| OTLP telemetry disable        | API / Backend                   | —                | Celery beat task in `apps/api`; env var in `render.yaml`                                                                      |
| PostHog telemetry             | API / Backend                   | —                | `event_tracking_task.py` in `apps/api`; already guard-gated; just needs env vars left unset                                   |
| Frontend plane.so URL cleanup | Browser / Client                | —                | Static strings in React components in `apps/web` and `apps/admin`                                                             |
| AGPL §13 source offer         | API / Backend                   | Browser / Client | HTTP endpoint in `plane.web.urls`; link surface in frontend footer                                                            |
| NOTICE file                   | Static / Repo                   | —                | Top-level file; no runtime component                                                                                          |

---

## SEC-01: Django Settings Hardening

### Exact File Locations

**`apps/api/plane/settings/common.py`** — all three insecure defaults live here:

| Line    | Code                                                                                                   | Problem                                                                                                                                                                                 |
| ------- | ------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 29      | `SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())`                                   | Falls back to ephemeral random key on every process restart; session tokens/CSRF tokens are invalidated across restarts or workers                                                      |
| 76      | `ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")`                                      | Default `"*"` allows any host header                                                                                                                                                    |
| 163–171 | `if cors_allowed_origins: ... else: CORS_ALLOW_ALL_ORIGINS = True`                                     | When `CORS_ALLOWED_ORIGINS` env var is empty/missing, sets `CORS_ALLOW_ALL_ORIGINS = True` while `CORS_ALLOW_CREDENTIALS = True` is fixed on line 163 — cross-origin credential leakage |
| 169     | `secure_origins = False if [origin for origin in cors_allowed_origins if "http:" in origin] else True` | Accepts `http://` origins; in production all origins must be `https://`                                                                                                                 |

**`render.yaml`** — current state (good):

- `SECRET_KEY: generateValue: true` (line 42) — Render generates once and persists. [VERIFIED: codebase]
- `CORS_ALLOWED_ORIGINS: https://bright-byte-web.onrender.com,https://bright-byte-admin.onrender.com,https://bright-byte-space.onrender.com` (line 93–94) — already explicit. [VERIFIED: codebase]
- `ALLOWED_HOSTS` is NOT present in `render.yaml` — defaults to `"*"`. This is the gap to fix. [VERIFIED: codebase]

**`apps/api/plane/settings/production.py`** — no overrides to `ALLOWED_HOSTS` or `CORS`. Only adds `SECURE_PROXY_SSL_HEADER`. No changes needed here for SEC-01.

### Boot-Time Guard Hook Site

Django provides two idiomatic hooks:

1. **Settings-import-time guard** (simplest): Add validation code directly at the bottom of `common.py` after the settings definitions. Raises `django.core.exceptions.ImproperlyConfigured` (already imported/used in `plane/utils/host.py:7`). This runs before the process accepts any connection. [ASSUMED: hook placement is valid; `ImproperlyConfigured` is already a project pattern]

2. **Django system checks** (`checks.py` + `AppConfig.ready()`): More canonical for reusable checks; decorates with `@register()`. One existing `ready()` override is in `apps/api/plane/api/apps.py`. [VERIFIED: codebase]

**Recommendation:** Settings-import-time guard in `common.py` is simpler and equally effective for a self-hosted app. It catches misconfiguration before the WSGI/ASGI server is woken. Raise `ImproperlyConfigured` for missing/insecure `SECRET_KEY` and for `CORS_ALLOW_ALL_ORIGINS=True` when credentials are also enabled.

### Guard Logic (what to check)

```python
# Source: verified from common.py analysis + Django docs pattern [ASSUMED: exact guard text]
import sys
from django.core.exceptions import ImproperlyConfigured

_guard_errors = []

# 1. SECRET_KEY must come from env — default means ephemeral key
if not os.environ.get("SECRET_KEY"):
    _guard_errors.append(
        "SECRET_KEY env var is not set. "
        "A random fallback is generated per process restart — session and CSRF tokens "
        "will be invalidated on every restart. Set a stable SECRET_KEY."
    )

# 2. ALLOWED_HOSTS must not be wildcard in non-DEBUG mode
if not DEBUG and "*" in ALLOWED_HOSTS:
    _guard_errors.append(
        "ALLOWED_HOSTS is '*' — set it to the exact hostnames of your Render services. "
        "Example: ALLOWED_HOSTS=bright-byte-api.onrender.com"
    )

# 3. CORS_ALLOW_ALL_ORIGINS must not be True when credentials are enabled
if globals().get("CORS_ALLOW_ALL_ORIGINS") and CORS_ALLOW_CREDENTIALS:
    _guard_errors.append(
        "CORS_ALLOW_ALL_ORIGINS=True with CORS_ALLOW_CREDENTIALS=True is insecure. "
        "Set CORS_ALLOWED_ORIGINS to explicit https:// origins."
    )

if _guard_errors and not DEBUG:
    raise ImproperlyConfigured(
        "Insecure configuration detected:\n" + "\n".join(f"  - {e}" for e in _guard_errors)
    )
```

**Note:** Guard only fires when `DEBUG=False` (production). Local dev with no env vars must not break.

### render.yaml Change Required (SEC-01)

Add `ALLOWED_HOSTS` env var to the `bright-byte-api` service pointing to the API service hostname. Workers and migrator share `SECRET_KEY` via `fromService` — already done. [VERIFIED: render.yaml]

---

## SEC-02: Constant-Time Secret Compare

### Exact File and Line

**`apps/live/src/lib/auth-middleware.ts`**:

- **Line 34:** `// TODO - Move to hmac` — original developer acknowledged this is incomplete
- **Lines 36–38:**
  ```typescript
  const secretKey = req.headers["live-server-secret-key"];
  if (!secretKey || secretKey !== env.LIVE_SERVER_SECRET_KEY) {
  ```
  The `!==` comparison is a **timing-oracle vulnerability**: an attacker can measure response latency to infer how many characters of the secret they guessed correctly.

### Fix Pattern

Node.js `crypto.timingSafeEqual` requires `Buffer` arguments of **equal byte length**. If lengths differ, the function throws (not a constant-time false). A length check before calling it is not a timing oracle — length is not the secret. [VERIFIED: Node.js docs pattern [ASSUMED: exact TypeScript code shape]]

```typescript
// Source: Node.js crypto docs — timingSafeEqual [ASSUMED: exact code]
import { timingSafeEqual } from "crypto";

export const requireSecretKey = (req: Request, res: Response, next: NextFunction): void => {
  const provided = req.headers["live-server-secret-key"];
  const expected = env.LIVE_SERVER_SECRET_KEY;

  let isValid = false;
  if (typeof provided === "string" && provided.length === expected.length) {
    isValid = timingSafeEqual(Buffer.from(provided, "utf8"), Buffer.from(expected, "utf8"));
  }

  if (!isValid) {
    logger.warn(`...`); // existing warn block unchanged
    res.status(401).json({ error: "Unauthorized", status: 401 });
    return;
  }
  next();
};
```

**Why length check is safe:** The secret length is not secret (it is a fixed-format Render `generateValue` token). Constant-time equality on fixed-length secrets is sufficient. [ASSUMED: Render generateValue token length is fixed; if variable-length secrets are possible, use a constant-time HMAC comparison instead — the `// TODO - Move to hmac` comment acknowledges this]

**Import source:** `crypto` is a Node built-in; no new package needed. Already available in Node 22 (`timingSafeEqual` is available since Node 6). [VERIFIED: tested with `node -e "const crypto = require('crypto'); console.log(typeof crypto.timingSafeEqual)"` → `function`]

---

## SEC-03: Print Removal and Telemetry Neutralization

### A. `print()` Inventory

#### Unconditional prints (run in production — MUST replace with `logger.*`):

| File                                          | Line | Content                                                                           | Severity                                                                   | Fix                                                                          |
| --------------------------------------------- | ---- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `apps/api/plane/app/views/base.py`            | 79   | `(print(e, traceback.format_exc()) if settings.DEBUG else print("Server Error"))` | HIGH — in `handle_exception()`, called on every unhandled server exception | Replace both branches: `logger.error(...)` in both DEBUG and non-DEBUG cases |
| `apps/api/plane/bgtasks/notification_task.py` | 673  | `print(e)`                                                                        | HIGH — bare except in notification bulk-create                             | Replace with `logger.exception(e)`                                           |
| `apps/api/plane/bgtasks/deletion_task.py`     | 99   | `print(f"Error handling relation {related_name}: {str(e)}")`                      | MEDIUM — in soft-delete relation cleanup                                   | Replace with `logger.error(...)`                                             |
| `apps/api/plane/settings/storage.py`          | 96   | `print(f"Error generating presigned POST URL: {e}")`                              | MEDIUM — in S3 presigned-URL generator (data path)                         | Replace with `log_exception(e)` or `logger.error(...)`                       |

#### DEBUG-gated prints (only run when `DEBUG=True` — safe in production, but clean up for hygiene):

| File                                       | Lines            | Content                                             | Action                                           |
| ------------------------------------------ | ---------------- | --------------------------------------------------- | ------------------------------------------------ |
| `apps/api/plane/app/views/base.py`         | 115–118, 210–213 | Query-count print inside `if settings.DEBUG:`       | Replace with `logger.debug(...)` for cleanliness |
| `apps/api/plane/api/views/base.py`         | 106–109, 234–238 | Same query-count pattern                            | Replace with `logger.debug(...)`                 |
| `apps/api/plane/space/views/base.py`       | 110–112, 193–195 | Same query-count pattern                            | Replace with `logger.debug(...)`                 |
| `apps/api/plane/license/api/views/base.py` | 103–104          | Same query-count pattern                            | Replace with `logger.debug(...)`                 |
| `apps/api/plane/bgtasks/webhook_task.py`   | 472              | `if settings.DEBUG: print(e)` — already DEBUG-gated | Replace with `logger.debug(...)`                 |

**Logger import pattern in use:** `logger = logging.getLogger("plane.worker")` or `"plane.api"` etc. Match the existing logger name for the module. [VERIFIED: codebase]

### B. OTLP Telemetry (phones home to `telemetry.plane.so`)

**Key files:**

- `apps/api/plane/utils/otlp_endpoints.py` — hardcodes `_DEFAULT_OTLP_ENDPOINT = "https://telemetry.plane.so"` (line 19) as the fallback when `OTLP_ENDPOINT` env var is absent
- `apps/api/plane/license/bgtasks/telemetry_metrics.py` — the Celery task; reads `Instance.is_telemetry_enabled`; already has early-return on line 80: `if not instance.is_telemetry_enabled: return`
- `apps/api/plane/celery.py` — beat schedule, line 50–53: `"push-instance-metrics"` task runs every `METRICS_PUSH_INTERVAL_MINUTES` (default 360 minutes / 6 hours)
- `apps/api/plane/license/models/instance.py` line 35: `is_telemetry_enabled = models.BooleanField(default=True)` — new instances default to telemetry **on**

**Strategy (two-layer):** [ASSUMED: this is the minimal-risk approach; alternatives are: delete the beat task, or null the endpoint unconditionally]

1. **Instance model default**: Change `default=True` → `default=False` in `Instance.is_telemetry_enabled`. This prevents new instance registration from phone-home. (Requires a migration.)
2. **Env var in render.yaml**: Add `OTLP_ENDPOINT: ""` or point to a self-controlled endpoint. When set to an invalid URL the task will fail gracefully (it already catches `Exception` and logs, line 361). Alternatively, set `METRICS_PUSH_INTERVAL_MINUTES=99999999` to effectively disable scheduling.
3. **Admin UI**: The telemetry link in `apps/admin/app/(all)/(dashboard)/general/form.tsx:115` points to `https://developers.plane.so/self-hosting/telemetry` — update to internal docs or remove. The `apps/admin/components/instance/setup-form.tsx:358` has the same link.

### C. PostHog Event Tracking

**File:** `apps/api/plane/bgtasks/event_tracking_task.py`

Current behavior (lines 63–65):

```python
POSTHOG_API_KEY, POSTHOG_HOST = posthogConfiguration()
if not (POSTHOG_API_KEY and POSTHOG_HOST):
    logger.warning("Event tracking is not configured")
    return
```

This is **already safe**: if `POSTHOG_API_KEY` and `POSTHOG_HOST` are absent from env (which they are — not in `render.yaml`), the task exits immediately. No data is sent. **No code change needed** — just confirm the env vars are not set.

The `apps/api/plane/license/api/views/instance.py` lines 146–147 expose `posthog_api_key` and `posthog_host` in the instance config API response. These will be `None` when the env vars are absent. **No change needed.** [VERIFIED: codebase]

### D. Frontend `plane.so` URLs (BRAND-11 scope, SEC-03 alignment)

The Phase 1 brand sweep deferred these to Phase 5. All are in `apps/web` or `apps/admin` — user-visible links pointing to Plane's infrastructure.

| File                                                                       | Lines              | Content                                                     | Action                                                                       |
| -------------------------------------------------------------------------- | ------------------ | ----------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `apps/web/core/components/workspace/sidebar/help-section/root.tsx`         | 52, 83             | Docs link `go.plane.so/p-docs`, Forum link `forum.plane.so` | Replace with Bright-Byte support URL or remove                               |
| `apps/web/core/components/power-k/config/help-commands.ts`                 | 40, 53, 66         | Docs, Forum, GitHub bug-report URLs                         | Replace / remove command entries                                             |
| `apps/web/core/components/common/latest-feature-block.tsx`                 | 23                 | `plane.so/changelog`                                        | Replace or remove latest-feature component                                   |
| `apps/web/core/components/global/product-updates/footer.tsx`               | 21, 33, 44, 55, 64 | Docs, changelog, support email, forum, pages marketing      | Replace all with Bright-Byte equivalents or remove component                 |
| `apps/web/core/components/global/product-updates/fallback.tsx`             | 19–20              | Two changelog category URLs                                 | Replace or remove fallback                                                   |
| `apps/web/app/layout.tsx`                                                  | 45–46, 52          | OG/Twitter image URLs `app.plane.so/og-image.png`           | Replace with hosted Bright-Byte OG image URL                                 |
| `apps/web/app/(all)/workspace-invitations/page.tsx`                        | 118                | `forum.plane.so` link                                       | Replace or remove                                                            |
| `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/page.tsx` | 35                 | `plane.so/` link                                            | Replace or remove                                                            |
| `apps/web/app/error/prod.tsx`                                              | 20, 25             | `mailto:support@plane.so`, `status.plane.so`                | Replace with Bright-Byte support email and status page                       |
| `apps/web/core/components/inbox/sidebar/inbox-list-item.tsx`               | 132                | `intake@plane.so` email comparison                          | Keep (internal bot check — not user-visible URL)                             |
| `apps/web/core/components/estimates/root.tsx`                              | 114                | `docs.plane.so` docs link                                   | Replace or remove                                                            |
| `apps/admin/app/(all)/(dashboard)/sidebar-help-section.tsx`                | 24, 29             | Docs, forum links                                           | Replace or remove                                                            |
| `apps/admin/app/(all)/(dashboard)/ai/form.tsx`                             | 132                | `plane.so/contact`                                          | Replace or remove (Phase 3 deferred to Phase 5)                              |
| `apps/admin/components/instance/setup-form.tsx`                            | 358                | `developers.plane.so/self-hosting/telemetry`                | Update or remove                                                             |
| `apps/api/plane/settings/openapi.py`                                       | 15–24, 48          | Plane API title, contact URL, server URL                    | Update to Bright-Byte contact; only relevant when `ENABLE_DRF_SPECTACULAR=1` |

**Note:** `apps/api/plane/bgtasks/workspace_seed_task.py` line 529: `email=f"bot_user_{workspace.id}@plane.so"` — internal bot user email, not user-visible; classified as Keep per brand sweep conventions.

---

## SEC-04: AGPL §13 Source Availability

### What AGPL §13 Requires [ASSUMED: legal interpretation; verify with counsel for production]

AGPL §13 (GNU Affero GPL v3, Section 13) states: if the program is modified and used to provide a service over a network, the operator must offer users a way to obtain the corresponding source code. The source offer must be accessible from the application itself (e.g., a link in the interface or a known URL).

**Minimum compliant implementation:**

1. A publicly accessible URL where the source can be obtained (the upstream Plane CE repo on GitHub, or the Bright-Byte fork if published)
2. A link to that URL accessible to users when they interact with the network service
3. Attribution of the original work in the distribution (the `NOTICE` file)

### What MUST NOT Change [VERIFIED: codebase, CI]

- **`LICENSE.txt`**: GNU AGPL v3 full text — byte-identical. Do not touch.
- **All `*.py`, `*.ts`, `*.tsx` file headers**: `Copyright (c) 2023-present Plane Software, Inc. and contributors / SPDX-License-Identifier: AGPL-3.0-only`. The CI workflow `copyright-check.yml` runs `addlicense -check -f COPYRIGHT.txt` against all git-tracked Python and TypeScript files (excluding migrations and `*.config.ts`/`*.d.ts`). Any edit to an existing header or any new file missing the header fails CI. **Never edit these headers.** [VERIFIED: `.github/workflows/copyright-check.yml`]
- **`COPYRIGHT.txt`**: Three-line template: `Copyright (c) 2023-present Plane Software, Inc. and contributors / SPDX-License-Identifier: AGPL-3.0-only / See the LICENSE file for details.` — byte-identical. Do not touch.

### New Files to Create

**`NOTICE`** (top-level, no AGPL header required — this is an attribution file, not a source file):

```
Bright-Byte PMP
Copyright (c) 2026 Bright-Byte Ltd. and contributors

This product includes software developed by Plane Software, Inc.
and contributors, available at https://github.com/makeplane/plane
under the GNU Affero General Public License v3.0 (AGPL-3.0).

Modifications made by Bright-Byte Ltd.:
- Product rebrand: "Bright-Byte PMP" in place of "Plane" across UI, i18n, metadata
- AI assistant renamed "Byte" (label-only; backend unchanged)
- Billing, upsell, and paid-plan surfaces removed
- Package scope renamed @plane/* → @bright-byte/*
- Deployed as a shared managed instance on Render.com
- Security hardening: constant-time secret compare, config boot-time guard

Source code for this deployment is available at:
[URL of Bright-Byte's public fork or the upstream makeplane/plane repo]

The full license text is in LICENSE.txt.
```

**Network source offer (SEC-04 core):** Add a `/source` HTTP endpoint to the Django app that either:

- Returns a 302 redirect to the public source repo URL, OR
- Returns a JSON/HTML page with the source URL

**Implementation site:** `apps/api/plane/web/views.py` + `apps/api/plane/web/urls.py`

```python
# apps/api/plane/web/views.py — new view (add AGPL header to file — already present)
def source_disclosure(request):
    """AGPL §13 network source availability offer."""
    source_url = os.environ.get(
        "SOURCE_AVAILABILITY_URL",
        "https://github.com/makeplane/plane"  # fallback to upstream
    )
    return JsonResponse({
        "license": "AGPL-3.0-only",
        "source": source_url,
        "notice": "This service runs Bright-Byte PMP, a modified version of Plane CE. "
                  "You may obtain the corresponding source code at the URL above.",
    })
```

```python
# apps/api/plane/web/urls.py — add path
urlpatterns = [
    path("robots.txt", robots_txt),
    path("source", source_disclosure),
    path("", health_check),
]
```

**Frontend link:** Add a "Source code (AGPL)" link in `apps/web/core/components/auth-screens/footer.tsx` pointing to `/source` (or the direct repo URL). This ensures users see the offer when they authenticate. The auth-screen footer is already the lowest-friction placement that does not require being logged in.

**render.yaml:** Add `SOURCE_AVAILABILITY_URL` env var pointing to the public source repo.

### NOTICE vs CHANGES File

The AGPL explicitly mentions a "written offer" or a visible indication in the interface. A top-level `NOTICE` file (Apache-style attribution) is sufficient for the attribution requirement. A `CHANGES` file is optional and records what was changed — useful for audit but not mandated by AGPL §13 alone. Creating `NOTICE` alone is sufficient; creating both is fine.

---

## Don't Hand-Roll

| Problem                         | Don't Build                         | Use Instead                                                               | Why                                                |
| ------------------------------- | ----------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------- |
| Constant-time string comparison | Custom character-loop timing code   | `crypto.timingSafeEqual` (Node built-in)                                  | Subtle timing channels; use the audited primitive  |
| CORS credential safety          | Custom `Origin:` header validation  | `django-cors-headers` already installed; configure `CORS_ALLOWED_ORIGINS` | Already in MIDDLEWARE; just set env vars correctly |
| Boot-time config validation     | Runtime try/except in view handlers | `ImproperlyConfigured` raised at import time                              | Fails fast before accepting any connections        |

---

## Common Pitfalls

### Pitfall 1: Guard Fires in Local Dev

**What goes wrong:** Guard raises `ImproperlyConfigured` when developer runs without env vars.
**Why it happens:** `ALLOWED_HOSTS="*"` is the local default.
**How to avoid:** Gate the guard on `not DEBUG`. Local dev always runs with `DEBUG=True`; production always has `DEBUG=False`. [VERIFIED: `production.py` defaults `DEBUG=0`; `local.py` sets `DEBUG=True`]
**Warning signs:** `ImproperlyConfigured` on `manage.py runserver` without env vars.

### Pitfall 2: timingSafeEqual Throws on Length Mismatch

**What goes wrong:** Calling `timingSafeEqual(a, b)` when `a.length !== b.length` throws `RangeError: Input buffers must have the same byte length`.
**Why it happens:** The function requires equal-length inputs; it does not return false.
**How to avoid:** Always check `provided.length === expected.length` before calling `timingSafeEqual`. This is not a timing oracle because the secret length is not the secret — Render tokens have a known, fixed format.
**Warning signs:** Unhandled `RangeError` on 401 responses with wrong-length tokens.

### Pitfall 3: Editing `COPYRIGHT.txt` or File Headers

**What goes wrong:** CI `copyright-check.yml` fails; AGPL violation.
**Why it happens:** Confusion between the attribution `NOTICE` file (new, owned by Bright-Byte) and the source-file copyright headers (Plane Software, Inc.; must stay).
**How to avoid:** Only add the top-level `NOTICE` file. Never edit existing `# Copyright (c) 2023-present Plane Software, Inc.` headers. New files added in Phase 5 must carry the same verbatim header. [VERIFIED: `copyright-check.yml`]
**Warning signs:** `addlicense -check` failure in CI on any modified or new `.py`/`.ts`/`.tsx` file.

### Pitfall 4: `CORS_ALLOW_ALL_ORIGINS` + `CORS_ALLOW_CREDENTIALS` in Production

**What goes wrong:** Every cross-origin request can include session cookies — effectively makes the session cookie accessible to any origin.
**Why it happens:** When `CORS_ALLOWED_ORIGINS` env var is empty, `common.py` line 171 sets `CORS_ALLOW_ALL_ORIGINS = True`. `CORS_ALLOW_CREDENTIALS = True` is unconditional on line 163.
**How to avoid:** The boot-time guard catches this. Also ensure `render.yaml` always has `CORS_ALLOWED_ORIGINS` populated. [VERIFIED: render.yaml already has explicit origins for the API service]
**Warning signs:** `CORS_ALLOW_ALL_ORIGINS = True` appears in Django settings dump (`manage.py diffsettings`).

### Pitfall 5: Telemetry Beat Task Keeps Running

**What goes wrong:** `push-instance-metrics` Celery task fires every 6 hours even after disabling telemetry via admin UI, because `is_telemetry_enabled` defaults to `True` for new instance registration.
**Why it happens:** `Instance.is_telemetry_enabled` defaults `True` in the model; the initial `configure_instance` management command sets up the DB record with the model default.
**How to avoid:** Change model default to `False` (with migration); also ensure `OTLP_ENDPOINT` in `render.yaml` does not point to `telemetry.plane.so`.
**Warning signs:** Network connections to `telemetry.plane.so` in Render logs.

---

## Code Examples

### SEC-01: Settings guard pattern

```python
# apps/api/plane/settings/common.py — add after all settings are defined
# Source: Django ImproperlyConfigured pattern [VERIFIED: plane/utils/host.py uses same pattern]
from django.core.exceptions import ImproperlyConfigured

_boot_errors = []

if not os.environ.get("SECRET_KEY"):
    _boot_errors.append(
        "SECRET_KEY env var is required in production. "
        "Without it, a random key is generated per process restart, "
        "invalidating all sessions and CSRF tokens."
    )

if not DEBUG and "*" in ALLOWED_HOSTS:
    _boot_errors.append(
        "ALLOWED_HOSTS='*' is not permitted in production. "
        "Set ALLOWED_HOSTS to comma-separated exact hostnames."
    )

if globals().get("CORS_ALLOW_ALL_ORIGINS") and CORS_ALLOW_CREDENTIALS:
    _boot_errors.append(
        "CORS_ALLOW_ALL_ORIGINS=True with CORS_ALLOW_CREDENTIALS=True is insecure. "
        "Set CORS_ALLOWED_ORIGINS to explicit https:// origin list."
    )

if _boot_errors and not DEBUG:
    raise ImproperlyConfigured(
        "\n".join(["Insecure configuration — fix before running in production:"] + _boot_errors)
    )
```

### SEC-02: Constant-time compare

```typescript
// apps/live/src/lib/auth-middleware.ts
// Source: Node.js crypto.timingSafeEqual [ASSUMED: exact code — verify against Node docs]
import { timingSafeEqual } from "crypto";
import type { Request, Response, NextFunction } from "express";
import { logger } from "@bright-byte/logger";
import { env } from "@/env";

export const requireSecretKey = (req: Request, res: Response, next: NextFunction): void => {
  const provided = req.headers["live-server-secret-key"];
  const expected = env.LIVE_SERVER_SECRET_KEY;

  let isValid = false;
  if (typeof provided === "string" && provided.length === expected.length) {
    try {
      isValid = timingSafeEqual(Buffer.from(provided, "utf8"), Buffer.from(expected, "utf8"));
    } catch {
      isValid = false;
    }
  }

  if (!isValid) {
    logger.warn(`[AUTH] Unauthorized access attempt — ${req.method} ${req.path} from ${req.ip}`);
    res.status(401).json({ error: "Unauthorized", status: 401 });
    return;
  }
  next();
};
```

### SEC-03: Logger replacement pattern

```python
# Replace: print(e)
# With:
import logging
logger = logging.getLogger("plane.worker")  # or "plane.api" etc per module
logger.exception("Notification bulk create failed: %s", e)
```

---

## Phase 4 Dependencies

Phase 5 settings work **consumes** Render-provided values set in Phase 4's `render.yaml`. The current state of `render.yaml`:

| Env Var                   | Status in render.yaml                                      | Phase 5 Action                                                        |
| ------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------- |
| `SECRET_KEY`              | `generateValue: true` on api, `fromService` on worker/beat | Already correct — no change needed                                    |
| `CORS_ALLOWED_ORIGINS`    | Explicit list on api service                               | Already correct — add to render.yaml validation checklist             |
| `ALLOWED_HOSTS`           | **Missing** — defaults to `"*"`                            | Add to `render.yaml` for api, worker, beat services                   |
| `OTLP_ENDPOINT`           | Not present                                                | Add `OTLP_ENDPOINT: ""` or self-hosted endpoint to disable phone-home |
| `SOURCE_AVAILABILITY_URL` | Not present                                                | Add for SEC-04                                                        |

---

## Validation Architecture

> `workflow.nyquist_validation` not explicitly false in config — section included.

### Test Framework

| Property              | Value                                                                |
| --------------------- | -------------------------------------------------------------------- |
| Django Framework      | pytest 7.x via `pytest.ini` in `apps/api/`                           |
| Live server Framework | Vitest 4.0.8 in `apps/live/`                                         |
| Config file (API)     | `apps/api/pytest.ini` — `DJANGO_SETTINGS_MODULE=plane.settings.test` |
| Quick run (API)       | `cd apps/api && python -m pytest -m unit -x`                         |
| Quick run (live)      | `cd apps/live && pnpm test`                                          |
| Full suite (API)      | `cd apps/api && python -m pytest`                                    |

### Phase Requirements → Test Map

| Req ID  | Behavior                                                                                  | Test Type       | Automated Command                                                                                                               | File Exists?     |
| ------- | ----------------------------------------------------------------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| SEC-01a | Boot guard raises `ImproperlyConfigured` when `SECRET_KEY` absent in non-DEBUG            | unit            | `pytest apps/api/plane/tests/unit/settings/test_config_guard.py::test_boot_guard_requires_secret_key -x`                        | ❌ Wave 0        |
| SEC-01b | Boot guard raises when `CORS_ALLOW_ALL_ORIGINS=True` + credentials                        | unit            | `pytest apps/api/plane/tests/unit/settings/test_config_guard.py::test_boot_guard_rejects_allow_all_cors -x`                     | ❌ Wave 0        |
| SEC-01c | Boot guard raises when `ALLOWED_HOSTS=['*']` in non-DEBUG                                 | unit            | `pytest apps/api/plane/tests/unit/settings/test_config_guard.py::test_boot_guard_rejects_wildcard_allowed_hosts -x`             | ❌ Wave 0        |
| SEC-01d | Guard is silent (no raise) when `DEBUG=True` regardless of env vars                       | unit            | `pytest apps/api/plane/tests/unit/settings/test_config_guard.py::test_boot_guard_silent_in_debug -x`                            | ❌ Wave 0        |
| SEC-02  | `requireSecretKey` middleware: correct secret → 200, wrong secret → 401, timing-safe path | unit            | `pnpm --filter live test -- --reporter=verbose lib/auth-middleware`                                                             | ❌ Wave 0        |
| SEC-03a | No bare `print()` in non-DEBUG paths — grep gate                                          | automated grep  | `grep -rn "^print\|[^#]print(" apps/api/plane/ --include="*.py" \| grep -v "migrations/" \| grep -v "settings.DEBUG"` returns 0 | N/A (CI gate)    |
| SEC-03b | OTLP endpoint does not point to `telemetry.plane.so` at boot                              | unit            | `pytest apps/api/plane/tests/unit/settings/test_telemetry.py::test_otlp_endpoint_not_plane_so -x`                               | ❌ Wave 0        |
| SEC-04a | `GET /source` returns 200 with `license` and `source` keys                                | smoke           | `pytest apps/api/plane/tests/contract/app/test_source_disclosure.py -x`                                                         | ❌ Wave 0        |
| SEC-04b | `NOTICE` file exists at repo root and contains "Plane Software" attribution               | automated check | `test -f NOTICE && grep -q "Plane Software" NOTICE`                                                                             | N/A (file check) |
| SEC-04c | `LICENSE.txt` is byte-identical to AGPL v3                                                | automated check | `addlicense -check -f COPYRIGHT.txt $(git ls-files '*.py' '*.ts' '*.tsx')` passes in CI                                         | Existing CI      |

### Wave 0 Gaps

- [ ] `apps/api/plane/tests/unit/settings/test_config_guard.py` — covers SEC-01a, SEC-01b, SEC-01c, SEC-01d
- [ ] `apps/api/plane/tests/unit/settings/test_telemetry.py` — covers SEC-03b
- [ ] `apps/api/plane/tests/contract/app/test_source_disclosure.py` — covers SEC-04a
- [ ] `apps/live/tests/lib/auth-middleware.test.ts` — covers SEC-02

### Sampling Rate

- **Per task commit:** run the unit tests for the specific requirement touched
- **Per wave merge:** `python -m pytest apps/api/plane/tests/unit/ -x && pnpm --filter live test`
- **Phase gate:** Full suite green + grep gate for `print()` before `/gsd:verify-work`

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category         | Applies | Standard Control                                                                  |
| --------------------- | ------- | --------------------------------------------------------------------------------- |
| V2 Authentication     | Yes     | Session cookie (existing); `requireSecretKey` middleware (SEC-02)                 |
| V3 Session Management | Yes     | `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` (already gated on `secure_origins`) |
| V4 Access Control     | No      | Not in scope for this phase                                                       |
| V5 Input Validation   | Partial | Boot-time env var validation (SEC-01 guard)                                       |
| V6 Cryptography       | Yes     | `crypto.timingSafeEqual` for secret compare (SEC-02)                              |

### Known Threat Patterns

| Pattern                                                 | STRIDE                 | Standard Mitigation                                   |
| ------------------------------------------------------- | ---------------------- | ----------------------------------------------------- |
| Timing oracle on secret compare                         | Information Disclosure | `crypto.timingSafeEqual`                              |
| Host header injection                                   | Spoofing               | `ALLOWED_HOSTS` whitelist                             |
| CORS credential leak (allow-all + credentials)          | Information Disclosure | Explicit `CORS_ALLOWED_ORIGINS` list                  |
| Ephemeral `SECRET_KEY` (session/CSRF invalidation)      | Tampering              | Stable `SECRET_KEY` from env                          |
| Telemetry phone-home (data exfiltration to third party) | Information Disclosure | Disable `is_telemetry_enabled`, unset `OTLP_ENDPOINT` |
| Unlicensed software deployment                          | Compliance             | AGPL §13 source offer, `NOTICE` file                  |

---

## Environment Availability

| Dependency                                    | Required By            | Available | Version  | Fallback |
| --------------------------------------------- | ---------------------- | --------- | -------- | -------- |
| Python 3.12                                   | Django API             | ✓         | (system) | —        |
| Node 22                                       | live server            | ✓         | v22.15.0 | —        |
| `crypto` (Node built-in)                      | SEC-02 timingSafeEqual | ✓         | built-in | —        |
| `django.core.exceptions.ImproperlyConfigured` | SEC-01 guard           | ✓         | built-in | —        |
| No new packages                               | All SEC requirements   | ✓         | —        | —        |

**No new packages to install for this phase.** Zero npm or pip additions required.

---

## Package Legitimacy Audit

> Not applicable — this phase installs zero new external packages.

---

## Runtime State Inventory

> This phase modifies settings and adds a NOTICE file, not a rename/migration.

| Category            | Items Found                                                                                          | Action Required                                                                                                                                                                               |
| ------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Stored data         | Instance model `is_telemetry_enabled=True` for any existing instance row                             | DB migration to change default; existing rows need one-time update (`UPDATE plane_license_instance SET is_telemetry_enabled=False`) — or accept that the admin must toggle it off post-deploy |
| Live service config | Render env vars: `ALLOWED_HOSTS` missing, `OTLP_ENDPOINT` missing, `SOURCE_AVAILABILITY_URL` missing | Add to `render.yaml`                                                                                                                                                                          |
| OS-registered state | None — no OS-level state involved                                                                    | None                                                                                                                                                                                          |
| Secrets/env vars    | `SECRET_KEY` already `generateValue: true` in render.yaml; `LIVE_SERVER_SECRET_KEY` same             | No change needed                                                                                                                                                                              |
| Build artifacts     | None — no rename; no egg-info or compiled artifacts affected                                         | None                                                                                                                                                                                          |

---

## Assumptions Log

| #   | Claim                                                                                                                             | Section | Risk if Wrong                                                                                                  |
| --- | --------------------------------------------------------------------------------------------------------------------------------- | ------- | -------------------------------------------------------------------------------------------------------------- |
| A1  | The boot-time guard should be gated on `not DEBUG` — local dev with empty env vars should not break                               | SEC-01  | If wrong (guard fires in dev), developers can't run locally; low risk, easy to diagnose                        |
| A2  | Render `generateValue` token has a fixed, known byte-length so a pre-length-check before `timingSafeEqual` is not a timing oracle | SEC-02  | If Render uses variable-length tokens, switch to constant-time HMAC; low risk                                  |
| A3  | Setting `OTLP_ENDPOINT=""` causes the telemetry push task to fail gracefully (caught Exception) rather than phone home            | SEC-03  | If the SDK does not fail gracefully on empty endpoint, metrics could still export; test with disabled endpoint |
| A4  | AGPL §13 compliance is satisfied by a `/source` endpoint + `NOTICE` file + a link from the auth footer                            | SEC-04  | Legal interpretation — not a code fact. Verify with counsel; the AGPL §13 text is the authoritative source     |
| A5  | `intake@plane.so` in `inbox-list-item.tsx:132` is an internal bot-detection check, not a user-visible URL                         | SEC-03  | If wrong, it would be visible to end users; inspect the rendered output                                        |

---

## Open Questions (RESOLVED — addressed via checkpoint:decision gates in plans 05-03, 05-04, 05-05)

1. **Source repo URL for AGPL §13 offer**
   - What we know: The offer must point to the "corresponding source" — the version being served
   - What's unclear: Does Bright-Byte have a public fork? Or does the offer point back to upstream `makeplane/plane`? If modifications are significant (they are — rebrand, de-monetization), the modified source should be published
   - Recommendation: Decide on a public fork URL before Phase 5 execution; use upstream as fallback

2. **Telemetry: delete beat task vs. disable via env var vs. set default=False**
   - What we know: All three approaches work
   - What's unclear: Whether the admin should ever be able to re-enable telemetry to a self-controlled collector
   - Recommendation: Change model default to `False`, add `OTLP_ENDPOINT` to `render.yaml` pointing to nowhere, leave the beat task in place (it will exit immediately with `is_telemetry_enabled=False`)

3. **Frontend `plane.so` URLs: replace or remove?**
   - What we know: There are ~16 occurrences; replacements require a real Bright-Byte support URL, docs URL, forum URL
   - What's unclear: Whether Bright-Byte has these resources yet
   - Recommendation: Remove links or replace with `#` / `mailto:support@bright-byte.example` for v1; real URLs when available

---

## Sources

### Primary (HIGH confidence — verified in this session against codebase)

- `apps/api/plane/settings/common.py` — SECRET_KEY, ALLOWED_HOSTS, CORS logic
- `apps/api/plane/settings/production.py` — production overrides
- `apps/live/src/lib/auth-middleware.ts` — string compare at line 38
- `apps/api/plane/bgtasks/event_tracking_task.py` — PostHog guard
- `apps/api/plane/license/bgtasks/telemetry_metrics.py` — OTLP telemetry task
- `apps/api/plane/utils/otlp_endpoints.py` — hardcoded `telemetry.plane.so` default
- `apps/api/plane/celery.py` — beat schedule with `push-instance-metrics`
- `.github/workflows/copyright-check.yml` — addlicense mechanics
- `COPYRIGHT.txt` — verbatim content
- `render.yaml` — current env var state
- `.planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md` — OUT-OF-PHASE telemetry rows

### Secondary (MEDIUM confidence)

- AGPL v3 Section 13 text [ASSUMED: legal interpretation based on training; verify with counsel]
- Node.js `crypto.timingSafeEqual` availability [VERIFIED: live test against Node 22.15.0]
- Django `ImproperlyConfigured` pattern [VERIFIED: in use at `plane/utils/host.py:7`]

---

## Metadata

**Confidence breakdown:**

- Standard stack (no new packages): HIGH — verified no new deps needed
- Exact file locations for all 4 requirements: HIGH — verified against source in this session
- AGPL §13 legal interpretation: MEDIUM/LOW — software engineering implementation is clear; legal sufficiency requires counsel
- Guard hook site: HIGH — Django `ImproperlyConfigured` pattern is already in use in the project

**Research date:** 2026-06-03
**Valid until:** 2026-07-03 (settings logic is stable; AGPL text does not change)
