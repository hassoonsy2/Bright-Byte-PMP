# Bright-Byte PMP

## What This Is

Bright-Byte PMP is a self-hosted, white-labeled project-management platform — a rebrand of the open-source Plane (Community Edition) — that we run for the clients who work with us. It keeps Plane's full feature set (workspaces, projects, work items, cycles, modules, views, pages, real-time collaboration) but removes all subscription/payment surfaces, carries our own brand and logo, renames the AI assistant to **Byte**, and is deployed as a single shared instance on Render.

## Core Value

Our clients get a fully branded, fully unlocked project-management tool with no payment or licensing friction — every capability available, hosted and operated by us.

## Requirements

### Validated

<!-- Inferred from existing Plane codebase (see .planning/codebase/). Shipped and relied upon. -->

- ✓ Workspaces with membership, roles, and invitations — existing
- ✓ Projects within workspaces — existing
- ✓ Work items (issues) with states, labels, assignees, comments, attachments, sub-issues — existing
- ✓ Cycles, modules, and custom views — existing
- ✓ Pages (rich-text docs) with real-time collaboration via the live server (`apps/live`, Hocuspocus) — existing
- ✓ Public shared views / "Sites" (`apps/space`) — existing
- ✓ Instance admin app (`apps/admin`) — existing
- ✓ Django REST backend with both internal (`plane/app`) and public token API (`plane/api`) — existing
- ✓ AI assistant in editor/issue modals (GPT assistant) — existing (to be renamed)
- ✓ Email-based auth, OAuth, notifications, webhooks — existing
- ✓ S3-compatible file/asset storage — existing
- ✓ Issue (notification) subscriptions — existing; **distinct from billing**, retained as-is

### Active

<!-- This milestone's scope. Hypotheses until shipped and validated. -->

- [ ] Rebrand all user-facing surfaces to "Bright-Byte PMP" (app titles, manifest, page metadata, emails, UI strings)
- [ ] Replace logos / favicons / app icons with client-provided Bright-Byte PMP brand assets
- [ ] Deep rename of internal package scope `@plane/*` → `@bright-byte/*` across all packages, imports, build config, and tsconfig path aliases
- [ ] Rename the AI assistant to **Byte** everywhere it surfaces (labels, prompts, tooltips, component naming)
- [ ] Remove all billing / license-upsell UI (`apps/web/core/components/license/*`, `apps/web/ce/components/license/*`, `workspace/billing/*`, edition badge, in-component upgrade banners, `constants/plans.tsx`, `packages/constants/src/payment.ts` + `subscription.ts`)
- [ ] Expose all CE-present features by removing upsell chrome — after an inventory/classification of each upsell stub. **Note (research correction):** CE has *no runtime license enforcement*; gated EE features are *absent code*, not flag-disabled. "Unlock" = remove upsell surfaces so CE's already-working features stand free; do NOT attempt to port EE code (out of scope)
- [ ] Deploy as a single shared instance on Render via a `render.yaml` blueprint (web, api, live, admin, worker/beat)
- [ ] Use Render managed Postgres + Render Key Value (Redis) as the data services
- [ ] Provision required external infra: S3-compatible object storage (attachments) and an SMTP provider (invites/notifications)
- [ ] Operate a multi-client model where each client is a workspace inside the one shared instance

### Out of Scope

<!-- Explicit boundaries with reasoning. -->

- Subscriptions, paywalls, and payment processing — product is operated free for our clients; no monetization
- Per-client isolated instances/databases — chosen single shared instance with per-client workspaces instead (lower ops overhead)
- Removing issue/notification "subscriptions" — these are a core feature, not billing; they stay
- Rewriting core PM functionality — we inherit Plane's feature set as-is
- Custom logo design — client is providing brand assets
- Plane Cloud / multi-tenant SaaS billing infrastructure — not relevant to internal client use

## Context

- **Brownfield.** Built on the Plane monorepo (pnpm + Turborepo): 6 apps (`admin`, `api`, `live`, `proxy`, `space`, `web`) and 15 `@plane/*` packages. Full analysis in `.planning/codebase/` (STACK, ARCHITECTURE, STRUCTURE, CONVENTIONS, TESTING, INTEGRATIONS, CONCERNS).
- **Brand split matters.** User-facing "Plane" lives in `apps/web/manifest.json`, titles, logos, i18n strings, and emails. The internal `@plane/*` package scope is a *separate* workstream: research measured **~1,805 files / ~5,003 import sites across 19 `package.json`** (larger than the initial ~1,274 estimate). It must be **one atomic, build-gated phase** (a half-renamed `workspace:*` monorepo won't install/build, and there is no CI test net). The `@/plane-web/*` and `@/plane-live/*` edition **aliases must NOT be renamed** (they are `@/`-prefixed, not `@plane/`); the Python `plane` package has 0 `@plane/` refs and is left alone.
- **Community Edition has no real payment processor and no runtime license enforcement.** "Payment" surfaces are pure upsell/license UI. De-monetization is a UI-removal + inventory job, not a billing-integration or feature-flag change.
- **Deployment gotchas** (from research): Render has no managed object storage → attachments need an external S3-compatible bucket (**Cloudflare R2** recommended); **Celery broker is AMQP-only in code and Render has no managed RabbitMQ** → a blocking decision (CloudAMQP vs self-run RabbitMQ vs a ~3-line Redis-broker change reusing Render Key Value); SMTP must be provisioned; `space` is SSR (Docker web service) while `web`/`admin` are static sites; `VITE_*` URLs are **baked at build time** (domain changes need a rebuild); Celery worker/beat run as Background Workers (exactly one beat).
- **Migration debt to be aware of** (from `.planning/codebase/CONCERNS.md`): an in-progress Next.js → React Router migration with compat shims, CE/EE boundary leakage, oversized issue modules, and insecure-by-default API settings (`ALLOWED_HOSTS="*"`, CORS allow-all fallback, ephemeral `SECRET_KEY`) that must be hardened for a real Render deployment.

## Constraints

- **Tech stack**: Inherit Plane's stack — Django REST (Python) backend, React Router + Vite frontends, Hocuspocus live server, pnpm/Turborepo monorepo. No framework changes.
- **License**: Plane is AGPL-3.0. Every source file carries an AGPL header reading "Plane Software, Inc." enforced by `copyright-check.yml` via `addlicense` against `COPYRIGHT.txt`. These headers and `LICENSE.txt` **stay verbatim** — editing them is both an AGPL violation and a guaranteed CI failure. Attribution changes go in a top-level `NOTICE`/`CHANGES` file, and an **AGPL §13 network source-availability offer must be live in the deployed app before serving clients**.
- **Hosting**: Render only (managed Postgres + Render Key Value/Redis). Existing Docker assets adapted to a `render.yaml` blueprint.
- **Compatibility**: Deep package rename must not break the build — imports, workspace catalog (`pnpm-workspace.yaml`), `turbo.json`, and `tsconfig` path aliases all updated atomically.
- **Security**: Insecure-by-default settings must be locked down before serving real client data.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Deep rename `@plane/*` → `@bright-byte/*` (not just user-facing brand) | User wants a complete rebrand including internal package scope | — Pending |
| Remove billing UI; "unlock" = strip upsell chrome (no EE code porting) | CE has no license enforcement — EE features are absent code, not flag-gated (research) | — Pending |
| Single shared instance, clients = workspaces | Lower ops/infra overhead than per-client instances | — Pending |
| Host on Render with managed Postgres + Redis | Single-vendor simplicity | — Pending |
| Rename AI assistant to "Byte" | Ties to "Bright-Byte" brand | — Pending |
| Client provides logo assets | Brand identity owned by client | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-31 after research (corrected EE-ungating framing, rename scope, broker + AGPL constraints)*
