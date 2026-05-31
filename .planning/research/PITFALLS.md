# Pitfalls Research

**Domain:** Brownfield rebrand + de-monetization + Render deployment of an AGPL-3.0 Django + Node monorepo (Plane CE)
**Researched:** 2026-06-01
**Confidence:** HIGH (codebase-grounded), MEDIUM on a few Render platform specifics (verified against current Render docs 2026)

This document is specific to the Bright-Byte PMP milestone and the Plane CE codebase at HEAD `3f57fefdb4`. Counts/paths verified against the repo. Generic advice is omitted.

---

## Critical Pitfalls

### Pitfall 1: Partial `@plane/*` → `@bright-byte/*` rename breaks the build mid-flight

**What goes wrong:**
The deep rename touches **19 `package.json` files** and **~1,799 `.ts`/`.tsx` files** that import `@plane/*`. A find-and-replace done incrementally (one package at a time, or only in `apps/`) leaves a graph where some packages publish under `@bright-byte/*` while consumers still import `@plane/*` (or vice versa). pnpm cannot resolve the workspace link, `tsdown`/`tsc` fail to find types, and Vite/React-Router builds fail with "Cannot find module @plane/...". Because there is **no CI test step** (only lint + typecheck per `CONCERNS.md`), a half-rename can pass local smoke checks and only blow up at `turbo run build`.

**Why it happens:**
The rename has many non-obvious sites beyond imports: the `name` field in each `package.json`, `dependencies`/`devDependencies` keys, `tsconfig` path aliases, `tsdown`/build config, `turbo.json` task filters, and string references in `.oxlintrc.json` / scripts. People rename imports but miss the package `name` fields, or rename `name` but not the dependency references in sibling packages.

**How to avoid:**
- Do it as **one atomic commit** across the whole repo, scripted — not hand-edited. The repo already ships `packages/codemods` (the only place with TS tests); use a codemod / `jscodeshift`-style transform plus a `pnpm` rename for `package.json` `name` and dependency keys.
- Rename in this order in a single pass: (1) every `package.json` `name`, (2) every `dependencies`/`devDependencies`/`peerDependencies` key, (3) all source imports, (4) `tsconfig*.json` `paths`, (5) `turbo.json`, `.oxlintrc.json`, any `vite.config.ts` aliases.
- Regenerate the lockfile in the same commit: `pnpm install` to rewrite `pnpm-lock.yaml`. A stale lockfile pointing at the old scope is a classic post-rename failure.
- Gate the commit on a **full clean build**: `pnpm install && turbo run build check:types` from a clean `node_modules`.

**Warning signs:**
- `pnpm install` warns about unresolved workspace dependencies.
- Typecheck errors clustered as "Cannot find module '@plane/...'" or "'@bright-byte/...' has no exported member".
- `git grep -c "@plane/"` is non-zero after the rename commit (should be 0 in source, excluding AGPL header comments and historical migration files).

**Phase to address:**
Package-rename phase (the deep `@plane/*` → `@bright-byte/*` workstream). This is the largest and riskiest workstream per `PROJECT.md`; isolate it so a failure doesn't block brand/deploy work.

---

### Pitfall 2: `tsconfig` path-alias and Next.js compat-shim breakage during rename

**What goes wrong:**
`apps/web/tsconfig.json:9` aliases `"@/plane-web/*": ["./ce/*"]` — note this alias contains the literal string `plane-web` but resolves to the edition seam directory `apps/web/ce/`, **not** the `@plane` npm scope. A naive global replace of `plane` → `bright-byte` will rewrite `@/plane-web` to `@/bright-byte-web` in **200+ files / 330+ import statements** (`CONCERNS.md` item 2) while leaving the alias key or the `./ce` directory mismatched — or worse, rewrite the alias and not the imports. Separately, the Next.js compat shims at `apps/web/app/compat/next/` are wired by Vite aliases (`next/link`, `next/navigation`, `next/script`) and are relied on by **260+ files**; touching Vite alias config during the rename can silently break shim resolution.

**Why it happens:**
"Plane" appears in three distinct namespaces that look similar but mean different things: the npm scope `@plane/*`, the edition alias `@/plane-web`, and user-facing brand text. A single blunt sed across all of them conflates them.

**How to avoid:**
- Treat the three namespaces as **separate rename targets** with separate, anchored patterns. The npm scope is exactly `@plane/` (slash-anchored). The edition alias is exactly `@/plane-web`. Decide explicitly whether `@/plane-web` is renamed at all — it is internal-only and renaming it adds risk with zero user-visible benefit; recommend **leaving `@/plane-web` as-is** or renaming it to a brand-neutral alias like `@/edition/*` in a separate commit.
- Never run an unanchored `plane` → `bright-byte` replace. Always match `@plane/`.
- Do not modify the `apps/web/app/compat/next/` shims or their Vite aliases during the scope rename — they are unrelated.

**Warning signs:**
- `apps/web` build errors referencing `./ce/*` or unresolved `@/plane-web`.
- `next/navigation` / `next/link` resolution failures (shim breakage).
- Diff shows changes inside `apps/web/app/compat/next/`.

**Phase to address:**
Package-rename phase, as an explicit sub-task with its own verification (build `apps/web` in isolation).

---

### Pitfall 3: AGPL-3.0 violation by stripping or rewriting copyright headers

**What goes wrong:**
`.github/workflows/copyright-check.yml` runs `addlicense -check -f COPYRIGHT.txt` on **every** `.py`, `.ts`, and `.tsx` file (excluding migrations, `*.config.ts`, `*.d.ts`). `COPYRIGHT.txt` reads `Copyright (c) 2023-present Plane Software, Inc. and contributors` / `SPDX-License-Identifier: AGPL-3.0-only`. During an enthusiastic rebrand it is tempting to replace "Plane Software, Inc." with "Bright-Byte" in the headers and `LICENSE.txt`. **This is an AGPL-3.0 violation** — you may not remove the original authors' copyright notices, and you cannot relicense Plane's code. Doing so also breaks the CI gate (header no longer matches `COPYRIGHT.txt`), failing every PR.

**Why it happens:**
Teams conflate "rebrand the product" with "claim authorship of the code." Under AGPL-3.0 these are entirely different: you may rebrand the running product and trademarks, but the source-level copyright/license notices of upstream must be preserved.

**How to avoid:**
- **Keep `LICENSE.txt` (AGPL-3.0) verbatim.** Keep the existing `Copyright (c) 2023-present Plane Software, Inc. and contributors` headers verbatim. Do **not** edit `COPYRIGHT.txt` to your name.
- You may **add** an additional copyright line for Bright-Byte modifications (e.g. `Copyright (c) 2026-present Bright-Byte`) *below* the existing one on files you materially change — but `addlicense` matches a header template, so adding lines may break the check. Safer: leave headers exactly as-is and record your modifications in a top-level `NOTICE`/`CHANGES` file rather than per-file.
- **Network-use clause (AGPL §13) applies.** Bright-Byte PMP serves clients "over a network," so the corresponding source — *including your modifications* — must be offered to those users (typically a visible "Source code" link to a repo or tarball matching the running version). Plan for a source-availability mechanism. Note Plane CE already ships a `robots.txt`-style disallow and instance changelog; AGPL source-offer is a separate obligation.
- Verify the AGPL header check still passes after the brand work: run `addlicense -check -f COPYRIGHT.txt $(git ls-files '*.py' '*.ts' '*.tsx')` locally before pushing.

**Warning signs:**
- `copyright-check.yml` failing on PRs ("missing license header").
- A diff that modifies `COPYRIGHT.txt`, `LICENSE.txt`, or the `Copyright (c) ... Plane Software` comment block.
- No mechanism in the deployed app to obtain source.

**Phase to address:**
Two phases. The **rebrand phase** must explicitly scope "do NOT touch copyright headers / LICENSE / COPYRIGHT.txt." A dedicated **AGPL compliance** task (can live in the deploy/hardening phase) must add the source-availability offer before serving real client data.

---

### Pitfall 4: Ungating "EE/Pro" features that don't exist in the CE codebase

**What goes wrong:**
"Unlock all Pro/EE features" assumes the feature code is present and merely flag-gated. For Plane CE it largely **is not**. The edition seam `apps/web/ce/` ships *stub* components that render upgrade prompts instead of the feature, e.g. `apps/web/ce/components/active-cycles/workspace-active-cycles-upgrade.tsx` (`WorkspaceActiveCyclesUpgrade`), `apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx` (`IssueEmbedUpgradeCard`), and `apps/web/ce/components/license/modal/upgrade-modal.tsx` whose own copy reads *"Dashboards, Workflows, Approvals, Time Management, and other superpowers…"*. The actual implementations of those EE features live in Plane's closed/cloud `plane-web` EE package — **they are not in this repo.** Removing the upgrade banner does not produce a working Dashboard/Workflow/Approval feature; it produces a blank or broken surface. Some "ungatable" features also call cloud-only endpoints (`app.plane.so`, license/prime servers) that don't exist self-hosted.

**Why it happens:**
The repo presents these as "locked" features (banners, modals), which reads as "flip a flag to unlock." In reality CE = the free feature set; the gated items are *absent code*, not disabled code.

**How to avoid:**
- **Reframe the requirement:** the goal is to remove the *upsell/billing surfaces* and ensure every feature **that exists in CE** is fully usable — not to materialize EE features. Update `PROJECT.md`'s "unlock all Pro/EE features" to "remove upsell surfaces; expose all CE-present features."
- Inventory each `*-upgrade*.tsx` / `*UpgradeCard` / `*UpgradeBanner` / `upgrade-modal` stub and classify: (a) feature fully present in CE behind a banner → safe to ungate; (b) feature is an EE stub with no CE implementation → **cannot ungate**, instead cleanly hide/remove the entry point so it doesn't dangle.
- Remove billing/upsell UI per `PROJECT.md` (`apps/web/core/components/license/*`, `workspace/billing/*`, `constants/plans.tsx`) but do **not** assume the modal's listed features become available.
- Confirm against the API: features needing instance `license_key`/`is_activated` (`apps/api/plane/license/...`) or external license servers must be treated as unavailable, not "unlocked."

**Warning signs:**
- After removing a banner, the surface renders empty, throws, or calls an unreachable host.
- Grep for cloud hosts in components you "unlocked" (`app.plane.so`, `prime`, `/billing`, `talk-to-sales`).
- Imports from a non-existent `@/plane-web` EE implementation (only the CE stub resolves).

**Phase to address:**
De-monetization / EE-ungating phase. Front-load the **inventory + classification** step before any removal so scope is realistic.

---

### Pitfall 5: Insecure-by-default Django settings deployed unconfigured (real client data exposure)

**What goes wrong:**
`apps/api/plane/settings/common.py` fails **open** on three settings (`CONCERNS.md` Security 1–3):
- `ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")` (line 76) → accepts any Host header.
- `CORS_ALLOW_CREDENTIALS = True` (line 163) **plus** `CORS_ALLOW_ALL_ORIGINS = True` fallback (line 171) when `CORS_ALLOWED_ORIGINS` is unset → any origin can make credentialed cross-site requests. This combination is the dangerous one.
- `SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())` (line 29) → if unset, a new key per process restart invalidates all sessions/signed tokens (users logged out on every Render deploy/cold start).

Additionally, `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` derive from `secure_origins`, which is `False` whenever the CORS fallback is hit (line 172) or any origin uses `http:` — so cookies may be sent insecurely.

**Why it happens:**
Render env vars are easy to forget; the app boots fine with the insecure defaults, so misconfiguration is invisible until exploited. Per-process `SECRET_KEY` regeneration looks like a flaky "users keep getting logged out" bug, not a config error.

**How to avoid:**
- In `render.yaml`, set **all** of `SECRET_KEY` (generated once, stored — use Render's `generateValue: true` so it's stable), `ALLOWED_HOSTS` (your exact Render hostname + custom domain), and `CORS_ALLOWED_ORIGINS` (exact web/admin/space origins, https only).
- Add a **boot-time guard**: refuse to start (or loudly warn) if `DEBUG=0` and any of `SECRET_KEY`/`ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS` is unset or `*`. Consider hardening `common.py` so the allow-all fallbacks only apply when `DEBUG=1`.
- Ensure `secure_origins` resolves `True` in prod (all origins `https:`), so `SESSION_COOKIE_SECURE`/`CSRF_COOKIE_SECURE` are enabled.

**Warning signs:**
- Users logged out after every deploy (ephemeral `SECRET_KEY`).
- `Invalid HTTP_HOST header` absent even from unknown hosts (ALLOWED_HOSTS=*).
- Browser sends cookies on cross-origin requests from arbitrary sites.

**Phase to address:**
Security-hardening phase, completed **before** the first real-client cutover. This is a hard gate on "serving real client data."

---

### Pitfall 6: Render has no managed object storage — attachments break or vanish

**What goes wrong:**
Plane stores all attachments/assets in S3-compatible object storage (`apps/api/plane/settings/storage.py`, `boto3` + `django-storages`). The local-dev path uses MinIO. **Render provides no managed object storage**, and Render's filesystem is **ephemeral** by default (lost on every deploy/restart). If the team deploys without provisioning an external S3 bucket — or tries to use a Render persistent disk as a stand-in — uploads either fail or disappear on the next deploy. A Render persistent disk also **prevents horizontal scaling** (single-instance only) and is not S3, so `S3Storage` won't use it anyway.

**Why it happens:**
Docker-compose ships MinIO as a service, creating the illusion that storage is "included." On Render there is no MinIO container; `PROJECT.md`/`CONCERNS` already flag this but it's easy to defer.

**How to avoid:**
- Provision an external S3-compatible bucket (AWS S3, Cloudflare R2, Backblaze B2, etc.) **before** first deploy. Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`, `AWS_REGION`, and `AWS_S3_ENDPOINT_URL` in `render.yaml`. Leave `USE_MINIO` unset/0.
- Note default `AWS_DEFAULT_ACL = "public-read"` (`common.py:291`) — for client data, configure the bucket/policy deliberately (presigned URLs are supported; `AWS_QUERYSTRING_AUTH = False`).
- CORS on the bucket must allow your web origins for presigned uploads.

**Warning signs:**
- Attachment uploads 500 or silently fail.
- Files present pre-deploy are gone post-deploy.
- `AWS_S3_ENDPOINT_URL` unset while expecting MinIO behavior.

**Phase to address:**
Deployment / infra-provisioning phase, as a prerequisite to first deploy.

---

### Pitfall 7: Multi-service Render topology — worker/beat/live deployed as wrong service types

**What goes wrong:**
The stack is **not** one process. Per `STACK.md` and `apps/api/bin/`, it needs: `api` (Gunicorn/uvicorn web), `worker` (`celery -A plane worker`, `docker-entrypoint-worker.sh`), `beat` (`celery -A plane beat`, `docker-entrypoint-beat.sh`), `live` (Express + Hocuspocus WebSocket), plus the `web`/`admin`/`space` frontends. Common Render mistakes: (a) running Celery worker/beat as a **Web Service** (Render kills it for not binding a port) instead of a **Background Worker**; (b) merging worker and beat into one process (causes duplicate/missed scheduled tasks — `email_notification_task` every 5 min, telemetry, cleanup); (c) putting the WebSocket `live` server behind a config that doesn't pass WS upgrades; (d) forgetting the DB `migrator` step so schema is never applied.

**Why it happens:**
docker-compose hides this as named services that "just work." Render requires each to be declared explicitly with the correct service type and start command.

**How to avoid:**
- In `render.yaml`: `api` = Web Service; `live` = Web Service (Render supports WebSockets on web services — verified); `worker` and `beat` = **separate Background Workers** with `docker-entrypoint-worker.sh` / `docker-entrypoint-beat.sh`; frontends = Static Sites or Web Services.
- Run migrations via a Render **preDeploy** command (or one-off job), not on every container boot of every replica.
- Keep `beat` as exactly **one** instance (it's a scheduler; multiple beats = duplicate jobs). `DatabaseScheduler` is used (`django_celery_beat`).
- Provision RabbitMQ (`AMQP_URL`) — Render has no managed RabbitMQ; either use Render Key Value/Redis as the Celery broker if supported by config, or an external CloudAMQP. Confirm broker choice early; `common.py` builds `CELERY_BROKER_URL` from `AMQP_URL` or RabbitMQ vars.

**Warning signs:**
- Render reports a service "failed to bind to port" (worker mis-typed as web).
- Scheduled emails/notifications fire twice or not at all (duplicate/no beat).
- WebSocket connections to `live` fail to upgrade (101) — collaborative pages don't sync.
- App 500s on missing tables (migrations never ran).

**Phase to address:**
Deployment phase — `render.yaml` blueprint design and service-type mapping.

---

### Pitfall 8: Missed brand references — "Plane" leaks into user-facing surfaces

**What goes wrong:**
Renaming the npm scope and visible logos misses many hardcoded "Plane" strings. Verified locations include **multiple** web manifests (`apps/web/manifest.json`, `apps/web/public/manifest.json`, `apps/web/public/site.webmanifest.json`, `apps/web/public/favicon/site.webmanifest`, plus `apps/admin/public/site.webmanifest.json`, `apps/space/public/site.webmanifest.json`, `apps/space/app/assets/favicon/site.webmanifest`), the i18n catalog (`packages/i18n/src/locales/en/*.json` — `common.json`, `auth.json`, `accessibility.json` alt text, etc.), the default email sender `EMAIL_FROM` = `Team Plane <team@mailer.plane.so>` (`apps/api/plane/license/utils/instance_value.py:56`), upgrade-modal copy referencing "Plane Pro" (`apps/web/ce/components/.../issue-embed-upgrade-card.tsx`), telemetry default `https://telemetry.plane.so` (`apps/api/plane/utils/otlp_endpoints.py`), and the `User-Agent: "Autopilot"` / Mozilla strings in webhook/link tasks. Page `<title>`, OG/meta tags, PWA icons, and generated PDFs (`@react-pdf/renderer`) each have their own copies.

**Why it happens:**
Brand text is scattered across JSON manifests, i18n files, Python defaults, and React components — no single source of truth. The deep package rename feels like "the rebrand," so visible-string sweeps get under-scoped.

**How to avoid:**
- Treat user-facing brand as a **separate, checklist-driven sweep** from the package rename. Grep the whole tree case-insensitively for `plane` and triage every hit into: keep (AGPL header / npm scope already handled / legitimate non-brand), or rename (user-visible).
- Specifically cover: all `*manifest*` / `*.webmanifest*` JSON, all `packages/i18n/src/locales/*/*.json` (every locale, not just `en`), `EMAIL_FROM` default and email templates (`apps/api/.../templates`), page `<title>`/meta in `apps/web/app/root.tsx` & `layout.tsx`, OG tags, favicon/PWA icon assets, PDF export headers/footers, and override `OTLP_ENDPOINT`/disable telemetry so you don't phone home to `telemetry.plane.so`.
- Set `EMAIL_FROM` env var so invite/notification emails come from a Bright-Byte address.

**Warning signs:**
- Installed PWA shows "Plane" name/icon.
- Invite emails arrive from `team@mailer.plane.so`.
- Browser tab title or OG preview says "Plane."
- Exported PDFs/CSVs carry Plane branding.

**Phase to address:**
Rebrand phase (user-facing surfaces), with a final verification checklist before client demo.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Global unanchored `plane`→`bright-byte` sed across all files | Fast, one command | Corrupts `@/plane-web` alias, AGPL headers, and unrelated strings; near-certain build break | **Never** — always anchor to `@plane/` and exclude header/LICENSE files |
| Editing `COPYRIGHT.txt`/headers to "Bright-Byte" | Feels like a complete rebrand | AGPL-3.0 violation + CI gate fails on every PR | **Never** — preserve upstream headers; record changes in NOTICE |
| Renaming the internal `@/plane-web` edition alias too | "Total" rebrand | 200+/330+ import churn, zero user benefit, high break risk | Only as a separate, optional commit after build is green; recommend skipping |
| Using a Render persistent disk for attachments instead of S3 | Avoids provisioning a bucket | Single-instance lock (no scaling), still not S3 so `S3Storage` ignores it, data risk | **Never** for attachments — use external S3 |
| Free-tier Render services for the shared client instance | $0 cost | Sleeps after 15 min (30–60s cold start), 1GB Postgres that expires in 30 days with no backups, logs-out users | Only for throwaway preview/testing, never for real clients |
| Deferring SECRET_KEY/ALLOWED_HOSTS/CORS env config | Faster first deploy | Users logged out each deploy; credentialed CORS open to any origin | **Never** before real client data |
| Removing upgrade banners without checking the feature exists in CE | Looks "unlocked" fast | Blank/broken surfaces, calls to non-existent cloud endpoints | **Never** — classify each stub first |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| S3 object storage | Assuming MinIO/disk is available on Render; leaving `AWS_DEFAULT_ACL=public-read` for client data | Provision external S3/R2/B2; set bucket CORS + deliberate ACL; rely on presigned URLs |
| Celery broker (RabbitMQ) | Expecting Render-managed RabbitMQ (none exists) | Provision external CloudAMQP (`AMQP_URL`) or confirm Redis-broker support before deploy |
| Redis (Render Key Value) | Forgetting `rediss://` triggers SSL path (`common.py:225`) and TLS cert handling | Use the `rediss://` URL Render provides; `REDIS_SSL` auto-detects and sets `ssl_cert_reqs:False` |
| SMTP | No SMTP provisioned → invites/magic-links/notifications silently never send | Provision an SMTP provider; set `ENABLE_SMTP` + `EMAIL_*`; set `EMAIL_FROM` to a Bright-Byte address |
| Live server (Hocuspocus) auth | Leaving `live-server-secret-key` compare as `!==` (`apps/live/src/lib/auth-middleware.ts:38`, TODO "Move to hmac"), non-constant-time | Use `crypto.timingSafeEqual`; set a strong `LIVE_SERVER_SECRET_KEY`; ensure WS upgrades pass through Render |
| OTLP telemetry | Phoning home to default `https://telemetry.plane.so` | Set `OTLP_ENDPOINT` to your own collector or disable the `push_instance_metrics` beat task |
| OAuth providers | Assuming they work out of the box | All off by default; configured via `InstanceConfiguration` (admin app), not just env — set redirect URIs to the Render domain |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Free/low-tier Render Postgres connection exhaustion | `FATAL: too many connections`, intermittent 500s | Gunicorn/uvicorn worker count × DB conns must stay under the plan limit; add `CONN_MAX_AGE`/pgbouncer; size workers conservatively | When api + worker + beat + live all open pools concurrently (multi-service stack multiplies connections) |
| Cold starts on sleeping services | First request after idle takes 30–60s; WebSocket/live reconnect storms | Use paid (always-on) tier for any client-serving service; never free tier for `api`/`live` | Immediately for free-tier; whenever traffic is bursty |
| Synchronous-heavy `issue_activities_task.py` (1604 lines) | Worker lag, delayed notifications under load | Watch worker queue depth; consider splitting the task | At higher issue-activity volume across many client workspaces |
| Oversized issue views/stores (`issue.py` 2542 lines, `base-issues.store.ts` 1965) | Slow parse/load, hard to change safely | Don't refactor during this milestone; just avoid regressions | Maintenance burden, not runtime — out of scope here |
| Single shared instance for all clients | One client's load/incident affects all | Monitor per-workspace; size DB/services for aggregate load | When client count grows (single-instance model is a `PROJECT.md` decision) |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Deploy with `ALLOWED_HOSTS=*` (default) | Host-header injection, cache poisoning | Set exact Render hostname(s) in `render.yaml` |
| `CORS_ALLOW_ALL_ORIGINS=True` + `CORS_ALLOW_CREDENTIALS=True` (fallback hit) | Any site can make credentialed requests as the user | Always set `CORS_ALLOWED_ORIGINS`; harden fallback to DEBUG-only |
| Ephemeral `SECRET_KEY` | Session/token invalidation each restart; signed-value forgery if predictable | Set a stable `SECRET_KEY` (Render `generateValue`), never rely on default |
| Non-constant-time live-server secret compare (`auth-middleware.ts:38`) | Timing side-channel on `LIVE_SERVER_SECRET_KEY` | Replace `!==` with `crypto.timingSafeEqual` |
| `print()` in 13 backend files (some exception paths) | Leaks detail to stdout/Render logs; bypasses structured logging | Replace with `@plane/logger`/Django logging before serving real data |
| Cookies non-secure when `secure_origins=False` | Session/CSRF cookies over plain HTTP | Ensure all prod origins are `https:` so `secure_origins` resolves True |
| AGPL source not offered to network users | License non-compliance (AGPL §13) | Add a "Source code" link/offer matching the deployed version |
| Re-confirm suppressed `CVE-2026-30242` on dep bumps (`.trivyignore`) | Re-introducing a real SSRF if mitigation regresses | Re-validate the `.trivyignore` rationale whenever bumping the webhook/url deps |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Removing a billing banner but leaving its dead button/menu entry | Clients click a "feature" that does nothing/errors | Remove the entry point entirely when the EE feature isn't in CE |
| Renaming AI assistant to "Byte" only in labels, not prompts/tooltips/system text | Inconsistent brand; "Plane AI" leaks in responses | Sweep labels, prompts, tooltips, component names, and any model system prompt |
| Route-coupled UI state breaking after brand/route renames (`CONCERNS.md` Bugs 2) | Empty states / mobile header misbehave | Don't rename route param strings during rebrand; brand is presentational only |
| Logged-out-on-deploy (ephemeral SECRET_KEY) | Clients re-login after every release | Stable `SECRET_KEY` (also a security item) |
| Cold-start latency on first daily visit | "App is broken/slow" perception | Always-on paid tier for client-facing services |

## "Looks Done But Isn't" Checklist

- [ ] **Package rename:** `git grep -c "@plane/"` returns 0 in source (excluding AGPL header comments) AND `pnpm install && turbo run build check:types` passes from clean `node_modules`.
- [ ] **Lockfile:** `pnpm-lock.yaml` regenerated in the rename commit — no stale `@plane/*` resolutions.
- [ ] **Brand sweep:** every `*manifest*`/`*.webmanifest*`, every locale under `packages/i18n/src/locales/*`, `EMAIL_FROM`, page `<title>`/OG/meta, favicon/PWA icons, and PDF exports updated — not just `en` and not just the web app.
- [ ] **AGPL:** `LICENSE.txt`, `COPYRIGHT.txt`, and per-file headers unchanged; `copyright-check.yml` passes; a source-availability offer is live in the deployed product.
- [ ] **EE ungating:** each `*-upgrade*`/`UpgradeBanner`/`upgrade-modal` stub classified; no removed banner leaves a blank/erroring surface or a call to a cloud-only host.
- [ ] **Telemetry:** `OTLP_ENDPOINT` overridden or `push_instance_metrics` disabled — not phoning home to `telemetry.plane.so`.
- [ ] **Render services:** worker/beat are Background Workers (not Web Services); exactly one beat; `live` passes WebSocket upgrades; migrations run via preDeploy.
- [ ] **Storage:** external S3 bucket provisioned, CORS set, ACL deliberate; `USE_MINIO` off; uploads survive a redeploy.
- [ ] **Security env:** `SECRET_KEY` (stable), `ALLOWED_HOSTS` (exact), `CORS_ALLOWED_ORIGINS` (exact, https) all set; `secure_origins` resolves True.
- [ ] **Email:** SMTP provisioned and a test invite actually arrives from a Bright-Byte address.
- [ ] **Live auth:** secret compare is constant-time; `LIVE_SERVER_SECRET_KEY` set strong.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Partial/broken rename committed | MEDIUM | Revert the rename commit; redo as a single scripted atomic commit; gate on clean full build |
| AGPL headers stripped/edited | LOW (if caught pre-release) | `git revert`/restore `COPYRIGHT.txt`+headers; re-run `addlicense -check`; add NOTICE for your changes instead |
| Ungated a non-existent EE feature → broken surface | LOW–MEDIUM | Re-hide the entry point; restore the CE stub or remove the menu item cleanly |
| Deployed with insecure defaults | LOW (config) but HIGH if data exposed | Set env vars immediately; rotate `SECRET_KEY` (logs everyone out); audit access logs for Host/CORS abuse |
| Attachments lost on Render redeploy | HIGH (data loss) | Provision S3 before relying on uploads; lost ephemeral files are unrecoverable — no recovery, only prevention |
| Duplicate scheduled emails (two beats) | MEDIUM | Scale beat to exactly 1; deduplicate any double-sent notifications; apologize to clients |
| Postgres connection exhaustion | MEDIUM | Lower worker counts, add pgbouncer/`CONN_MAX_AGE`, upgrade DB plan |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Partial `@plane/*` rename build break | Package-rename phase | `git grep -c "@plane/"` = 0 in source; clean `turbo run build check:types` |
| tsconfig alias / compat-shim breakage | Package-rename phase | `apps/web` builds in isolation; `@/plane-web`→`./ce` resolves; no diffs in `app/compat/next` |
| AGPL header/LICENSE violation | Rebrand phase (don't touch) + Deploy/hardening (source offer) | `copyright-check.yml` green; source-availability link live |
| Ungating non-existent EE features | De-monetization / EE phase | Each stub classified; no dangling/blank surfaces; no cloud-host calls |
| Insecure Django defaults | Security-hardening phase (gate before client data) | `SECRET_KEY`/`ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS` set; `secure_origins`=True |
| No managed object storage | Deployment / infra-provisioning phase | Upload survives a redeploy; bucket CORS/ACL correct |
| Wrong Render service types (worker/beat/live) | Deployment phase (`render.yaml`) | Workers run as Background Workers; 1 beat; WS upgrades succeed; migrations applied |
| Missed brand references | Rebrand phase (user-facing) | Brand checklist sweep across manifests/i18n/email/PDF/telemetry |
| `print()` + non-constant-time compare | Security-hardening phase | No `print()` in backend paths serving data; `timingSafeEqual` in live auth |
| Cold start / free-tier limits | Deployment phase | Client-facing services on always-on paid tier; Postgres plan with backups |

## Sources

- Codebase at HEAD `3f57fefdb4`: `apps/api/plane/settings/common.py`, `apps/live/src/lib/auth-middleware.ts`, `apps/web/tsconfig.json`, `apps/web/ce/components/**`, `apps/api/plane/license/**`, `apps/api/bin/docker-entrypoint-{worker,beat}.sh`, `apps/api/plane/utils/otlp_endpoints.py`, `apps/api/plane/license/utils/instance_value.py`, `.github/workflows/copyright-check.yml`, `COPYRIGHT.txt`, `LICENSE.txt`
- `.planning/PROJECT.md`, `.planning/codebase/CONCERNS.md`, `.planning/codebase/STACK.md`, `.planning/codebase/INTEGRATIONS.md`
- Render docs (verified 2026): [Deploy for Free](https://render.com/docs/free), [Persistent Disks](https://render.com/docs/disks), [Web Services](https://render.com/docs/web-services)
- AGPL-3.0 §13 network-use clause (GNU Affero General Public License, `LICENSE.txt`)
- `addlicense` (google/addlicense) header-check semantics

---
*Pitfalls research for: AGPL brownfield rebrand + de-monetization + Render deploy (Plane CE)*
*Researched: 2026-06-01*
