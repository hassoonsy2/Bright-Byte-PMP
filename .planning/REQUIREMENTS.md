# Requirements: Bright-Byte PMP

**Defined:** 2026-05-31
**Core Value:** Our clients get a fully branded, fully unlocked project-management tool with no payment or licensing friction — every capability available, hosted and operated by us.

> Brownfield milestone: the underlying Plane CE PM feature set is inherited as-is (see `.planning/PROJECT.md` → Validated). These requirements cover only the _change surfaces_: rebrand, AI rename, de-monetization, package-scope rename, Render deployment, and security/AGPL hardening. Every requirement is grounded in `.planning/research/` (FEATURES.md, STACK.md, ARCHITECTURE.md, PITFALLS.md, SUMMARY.md).

## v1 Requirements

### Brand (user-facing rebrand)

- [x] **BRAND-01**: Web app brand metadata reads "Bright-Byte PMP" — `apps/web/app/root.tsx` `APP_TITLE`, OG/twitter/`application-name` tags (color unchanged for v1)
- [x] **BRAND-02**: Brand constants set to Bright-Byte values — `packages/constants/src/metadata.ts` (`SITE_NAME`/`SITE_TITLE`/`SITE_DESCRIPTION`/`SITE_URL`, space-site equivalents) and `endpoints.ts` (`WEBSITE_URL`, `SUPPORT_EMAIL`)
- [x] **BRAND-03**: Favicons, app icons, PWA icons, and OG image replaced with client-provided assets — `apps/web/app/assets/{favicon,icons}`, `apps/web/public/{icons,favicon}`, OG image
- [x] **BRAND-04**: Logo assets and logo components show the Bright-Byte logo — sidebar, auth screen, spinners, and `packages/propel/src/icons/brand/plane-logo.tsx`
- [x] **BRAND-05**: PWA manifests rebranded across web/admin/space (`manifest.json`, `site.webmanifest.json`)
- [x] **BRAND-06**: Admin app brand reads "Bright-Byte PMP" — `apps/admin/app/root.tsx`, admin manifest
- [x] **BRAND-07**: Space (public Sites) app brand reads Bright-Byte — `apps/space/app/root.tsx`, space metadata constants (external-facing)
- [x] **BRAND-08**: English i18n strings rebranded — `packages/i18n/src/locales/en/*` (~130 "Plane" occurrences)
- [x] **BRAND-09**: All 18 non-English locales rebranded — `packages/i18n/src/locales/{cs,de,es,fr,id,it,ja,ko,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/*`
- [ ] **BRAND-10**: Email templates rebranded — `apps/api/templates/base.html` + `apps/api/templates/emails/**` (invites, magic-link, password reset, notifications) and `EMAIL_FROM`
- [ ] **BRAND-11**: No "Plane" leaks remain — case-insensitive sweep across manifests, i18n, email `EMAIL_FROM`, generated PDFs, and telemetry/user-agent strings passes clean (excludes AGPL copyright headers, which stay verbatim)

### AI Assistant (Byte)

- [x] **AI-01**: AI assistant user-visible labels read "Byte" — `apps/web/core/constants/ai.ts` ("Byte is generating response"), `pi_chat` locale key across all 19 locales, and `gpt-assistant-popover.tsx` placeholders
- [x] **AI-02**: AI logo/icon shows the Byte mark wherever `PiChatLogo` is used (e.g. `apps/web/core/components/workspace/sidebar/user-menu.tsx`)
- [x] **AI-03**: Internal code identifiers renamed Pi→Byte — `PiChatLogo` component, `sub-brand.pi-chat` icon registry key, `pi_chat` key, `GptAssistantPopover` naming (folded into the rename phase; AI backend service contract untouched)

### De-monetization (Billing)

- [x] **BILL-01**: Billing/Plans settings page and route removed — `apps/web/app/(all)/[workspaceSlug]/(settings)/.../billing/*`, route registration in `apps/web/app/routes/core.ts`, and the settings-sidebar nav entry (route removed before components, per dependency order)
- [x] **BILL-02**: License/upsell modal cluster removed — `apps/web/core/components/license/**` and `apps/web/ce/components/license/**` (PaidPlanUpgradeModal, plan cards, checkout, talk-to-sales)
- [x] **BILL-03**: "Community" edition badge → upgrade trigger neutralized to a version-only badge — `apps/web/ce/components/workspace/edition-badge.tsx` (badge neutralized before its imported modal is deleted)
- [x] **BILL-04**: In-component upsell banners/CTAs removed — e.g. `apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx` and all references to `MARKETING_*`/`SUBSCRIPTION_*` upgrade triggers
- [x] **BILL-05**: Plan/pricing data removed — `apps/web/core/constants/plans.tsx`, `packages/constants/src/payment.ts`, billing constants in `packages/constants/src/subscription.ts`
- [x] **BILL-06**: Each upsell stub inventoried and classified before removal; CE-present features left exposed and working, EE-only dangling entry points cleanly removed (no blank/broken surfaces, no calls to `plane.so`/`app.plane.so`)

### Package-Scope Rename (atomic)

- [x] **RENAME-01**: `@plane/*` renamed to `@bright-byte/*` across all 15 package names, 19 `package.json` dependency sets, ~5,003 import sites, tsconfig `extends`, and CSS `@import`s — implemented via a new `packages/codemods` jscodeshift transform with Vitest fixtures; lockfile regenerated via `pnpm install` (never hand-edited)
- [x] **RENAME-02**: Edition aliases preserved — `@/plane-web/*` and `@/plane-live/*` are NOT renamed (they are `@/`-prefixed, not `@plane/`); Next.js compat shims and the Python `plane` package left untouched
- [x] **RENAME-03**: Rename verification gate passes — `pnpm build && pnpm check:types && pnpm check:lint` all green and `git grep -c "@plane/"` returns 0 in source (single atomic commit; build is the safety net since there is no CI test step)

### Render Deployment (single shared instance)

- [ ] **DEPLOY-01**: A `render.yaml` Blueprint defines the full topology reusing existing Dockerfiles — `api` (Web), `worker` + `beat` (Background Workers, exactly one beat), `live` (Web, WebSocket), `space` (Web, SSR), `web` + `admin` (Static Sites), `migrator` (preDeploy)
- [ ] **DEPLOY-02**: Render managed Postgres + Render Key Value (Redis/Valkey) provisioned and wired (paid tiers — never free; free PG expires in 30 days)
- [ ] **DEPLOY-03**: External S3-compatible object storage (Cloudflare R2) provisioned for attachments and verified for presigned PUT/GET
- [ ] **DEPLOY-04**: SMTP provider configured so invites/magic-link/notifications send successfully
- [ ] **DEPLOY-05**: Celery broker decision resolved and implemented (CloudAMQP vs self-run RabbitMQ vs ~3-line Redis-broker change reusing Render Key Value with `noeviction`)
- [ ] **DEPLOY-06**: Proxy/origin topology decided and applied — correct `VITE_*_BASE_URL`/`*_BASE_PATH` build args (baked at build time) and OAuth redirect URIs; auth cookies work across services
- [ ] **DEPLOY-07**: Single shared instance is live on Render and a client can be onboarded as a workspace end-to-end (sign in, create project, upload attachment, receive email)

### Security & Compliance (hard gate before client cutover)

- [ ] **SEC-01**: Django settings hardened — stable `SECRET_KEY` (no ephemeral regen), exact `ALLOWED_HOSTS`, explicit `CORS_ALLOWED_ORIGINS` (https only, no allow-all fallback with credentials); boot-time guard rejects insecure config (`apps/api/plane/settings/common.py`)
- [ ] **SEC-02**: Live-server secret comparison is constant-time — `apps/live/src/lib/auth-middleware.ts` uses a timing-safe compare (replaces `!==`)
- [ ] **SEC-03**: `print()` removed from backend data/error paths; telemetry repointed or disabled (no data sent to Plane endpoints)
- [ ] **SEC-04**: AGPL §13 network source-availability offer is live in the deployed app; attribution recorded in a top-level `NOTICE`/`CHANGES` file (copyright headers and `LICENSE.txt` unchanged)

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Brand polish

- **BRANDV2-01**: Full brand-color change — replace Plane blue `#3579f6` with Bright-Byte brand colors across `theme_color`/`theme-color` meta and the Tailwind theme (`packages/tailwind-config`)
- **BRANDV2-02**: Repurpose the removed upgrade modal into a positive "all features included" affordance

### Operations

- **OPSV2-01**: Automated backups/restore runbook for Render Postgres + R2
- **OPSV2-02**: Per-client onboarding automation (workspace provisioning script)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature                                                     | Reason                                                                                                    |
| ----------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Subscriptions, paywalls, payment processing                 | Operated free for our clients; no monetization (PROJECT.md)                                               |
| Porting real EE-only features into CE                       | EE code lives in a `plane-web` package we don't have; "unlock" = remove upsell chrome only                |
| Editing AGPL copyright headers / LICENSE.txt                | AGPL violation + CI failure (`copyright-check.yml`); attribution goes in NOTICE instead                   |
| Renaming the `@/plane-web` / `@/plane-live` edition aliases | Internal edition seam, invisible to users; renaming is invasive and build-affecting                       |
| Issue / notification "subscriptions"                        | Core PM "notify me" feature, NOT billing — naming collision only; left intact                             |
| Re-engineering the AI/GPT backend                           | Rename is label-only; provider config stays admin-configurable                                            |
| `apps/api/plane/license/` instance-registration app         | Instance admin / God-mode bootstrap, not paid-plan billing                                                |
| Per-client isolated instances/databases                     | Chose single shared instance with per-client workspaces                                                   |
| Render free tier for production                             | Free PG expires in 30 days (no backups); free web services cold-start and break the live WebSocket server |

## Traceability

Each v1 requirement maps to exactly one phase (see `.planning/ROADMAP.md`).

| Requirement | Phase                                    | Status   |
| ----------- | ---------------------------------------- | -------- |
| BRAND-01    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-02    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-03    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-04    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-05    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-06    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-07    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-08    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-09    | Phase 1 — User-Facing Rebrand            | Complete |
| BRAND-10    | Phase 1 — User-Facing Rebrand            | Pending  |
| BRAND-11    | Phase 1 — User-Facing Rebrand            | Pending  |
| AI-01       | Phase 1 — User-Facing Rebrand            | Complete |
| AI-02       | Phase 1 — User-Facing Rebrand            | Complete |
| AI-03       | Phase 2 — Atomic Package-Scope Rename    | Complete |
| RENAME-01   | Phase 2 — Atomic Package-Scope Rename    | Complete |
| RENAME-02   | Phase 2 — Atomic Package-Scope Rename    | Complete |
| RENAME-03   | Phase 2 — Atomic Package-Scope Rename    | Complete |
| BILL-01     | Phase 3 — De-monetization + EE Ungating  | Complete |
| BILL-02     | Phase 3 — De-monetization + EE Ungating  | Complete |
| BILL-03     | Phase 3 — De-monetization + EE Ungating  | Complete |
| BILL-04     | Phase 3 — De-monetization + EE Ungating  | Complete |
| BILL-05     | Phase 3 — De-monetization + EE Ungating  | Complete |
| BILL-06     | Phase 3 — De-monetization + EE Ungating  | Complete |
| DEPLOY-01   | Phase 4 — Render Topology + Infra        | Pending  |
| DEPLOY-02   | Phase 4 — Render Topology + Infra        | Pending  |
| DEPLOY-03   | Phase 4 — Render Topology + Infra        | Pending  |
| DEPLOY-04   | Phase 4 — Render Topology + Infra        | Pending  |
| DEPLOY-05   | Phase 4 — Render Topology + Infra        | Pending  |
| DEPLOY-06   | Phase 4 — Render Topology + Infra        | Pending  |
| DEPLOY-07   | Phase 4 — Render Topology + Infra        | Pending  |
| SEC-01      | Phase 5 — Security Hardening + AGPL Gate | Pending  |
| SEC-02      | Phase 5 — Security Hardening + AGPL Gate | Pending  |
| SEC-03      | Phase 5 — Security Hardening + AGPL Gate | Pending  |
| SEC-04      | Phase 5 — Security Hardening + AGPL Gate | Pending  |

**Coverage:**

- v1 requirements: 34 total (BRAND 11 · AI 3 · BILL 6 · RENAME 3 · DEPLOY 7 · SEC 4)
- Mapped to phases: 34 ✓ (Phase 1: 13 · Phase 2: 4 · Phase 3: 6 · Phase 4: 7 · Phase 5: 4)
- Unmapped: 0 ✓
- Duplicates: 0 (each requirement in exactly one phase)

---

_Requirements defined: 2026-05-31_
_Last updated: 2026-06-01 after roadmap creation (traceability populated — 34/34 mapped)_
