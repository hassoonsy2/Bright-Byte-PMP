# Roadmap: Bright-Byte PMP

## Overview

Bright-Byte PMP transforms the open-source Plane (Community Edition) monorepo into a white-labeled, de-monetized, self-hosted project-management platform we operate for clients on Render. The journey runs across five phases derived from the work's natural dependency structure: first we make the product _look_ like Bright-Byte (user-facing rebrand — low build risk, immediately demonstrable), then we make it _named_ like Bright-Byte internally (the atomic `@plane/*` → `@bright-byte/*` package-scope rename — the single riskiest workstream, which must land green before anything downstream). With imports resolving under the new scope, we strip every billing/upsell surface so CE's already-working features stand free (de-monetization, inventory-first). In parallel we stand up the Render topology and external infra (R2, SMTP, broker), deploying only once the rename is green. Finally, security hardening + the AGPL §13 source-availability offer form the hard gate that must close before we serve any real client data.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: User-Facing Rebrand** - Every "Plane" surface (metadata, manifests, logos, i18n, emails) reads "Bright-Byte PMP" and the AI assistant shows as "Byte"
- [x] **Phase 2: Atomic Package-Scope Rename** - `@plane/*` → `@bright-byte/*` across the whole monorepo in one build-green commit (Pi→Byte internal identifiers folded in) (completed 2026-06-01)
- [ ] **Phase 3: De-monetization + EE Ungating** - All billing/upsell chrome removed inventory-first; every CE feature stands free with no blank or broken surfaces
- [ ] **Phase 4: Render Topology + Infra** - `render.yaml` blueprint + external R2/SMTP/broker provisioned; a client can be onboarded end-to-end on a live shared instance
- [ ] **Phase 5: Security Hardening + AGPL Gate** - Insecure defaults locked down and the AGPL §13 source-availability offer live before any client data is served

## Phase Details

### Phase 1: User-Facing Rebrand

**Goal**: Anyone using or visiting the product sees "Bright-Byte PMP" everywhere a human looks — app titles, browser tabs, PWA install, logos, icons, emails, and the AI assistant — with zero "Plane" leaks (AGPL copyright headers excepted).
**Depends on**: Nothing (first phase)
**Requirements**: BRAND-01, BRAND-02, BRAND-03, BRAND-04, BRAND-05, BRAND-06, BRAND-07, BRAND-08, BRAND-09, BRAND-10, BRAND-11, AI-01, AI-02
**Success Criteria** (what must be TRUE):

1. Loading web, admin, and space apps shows "Bright-Byte PMP" in the browser tab, OG/social preview, and PWA install prompt (no "Plane" title)
2. The Bright-Byte logo, favicon, and app/PWA icons appear in the sidebar, auth screen, spinners, and home-screen install (no Plane mark)
3. UI strings (English + all 18 other locales) and every email (invite, magic-link, password-reset, notification, `EMAIL_FROM`) read Bright-Byte, not Plane
4. The AI assistant presents as "Byte" — labels, generating-response text, and the assistant icon — everywhere a user sees it
5. A case-insensitive `plane` sweep across manifests, i18n, `EMAIL_FROM`, generated PDFs, and telemetry/user-agent strings comes back clean (excluding verbatim AGPL headers)

**Plans**: 6 plans
Plans:

- [ ] 01-01-PLAN.md — App metadata + brand constants (web/admin/space titles, OG/meta, @plane/constants); env-driven URL/email (BRAND-01/02/06/07)
- [ ] 01-02-PLAN.md — PWA manifests + logo/favicon/icon wiring & client-asset drop-in (BRAND-03/04/05)
- [ ] 01-03-PLAN.md — Email templates + EMAIL_FROM rebrand, remote-logo replacement (BRAND-10)
- [x] 01-04-PLAN.md — AI assistant → "Byte" labels/icon + English i18n incl. pi_chat (AI-01/02, BRAND-08)
- [x] 01-05-PLAN.md — All 18 non-English locales brand-mark rebrand + pi_chat=Byte (BRAND-09, AI-01)
- [ ] 01-06-PLAN.md — Brand-leak sweep + AGPL-integrity verification gate (BRAND-11)

**UI hint**: yes

### Phase 2: Atomic Package-Scope Rename

**Goal**: The internal package scope is fully `@bright-byte/*` and the monorepo still installs, builds, type-checks, and lints clean — delivered as one atomic commit because a half-renamed `workspace:*` monorepo cannot install or build and there is no CI test net.
**Depends on**: Phase 1
**Requirements**: RENAME-01, RENAME-02, RENAME-03, AI-03
**Success Criteria** (what must be TRUE):

1. `pnpm build && pnpm check:types && pnpm check:lint` all pass green on the renamed tree
2. `git grep -c "@plane/"` returns 0 across source (rename is complete, single atomic commit)
3. The `@/plane-web/*` and `@/plane-live/*` edition aliases, the Next.js compat shims, and the Python `plane` package are untouched and still resolve
4. The lockfile was regenerated via `pnpm install` (never hand-edited) and the workspace catalog, `turbo.json`, tsconfig `extends`, and CSS `@import`s all resolve under the new scope
5. Internal Pi→Byte identifiers (`PiChatLogo`, `sub-brand.pi-chat` registry key, `pi_chat` key, `GptAssistantPopover`) are renamed without changing the AI backend service contract

**Plans**: 1 plan
Plans:

- [x] 02-01-PLAN.md — Atomic package-scope rename: codemod, package graph/config/import rewrite, Byte internal identifiers, lockfile regeneration, and full build/type/lint gate (RENAME-01/02/03, AI-03)

**UI hint**: yes

### Phase 3: De-monetization + EE Ungating

**Goal**: Every payment/upsell/license surface is gone and every Community-Edition feature stands free — achieved inventory-first so no removal leaves a blank surface, a dead button, or a call to a Plane cloud host.
**Depends on**: Phase 2 (imports must resolve under `@bright-byte/*` before editing the billing/license consumers)
**Requirements**: BILL-01, BILL-02, BILL-03, BILL-04, BILL-05, BILL-06
**Success Criteria** (what must be TRUE):

1. There is no Billing/Plans settings page, route, or sidebar nav entry, and no license/upgrade modal cluster anywhere in the app
2. The edition badge shows version only (no upgrade trigger); no in-component upsell banners, CTAs, or `MARKETING_*`/`SUBSCRIPTION_*` triggers remain
3. Every previously upsell-gated CE feature is reachable and works; no surface is blank, broken, or dangling after removal
4. No UI path calls `plane.so` / `app.plane.so`, and plan/pricing data (`plans.tsx`, `payment.ts`, billing constants in `subscription.ts`) is deleted
5. An inventory/classification record exists for each upsell stub (CE-present → ungated vs EE-only → entry point cleanly removed)

**Plans**: TBD
**UI hint**: yes

### Phase 4: Render Topology + Infra

**Goal**: The full multi-service stack runs as a single shared instance on Render from a version-controlled `render.yaml` blueprint, with the three Render gaps (object storage, broker, SMTP) filled — and a client can be onboarded as a workspace end-to-end.
**Depends on**: Phase 2 green (Render images build the renamed packages). Blueprint/infra work may proceed in parallel with Phases 1–3, but deploy occurs only after the rename is green.
**Requirements**: DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05, DEPLOY-06, DEPLOY-07
**Success Criteria** (what must be TRUE):

1. A `render.yaml` blueprint deploys all services from the existing Dockerfiles — `api` (Web), `worker`+`beat` (Background Workers, exactly one beat), `live` (WebSocket), `space` (SSR), `web`+`admin` (Static Sites), `migrator` (preDeploy)
2. Render managed Postgres + Render Key Value (paid tiers) are provisioned and wired; external Cloudflare R2 is provisioned and verified for presigned PUT/GET
3. The Celery broker decision is resolved and implemented (CloudAMQP vs self-run RabbitMQ vs the ~3-line Redis-broker change with `noeviction`) and workers process jobs
4. Proxy/origin topology is decided and applied — correct baked `VITE_*_BASE_URL`/`*_BASE_PATH` build args, OAuth redirect URIs, and auth cookies work across services
5. On the live instance a client signs in, creates a project, uploads an attachment, and receives an email (invite/magic-link)

**Plans**: TBD
**UI hint**: yes

### Phase 5: Security Hardening + AGPL Gate

**Goal**: The deployed instance is safe and legally compliant to serve real client data — insecure-by-default settings are locked down, secrets compare in constant time, telemetry no longer phones Plane, and the AGPL §13 network source-availability offer is live. This is the hard gate before client cutover.
**Depends on**: Phase 4 (hardens the live deployment before real client data is served)
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04
**Success Criteria** (what must be TRUE):

1. Django boots with a stable `SECRET_KEY`, exact `ALLOWED_HOSTS`, and explicit https-only `CORS_ALLOWED_ORIGINS` (no allow-all + credentials fallback); a boot-time guard rejects insecure config
2. The live-server secret comparison is timing-safe (constant-time compare, not `!==`)
3. No `print()` remains in backend data/error paths and no telemetry/user-agent data is sent to Plane endpoints (repointed or disabled)
4. The deployed app exposes a working AGPL §13 source-availability offer, and attribution is recorded in a top-level `NOTICE`/`CHANGES` file (copyright headers and `LICENSE.txt` unchanged)

**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase                             | Plans Complete | Status      | Completed  |
| --------------------------------- | -------------- | ----------- | ---------- |
| 1. User-Facing Rebrand            | 2/6            | In Progress |            |
| 2. Atomic Package-Scope Rename    | 1/1            | Complete    | 2026-06-01 |
| 3. De-monetization + EE Ungating  | 0/TBD          | Not started | -          |
| 4. Render Topology + Infra        | 0/TBD          | Not started | -          |
| 5. Security Hardening + AGPL Gate | 0/TBD          | Not started | -          |
