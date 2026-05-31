# Project Research Summary

**Project:** Bright-Byte PMP
**Domain:** Brownfield white-label rebrand + de-monetization + Render deployment of an AGPL-3.0 Django + Node monorepo (Plane CE)
**Researched:** 2026-06-01
**Confidence:** HIGH (codebase-grounded; every claim cites a real path or an official Render/Celery doc)

## Executive Summary

Bright-Byte PMP is not a greenfield product — it is a **brownfield transformation** of the open-source Plane (Community Edition) monorepo into a white-labeled, de-monetized, self-hosted PM platform we operate for clients on Render. The work decomposes into four orthogonal workstreams: (A) a user-facing **rebrand** of every "Plane" surface, (B) a deep **`@plane/*` → `@bright-byte/*` package-scope rename**, (C) **de-monetization / EE-ungating**, and (D) **Render deployment + security hardening**. Plane's PM feature set is inherited as-is; the research deliberately maps only the *change surfaces*, not Plane's internals.

The single most consequential reframing from research: **"unlock all Pro/EE features" is a misnomer.** There is **zero runtime license enforcement** in CE (searches for `useFlag`/`FeatureFlag`/`E_FEATURE_FLAGS` returned no hits). EE features are **absent code** — CE ships *stub upsell components* (`*-upgrade*.tsx`, `upgrade-modal.tsx`) where the real implementation lives in a `plane-web` EE package we do not possess. Removing an upsell banner does **not** produce a working Dashboard/Workflow/Approval; it produces a blank or broken surface. So the real work is: **remove upsell chrome + expose all CE-present features, after classifying each stub** as (a) feature present behind a banner → ungate, or (b) EE-only stub → cleanly remove the entry point so nothing dangles. The recommended approach is to run the rename as **one atomic, scripted, build-gated commit** (via the existing `packages/codemods` jscodeshift harness — ~1,800 files / ~5,000 import sites), keep the user-facing rebrand as a separate checklist-driven sweep, and treat deployment as its own phase with hard security gates.

The dominant risks are: a **partial rename** (a half-renamed `workspace:*` monorepo will not `pnpm install` or build — and there is no CI test step to catch it); **AGPL-3.0 non-compliance** (copyright headers and `LICENSE.txt` must stay verbatim, CI enforces this via `addlicense`, and a §13 network-source-availability offer is mandatory before serving clients); the **Celery broker being AMQP-only in code** while Render has no managed RabbitMQ (a blocking deploy decision); the **build-time baking of `VITE_*` URLs** (domain changes require a rebuild, not an env edit); and **insecure-by-default Django settings** (`ALLOWED_HOSTS="*"`, CORS allow-all fallback, ephemeral `SECRET_KEY`) that must be hardened before any real client data is served.

## Key Findings

### Recommended Stack

The entire multi-service stack maps onto **one `render.yaml` Blueprint** built from the **existing Dockerfiles** — no rewrite. Render provides the compute (Web Services, Background Workers, Static Sites) and two managed datastores (Postgres, Key Value/Valkey), but has **three gaps Render does not fill**: object storage, a Celery broker (no managed RabbitMQ), and SMTP. See `.planning/research/STACK.md`.

**Core technologies:**
- **Render Blueprint (`render.yaml`)**: single IaC file defining all 8 services + 2 datastores — reproducible, version-controlled deploy of the whole stack.
- **Render Postgres 17 (paid `pro-4gb`+)** + **Render Key Value / Valkey 8 (paid, disk-persistent)**: primary DB + cache/sessions/Celery-result-backend/Hocuspocus sync. Never free tier (free PG expires in 30 days, no backups).
- **Cloudflare R2** (object storage): Render has no managed object store; R2 gives zero egress + full S3 presign API for Plane's attachments.
- **Celery broker — DECISION REQUIRED**: broker is AMQP-only in code (`apps/api/plane/settings/common.py:309`). Options: (a) CloudAMQP managed RabbitMQ = zero code change; (b) self-run RabbitMQ private service; (c) **~3-line code change so `AMQP_URL=redis://…` reuses Render Key Value** (Celery natively supports Redis brokers) — recommended long-term, requires `maxmemory-policy noeviction`.
- **Resend (or Brevo)** SMTP: invites/magic-link/notifications fail silently without it.
- **Service mapping**: `api`=Web; `worker`/`beat`=Background Workers (beat = exactly 1 instance); `live`=Web (WebSocket); `space`=Web (SSR Node); `web`/`admin`=Static Sites; `migrator`=preDeploy command. The Caddy `proxy` is **dropped** (Render routes) OR replicated as a single Web Service to preserve same-origin cookies (topology decision).

### Expected Features

This is a white-label of one upstream product, so "features" = the *change surfaces* of the rebrand. See `.planning/research/FEATURES.md`. **Critical mechanism:** gating is UI-only (CE no-op implementations behind `@/plane-web/*`, hard-coded upsell banners, the "Community" edition badge → upgrade modal). Most "Pro" PM features already ship fully functional in CE; the locked experience is mostly upsell chrome.

**Must have (table stakes — credible white-label):**
- Web/Admin/Space brand metadata (`root.tsx` `APP_TITLE`, OG/twitter/meta) + brand constants (`packages/constants/src/metadata.ts`, `endpoints.ts`) — the obvious tells.
- Favicons / app icons / PWA icons / logos swapped (client-provided assets) + PWA manifests (multiple `*.webmanifest` files).
- English i18n rebrand (`packages/i18n/src/locales/en/*`, ~130 "Plane" hits) + email templates (`apps/api/templates/**`).
- Remove the entire billing/license upsell cluster (`license/**`, `ce/.../license/**`, `workspace/billing/**`, billing route+page, edition-badge trigger, in-component upgrade banners, `plans.tsx` + `payment.ts`/`subscription.ts`).
- AI assistant → **"Byte"** (user-visible labels/icons; `ai.ts`, `pi_chat` key, `PiChatLogo`, popover placeholders).

**Should have (polish):**
- All 18 non-English locales rebranded; internal "Pi"→"Byte" code rename; theme/brand color.

**Defer (v2+ / separate milestone):**
- The `@plane/*` → `@bright-byte/*` deep package rename is treated by FEATURES.md as a separable workstream from the *brand* (different blast radius) — but PROJECT.md scopes it into **this** milestone, so it becomes its own phase here.

**Anti-features (do NOT touch):** issue/notification "subscriptions" (core PM, not billing — naming collision with `subscription.ts` which IS billing); AGPL copyright headers; the `@/plane-web/*` edition alias; the AI GPT backend (label-only rename); the `apps/api/plane/license/` instance-registration machinery (not paid-plan billing).

### Architecture Approach

The architecture of the *change* is three workstreams with a strict dependency order. See `.planning/research/ARCHITECTURE.md`. **Workstream A (scope rename) must be one atomic commit** — a `workspace:*` monorepo with a pnpm catalog cannot be half-renamed. **Workstream B (EE/billing removal) depends on A landing first** and uses an "ungate-then-prune" order (only ~9 `core` files directly import the billing/license surface). **Workstream C (Render) is independent** of A/B but deploys only after A is green.

**Major components:**
1. **Scope-rename codemod** (`packages/codemods/rename-scope.ts`) — a NEW jscodeshift transform alongside the two existing ones, matching the `@plane/` scope boundary *only* (never `@/plane-web` / `@/plane-live`). Non-source surfaces (package.json names/deps, tsconfig `extends`, CSS `@import`) handled by scripted AST-aware replace; lockfile regenerated via `pnpm install`, never hand-edited.
2. **Edition seam (`ce/` overlay)** — EE is gated through `@/plane-web/*`→`./ce/*`; ungate by replacing stub bodies with "unlocked"/no-op while keeping the `index.ts` export surface intact, then prune dead consumers last.
3. **Render service topology** — 8 services + Postgres + Key Value + external R2 + external SMTP, with `migrator` (preDeploy) blocking all app boots (`wait_for_migrations`), and Key-Value-as-broker (`AMQP_URL=redis://` + noeviction) as the recommended way to eliminate RabbitMQ.

**Key patterns:** atomic rename gated by the existing turbo graph (`build`/`check:types` both `dependsOn: ["^build"]`); verification gate = green `pnpm build && pnpm check:types && pnpm check:lint` + empty `@plane/` grep; AST codemod over blind `sed`. **Critical clarifications from architecture:** the Python backend has **0 `@plane/` references** (rename is JS/TS only; leave Python package `plane` as-is); the real file count is **1,805 files / 5,003 import sites** (not the ~1,274 estimate in PROJECT.md).

### Critical Pitfalls

From `.planning/research/PITFALLS.md` (8 critical pitfalls; top items by leverage):

1. **Partial `@plane/*` rename breaks the build** — there is no CI test step, so a half-rename passes local smoke checks and only blows up at `turbo run build`. Avoid: one atomic scripted commit (names → dep keys → imports → tsconfig paths → turbo/oxlint), regenerate lockfile in the same commit, gate on clean full build. Verify: `git grep -c "@plane/"` = 0 in source.
2. **AGPL-3.0 violation by editing copyright headers / LICENSE** — `copyright-check.yml` runs `addlicense` on every `.py/.ts/.tsx`; headers say "Plane Software, Inc." and must stay **verbatim**. Rebranding the product ≠ claiming authorship. Avoid: never edit `COPYRIGHT.txt`/`LICENSE.txt`/headers; record changes in a `NOTICE` file; add a **§13 source-availability offer** in the deployed app before serving clients.
3. **Ungating EE features that don't exist in CE** — removing a banner yields a blank/broken surface or a call to a cloud-only host (`app.plane.so`). Avoid: front-load an **inventory + classification** step; ungate present features, cleanly remove dangling EE entry points.
4. **Insecure-by-default Django settings** (`ALLOWED_HOSTS="*"`, `CORS_ALLOW_ALL_ORIGINS` + `CORS_ALLOW_CREDENTIALS` fallback, ephemeral `SECRET_KEY`) — hard gate before real client data. Avoid: set stable `SECRET_KEY` (`generateValue`), exact `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS` (https only); add a boot-time guard.
5. **Render has no managed object storage / RabbitMQ; wrong service types** — provision external R2 before first deploy (Render FS is ephemeral); resolve the broker decision; `worker`/`beat` must be Background Workers (not Web Services), exactly one `beat`; build-time `VITE_*` baking means domain changes need a rebuild; missed brand strings leak "Plane" into manifests/i18n/email-`EMAIL_FROM`/PDF/telemetry.

## Implications for Roadmap

Based on the dependency structure across all four files, the suggested phase order is below. The hard ordering constraint: **the package rename (Phase 2) must precede EE removal (Phase 3)**, and **deploy (Phase 5) must follow a green rename**; the rebrand (Phase 1) and rename (Phase 2) are best kept separate (different blast radius). Security hardening is a **gate**, not optional.

### Phase 1: User-Facing Rebrand
**Rationale:** Independent of the risky rename; immediately demonstrable; low build risk (strings/assets, not tooling). Keeping it separate means the brand can be reviewed/shipped without waiting on the atomic rename.
**Delivers:** Bright-Byte PMP brand across web/admin/space metadata, manifests, favicons/logos/icons, English i18n, email templates, and AI assistant labels → "Byte".
**Addresses:** All table-stakes rebrand features from FEATURES.md.
**Avoids:** Pitfall 8 (missed brand leaks — run the full case-insensitive `plane` sweep across manifests/i18n/`EMAIL_FROM`/PDF/telemetry) and Pitfall 3 (do **not** touch AGPL headers).

### Phase 2: `@plane/*` → `@bright-byte/*` Package-Scope Rename (atomic)
**Rationale:** The largest, riskiest workstream; cannot be half-done in a `workspace:*` monorepo. Single phase, internally sequenced. Must land green before any deploy.
**Delivers:** Full scope rename across 15 package names, 19 package.json dep sets, ~1,805 files / 5,003 imports, tsconfig `extends`, CSS `@import`, regenerated lockfile.
**Uses:** The existing `packages/codemods` jscodeshift harness (NEW `rename-scope.ts` transform + Vitest fixtures); scripted replace for non-source surfaces.
**Implements:** ARCHITECTURE.md Workstream A. **DoD:** green `pnpm build && pnpm check:types && pnpm check:lint` + empty `@plane/` grep.
**Avoids:** Pitfalls 1 & 2 (partial rename; corrupting `@/plane-web`/`@/plane-live` aliases or the Next.js compat shims — never run unanchored `plane`→`bright-byte`; leave Python `plane` package untouched).

### Phase 3: De-monetization + EE Ungating (inventory-first)
**Rationale:** Depends on Phase 2 being green (imports must resolve). Small blast radius (~9 direct consumers). Must be inventory-led to avoid blank surfaces.
**Delivers:** Removal of billing/license upsell cluster, plan/pricing data, edition-badge trigger, in-component banners; every CE-present feature exposed; every EE-only stub entry point cleanly removed.
**Addresses:** "Remove all billing/license upsell" + reframed "unlock all features" from FEATURES.md.
**Avoids:** Pitfall 4 (classify each `*-upgrade*`/`upgrade-modal` stub first; ungate-then-prune; no dangling buttons or cloud-host calls).

### Phase 4: Render Topology + Infra Provisioning (`render.yaml`)
**Rationale:** Independent build work that can proceed in parallel with Phases 1–3, but deploys only after Phase 2 is green. Resolves the blocking broker decision.
**Delivers:** `render.yaml` blueprint (8 services + Postgres + Key Value), external R2 bucket, SMTP provider, broker decision (CloudAMQP vs Redis-broker code change), proxy topology decision (replicate-Caddy vs subdomain-per-service), correct `VITE_*` build-args.
**Uses:** Existing Dockerfiles verbatim; STACK.md `render.yaml` skeleton.
**Avoids:** Pitfalls 5/6/7 (no managed object storage/RabbitMQ; wrong service types; ephemeral FS; build-time `VITE_*` baking; beat = 1).

### Phase 5: Security Hardening + AGPL Compliance (hard gate before client cutover)
**Rationale:** A non-negotiable gate the moment real client data is served. Pulls together the security items scattered across PITFALLS.md.
**Delivers:** Stable `SECRET_KEY`, exact `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS` (https), `secure_origins`=True, boot-time config guard; constant-time live-server secret compare; `print()` removal in backend data paths; telemetry repointed/disabled; **§13 source-availability offer live**.
**Avoids:** Pitfall 4 (insecure defaults) + Pitfall 3's compliance half (AGPL network-use clause).

### Phase Ordering Rationale

- **Rename (2) before EE removal (3):** EE removal edits files via `@/plane-web/*`; doing it pre-rename means redoing it, and the atomic rename must not be polluted with content edits.
- **Rebrand (1) separated from rename (2):** strings/assets vs build tooling — different risk profiles; mixing makes the shippable brand hostage to the risky rename.
- **Deploy (4) parallelizable but gated on a green rename (2):** Render images build the renamed packages.
- **Hardening (5) last and load-bearing:** it is the gate on "serving real client data," not a nice-to-have.

### Research Flags

Phases likely needing deeper research during planning (`/gsd:plan-phase --research-phase <N>`):
- **Phase 3 (EE ungating):** the per-stub inventory/classification is the actual unknown — which `*-upgrade*` components have a CE implementation vs are EE-only. Needs a discovery pass.
- **Phase 4 (Render deploy):** two open decisions — **broker** (CloudAMQP vs the 3-line Redis-broker change) and **proxy topology** (replicate Caddy for same-origin cookies vs subdomain-per-service + CORS). Both ripple into `VITE_*` values and OAuth redirect URIs. Verify R2 presign/ETag parity and exact Render `routes` behavior.

Phases with standard patterns (skip research-phase):
- **Phase 1 (rebrand):** mechanical, checklist-driven; all surfaces enumerated in FEATURES.md/PITFALLS.md.
- **Phase 2 (rename):** procedure fully specified in ARCHITECTURE.md (ordered steps + verification gate); execution risk is high but the *approach* is settled.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Render specifics verified vs official docs; broker-is-AMQP-only verified in-repo. R2 ETag parity + exact Render routing are MEDIUM. |
| Features | HIGH | Every surface cites a real path; the "no runtime license enforcement" finding rests on HIGH-confidence negative searches. |
| Architecture | HIGH | Rename mechanics + EE seam + file counts (1,805/5,003) verified against the tree; Render/Celery topology vs official docs. |
| Pitfalls | HIGH | Codebase-grounded at HEAD `3f57fefdb4`; a few Render platform specifics are MEDIUM. |

**Overall confidence:** HIGH

### Gaps to Address

- **Broker decision (Phase 4):** choose CloudAMQP (zero code) vs the ~3-line Redis-broker change (no extra infra, needs `noeviction`). Decide before deploy; it is the single biggest blocker.
- **Proxy / origin topology (Phase 4):** same-origin (replicate Caddy) vs subdomain-per-service (must solve cross-origin cookies/CORS). Determines every `VITE_*_BASE_URL`/`*_BASE_PATH` and OAuth redirect URI. Decide before building frontends (URLs are baked at build time).
- **EE stub classification (Phase 3):** which gated features are CE-present vs absent EE code is not yet enumerated per-component — needs a discovery pass before removal.
- **R2 ↔ S3 parity (Phase 4):** verify presigned PUT/GET and multipart-ETag behavior in testing (low risk given 5 MB default upload limit).
- **AGPL header check vs added attribution:** `addlicense` matches a template, so adding a Bright-Byte line per file may break CI — prefer a top-level `NOTICE`/`CHANGES` file.

## Sources

### Primary (HIGH confidence)
- Direct reads of the Bright-Byte-PMP repo at HEAD `3f57fefdb4`: `apps/api/plane/settings/common.py` (broker AMQP-only; insecure defaults), `apps/web/tsconfig.json` (`@/plane-web` seam), `packages/constants/src/{metadata,endpoints,payment,subscription}.ts`, `apps/web/core/components/license/**`, `apps/web/ce/**`, `packages/codemods/**`, `apps/*/Dockerfile.*`, `apps/api/bin/docker-entrypoint-*.sh`, `apps/proxy/Caddyfile.ce`, `.github/workflows/copyright-check.yml`, `COPYRIGHT.txt`, `LICENSE.txt`.
- Negative searches (HIGH-confidence absence): `useFlag`/`FeatureFlag`/`getFeatureFlag`/`E_FEATURE_FLAGS`/`WithFeatureFlagHOC` → 0 hits; `@plane/` in `apps/api/*.py` → 0 hits.
- `.planning/PROJECT.md` + `.planning/codebase/{STACK,ARCHITECTURE,STRUCTURE,CONVENTIONS,CONCERNS,INTEGRATIONS}.md`.
- [Render Blueprint YAML Reference](https://render.com/docs/blueprint-spec), [Key Value](https://render.com/docs/key-value), [Postgres](https://render.com/docs/postgresql-creating-connecting), [WebSockets](https://render.com/docs/websocket), [Monorepo](https://render.com/docs/monorepo-support), [free-PG-expiry changelog](https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90).
- [Celery Redis broker/backend docs](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html) (eviction/visibility caveats); AGPL-3.0 §13.

### Secondary (MEDIUM confidence)
- [CloudAMQP plans](https://www.cloudamqp.com/plans.html); object-storage comparisons (R2/S3/B2 egress + presign + ETag caveat); SMTP comparisons (Resend/Brevo/Postmark/SES); [Plane self-hosting guide](https://deepwiki.com/makeplane/plane/6.4-self-hosting-guide).

### Tertiary (LOW confidence)
- None load-bearing; R2↔S3 presign/multipart-ETag parity to be confirmed in deploy-phase testing.

---
*Research completed: 2026-06-01*
*Ready for roadmap: yes*
