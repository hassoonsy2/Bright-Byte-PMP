# Architecture Research

**Domain:** Brownfield monorepo rebrand — npm-scope rename + EE-ungating + single-instance Render deployment (Plane → Bright-Byte PMP)
**Researched:** 2026-06-01
**Confidence:** HIGH (rename mechanics + EE seam verified against the actual tree; Render/Celery topology verified against official Celery + Render docs)

> Scope note: This is the **architecture of the change**, not of Plane in general. Three workstreams:
> (1) `@plane/*` → `@bright-byte/*` scope rename, (2) billing/EE removal + ungating, (3) Render service topology.
> Plane's runtime architecture is already documented in `.planning/codebase/ARCHITECTURE.md` and is not re-derived here.

---

## Standard Architecture

### The Three Change Surfaces (what must move together)

```
┌──────────────────────────────────────────────────────────────────────┐
│  WORKSTREAM A — SCOPE RENAME  @plane/* → @bright-byte/*               │
│  (atomic: must land in ONE commit or build breaks)                    │
├──────────────────────────────────────────────────────────────────────┤
│  1. Package identity     15 packages/*/package.json  "name"           │
│  2. Dependency refs      19 package.json  deps/devDeps/peerDeps       │
│  3. Import sites         ~1,805 .ts/.tsx files (5,003 `from "@plane/"`)│
│  4. TS path aliases      apps/web/tsconfig.json (@/plane-web seam)    │
│  5. tsconfig "extends"   every app+pkg → @plane/typescript-config     │
│  6. CSS @import          3 globals.css + 1 storybook tailwind.css     │
│  7. Build configs        vite (via tsconfig-paths) / tsdown / turbo   │
│  8. Lockfile             pnpm-lock.yaml (regenerated, not edited)     │
├──────────────────────────────────────────────────────────────────────┤
│  WORKSTREAM B — EE/BILLING REMOVAL  (depends on A landing first)      │
│  CE overlay dirs (ce/components/license, workspace/billing) +         │
│  constants/plans.tsx + payment.ts + subscription gating              │
├──────────────────────────────────────────────────────────────────────┤
│  WORKSTREAM C — RENDER TOPOLOGY  (independent of A/B; render.yaml)    │
│  web · admin · space · live · api(web) · worker · beat · migrator    │
│  + Postgres · Key-Value(Redis) · S3(external) · SMTP(external)        │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities (rename targets)

| Surface | What it owns | Where it lives | Rename action |
|---------|--------------|----------------|---------------|
| Package names | The 15 publishable scope identities | `packages/*/package.json` `"name"` | `@plane/x` → `@bright-byte/x` |
| Dependency refs | `workspace:*` cross-links | all 19 `package.json` `dependencies`/`devDependencies`/`peerDependencies` | string-replace key |
| Import statements | 5,003 `from "@plane/…"` sites across ~1,805 files | `apps/{web,admin,space,live}` + `packages/*/src` | codemod (jscodeshift) |
| TS `extends` | Shared tsconfig presets | every `tsconfig.json` `"extends": "@plane/typescript-config/…"` | string-replace |
| CSS `@import` | Tailwind/editor/propel style entry | `apps/{web,admin,space}/styles/globals.css`, `packages/ui/styles/globals.css`, `packages/propel/.storybook/tailwind.css` | string-replace |
| Edition alias (web) | `@/plane-web/*` → `./ce/*` | `apps/web/tsconfig.json` ONLY | **do NOT rename** (see seam note) |
| Edition alias (live) | `@/plane-live/*` → `./src/ce/*` | `apps/live/tsconfig.json` ONLY | **do NOT rename** |
| Next compat shims | `next/link` `next/navigation` `next/script` | `apps/web/vite.config.ts` + `apps/web/app/compat/next/` | **untouched by scope rename** |
| Python backend | Django package `plane` | `apps/api/plane/` | **0 `@plane/` refs** — out of JS rename scope |

---

## CRITICAL FINDINGS (verified against the tree)

1. **The Python backend has ZERO `@plane/` references.** `grep -rl '@plane/' apps/api --include="*.py"` → 0. The npm scope rename is purely a JS/TS workstream. The Django Python package is independently named `plane` (`from plane.app…`) — renaming *that* (to `bright_byte`) is a much larger, optional, separable effort (touches every `from plane.` import, `INSTALLED_APPS`, Celery app name `-A plane`, migrations) and is **NOT** required for the rebrand. Recommend: leave the Python package as `plane`; it is invisible to end users.

2. **`@/plane-web/*` and `@/plane-live/*` are edition seams, not scope references.** They are local path aliases (web→`./ce/*`, live→`./src/ce/*`), NOT npm packages. A naive find-replace of "plane" WILL corrupt them. The codemod must match the `@plane/` *package scope* boundary only (`@plane/` followed by a package name), never `@/plane-web` or `@/plane-live`. Renaming the seam alias is cosmetic and risky — recommend leaving `@/plane-web` as-is, or doing it as a *separate, later* commit if desired.

3. **Vite gets aliases from tsconfig via `vite-tsconfig-paths`.** `apps/web/vite.config.ts` does NOT hardcode the `@/plane-web` alias — it loads `tsconfig.json` through the `tsconfigPaths` plugin. So updating tsconfig is sufficient; Vite needs no separate alias edit for the scope rename. The only hardcoded Vite aliases are the `next/*` compat shims, which are unaffected.

4. **The estimate of "~1,274 files" is low.** Actual: **1,805 source files** reference `@plane/`, with **5,003** `from "@plane/…"` import sites. Plan for ~1.8k files, not 1.3k.

5. **Celery broker can collapse onto Render Key Value.** `apps/api/plane/settings/common.py:309` sets `CELERY_BROKER_URL = AMQP_URL` whenever `AMQP_URL` is set. Celery natively supports `redis://` brokers, and Render Key Value speaks `redis://`/`rediss://`. So setting `AMQP_URL=redis://<keyvalue-internal-url>` lets you **drop RabbitMQ entirely** on Render (which has no managed RabbitMQ). Requires `maxmemory-policy noeviction` on the Key Value instance so queued jobs aren't evicted (HIGH — Render + Celery docs).

6. **`packages/codemods` already runs jscodeshift** (`function-declaration.ts`, `remove-directives.ts`) with a wired `jscodeshift -t … --parser=tsx` invocation and Vitest tests. This is the right tool and harness for the import rename — add a third transform alongside the existing two.

---

## Recommended Project Structure (the rename procedure as code)

```
packages/codemods/
├── rename-scope.ts          # NEW: jscodeshift transform (import/export/dynamic)
├── tests/rename-scope.spec.ts  # NEW: Vitest fixtures (named, type, dynamic, side-effect)
├── function-declaration.ts  # existing (untouched)
└── remove-directives.ts     # existing (untouched)
```

The transform rewrites `ImportDeclaration`, `ExportNamedDeclaration`/`ExportAllDeclaration`, `ImportExpression` (dynamic `import()`), and `CallExpression` (`require()`) `.source.value` when it starts with `@plane/` AND is NOT exactly `@/plane-web`/`@/plane-live` (those don't start with `@plane/` anyway, so the boundary is naturally safe). Map: `@plane/<rest>` → `@bright-byte/<rest>`.

### Structure Rationale

- **AST codemod over `sed`:** `sed -i 's#@plane/#@bright-byte/#g'` *would* mostly work because the scope token `@plane/` is unambiguous and never collides with `@/plane-web`. But the AST transform (a) is testable with Vitest fixtures, (b) won't touch strings inside comments/AGPL headers or unrelated literals, and (c) reuses the existing `packages/codemods` harness. Use the codemod for `.ts/.tsx`; use scripted string-replace for the *non-source* surfaces (package.json, tsconfig, css) where there's no AST.
- **package.json / tsconfig / css are NOT jscodeshift targets** — handle them with a small Node script or careful `pnpm`-aware replace, because the scope appears as object keys (deps) and `"name"`/`"extends"` values, not as import statements.

---

## Architectural Patterns

### Pattern 1: Atomic rename in one commit, gated by full verification

**What:** All of Workstream A lands together. A monorepo with `workspace:*` links + a pnpm catalog cannot be half-renamed: if `packages/types` becomes `@bright-byte/types` but `apps/web/package.json` still depends on `@plane/types`, `pnpm install` fails to resolve the workspace link.

**When to use:** Always, for scope renames in a `workspace:*` monorepo.

**Ordered procedure (the canonical sequence):**

```
0. Pre-flight: clean tree, `pnpm install` green, `pnpm build` green, `pnpm check` green.
   Record baseline. Branch: rename/bright-byte-scope.

1. Rewrite the 15 package "name" fields:        packages/*/package.json
2. Rewrite all dependency references:           19 package.json (deps/devDeps/peerDeps)
   - both the @plane key AND keep "workspace:*" value untouched
3. Rewrite tsconfig "extends":                   every tsconfig.json referencing
                                                  @plane/typescript-config/*
4. Rewrite CSS @import:                          4 css files (tailwind-config/editor/propel)
5. Run the codemod over imports/exports:         pnpm --filter @bright-byte/codemods exec \
   jscodeshift -t rename-scope.ts --parser=tsx \
   apps/*/app apps/*/ce apps/*/core apps/*/ee \
   apps/*/helpers apps/*/src packages/*/src \
   --ignore-pattern='**/node_modules/**' --ignore-pattern='**/dist/**'
6. Regenerate lockfile:                           pnpm install   (DO NOT hand-edit pnpm-lock.yaml)
7. ── VERIFICATION GATE (all must pass) ──
   a. pnpm install            → resolves, 0 unresolved workspace links
   b. grep -rl '@plane/' --include='*.ts*' --include='*.json' --include='*.css' .
        | grep -v node_modules | grep -v '/dist/'   → EMPTY (except @/plane-web aliases)
   c. pnpm build              → all packages + apps build (turbo ^build order)
   d. pnpm check:types        → tsc clean (depends on ^build)
   e. pnpm check:lint         → oxlint clean
8. Commit as a single atomic change.
```

**Trade-offs:** One large commit is harder to review but is the only safe granularity. Mitigate review pain by keeping the *content* change mechanical (pure scope swap) and isolating any EE/billing edits to Workstream B commits.

### Pattern 2: Verification gate driven by the existing turbo graph

**What:** `turbo.json` already encodes the safety net: `build` and `check:types` both have `dependsOn: ["^build"]`, so packages build before apps and types are checked against built `dist/`. Renaming changes nothing about this graph — so the same `pnpm build && pnpm check` that passed pre-rename is the exact gate that must pass post-rename.

**When to use:** As the definition of "done" for Workstream A. No green build = rename is incomplete.

**The build order is therefore fixed by turbo, not by you:**
```
@bright-byte/typescript-config, /tailwind-config   (leaf configs, no build)
        ↓
@bright-byte/{constants, types, logger, decorators, utils, shared-state}
        ↓
@bright-byte/{hooks, services, i18n, ui, propel}
        ↓
@bright-byte/editor
        ↓
apps/{web, admin, space, live}      (consume the packages)
```
`turbo run build` resolves this automatically from `workspace:*` deps — you do not hand-order it. The implication for *roadmap phasing*: the rename is a single phase with an internal sequence, not multiple phases.

### Pattern 3: Keep the edition seam; ungate by short-circuiting CE flags

**What:** EE features are gated by feature flags / subscription checks resolved through the `@/plane-web/*` (CE) overlay, NOT by the npm scope. The CE overlay already provides "community" implementations (`apps/web/ce/store/root.store.ts` extends `CoreRootStore`; `ce/components/license`, `ce/components/workspace/billing`, `ce/components/common/subscription`). Ungating = making the CE flag/subscription resolvers return "enabled/pro" instead of rendering upsell UI — done inside `ce/`, so `core/` imports stay valid and no import graph breaks.

**When to use:** Workstream B, AFTER the scope rename is green.

**Trade-offs:** Removing billing *components* outright risks breaking `core/` files that import them via `@/plane-web/components/workspace/billing`. Safer: keep the import surface (the `ce/.../index.ts` barrels) intact but replace the component bodies with no-ops / "already unlocked" states, then prune dead imports last. Only 9 files import the billing/license/plans surfaces directly — small blast radius.

---

## Data Flow

### Rename dependency flow (what blocks what)

```
package.json "name" rewrite ──┐
dependency-ref rewrite ───────┼──► pnpm install (regen lockfile) ──► workspace links resolve
tsconfig "extends" rewrite ───┘                                              │
import-site codemod ──────────────────────────────────────────────────────►┤
css @import rewrite ────────────────────────────────────────────────────────┤
                                                                             ▼
                                              turbo build (^build order) ──► check:types ──► check:lint
                                                                             │
                                                          GREEN = rename complete & safe
```

### EE-removal dependency flow

```
constants/plans.tsx  ─┐
payment.ts (types +   ├─► consumed by ce/components/workspace/billing/*  ─┐
  constants + utils)  │   consumed by ce/components/license/*            ├─► imported by ~9 core files
subscription gating  ─┘   consumed by ce/components/common/subscription  ─┘   via @/plane-web/*
                                                                             │
                                  Ungate: flip flag resolvers in ce/ ───────►│ (core imports unchanged)
                                  Remove UI: no-op the ce barrels last ──────►│ then prune 9 consumers
```

### Render request/runtime flow (single shared instance)

```
Internet
   │  (Render routes by service; no Caddy container needed — see topology note)
   ├── web (static SPA)        :10000  ── serves /*            ─┐
   ├── admin (static SPA)                ── /god-mode           │
   ├── space (SSR @react-router/serve)   ── /spaces             │  all call →
   ├── live (Node/Hocuspocus)  ws        ── /live  (WebSocket)  │
   └── api (Django gunicorn+uvicorn) :8000 ── /api /auth /static┘
                                              │        │      │
                                              ▼        ▼      ▼
                                   Render Postgres   Render Key-Value   External S3
                                   (DATABASE_URL)    (REDIS_URL +       (AWS_S3_ENDPOINT_URL,
                                                      AMQP_URL=redis://) USE_MINIO=0)
                                              ▲
                          worker (celery -A plane worker) ── consumes broker (Key-Value)
                          beat   (celery -A plane beat)   ── schedules → broker
                          migrator (one-off / pre-deploy) ── python manage.py migrate
                                                              ▲
                                                         SMTP provider (invites/notifications)
```

### Key Data Flows

1. **Celery broker = Key Value (no RabbitMQ):** API/worker/beat all read `AMQP_URL`. Set it to the Key Value `redis://` internal URL. `REDIS_URL` (cache/sessions) can be the *same* Key Value instance on a different logical DB or a second instance. Key Value must use `maxmemory-policy noeviction` for broker safety.
2. **Object storage is external:** Render has no managed S3 → the `migrator`/api `create_bucket` + `S3Storage` path needs `AWS_S3_ENDPOINT_URL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`, and `USE_MINIO=0` pointed at an external S3-compatible bucket (e.g. Cloudflare R2, Backblaze B2, AWS S3).
3. **Internal service URLs:** Frontends are configured via `VITE_API_BASE_URL`/`VITE_LIVE_BASE_URL` (tracked in `turbo.json` `globalEnv`). On a single public hostname these are relative paths; if split across Render services, set them to the public Render URLs. The live server authenticates by calling the API's `/api/users/me/`, so it needs the API's internal/public URL.

---

## Render Service Topology (explicit)

| Render service | Type | Source | Start command | Scales |
|----------------|------|--------|---------------|--------|
| `api` (web) | Web Service | `Dockerfile.api` | `docker-entrypoint-api.sh` (gunicorn+uvicorn `:$PORT`) | yes |
| `worker` | Background Worker | `Dockerfile.api` | `celery -A plane worker -l info` | yes |
| `beat` | Background Worker | `Dockerfile.api` | `celery -A plane beat -l info` | **exactly 1** (scheduler) |
| `migrator` | Job / pre-deploy | `Dockerfile.api` | `python manage.py migrate` | one-off |
| `live` | Web Service (WS) | `Dockerfile.live` | `node` Hocuspocus server | yes (Redis-synced awareness) |
| `web` | Static Site | `Dockerfile.web` / Vite build | `serve` static bundle | n/a |
| `admin` | Static Site | `Dockerfile.admin` | `serve` static bundle | n/a |
| `space` | Web Service (SSR) | `Dockerfile.space` | `@react-router/serve` | yes |
| `proxy` | (optional) | `Dockerfile.ce` Caddy | — | see note |

**Managed data services:** Render Postgres (`DATABASE_URL`), Render Key Value (`REDIS_URL` + broker via `AMQP_URL=redis://…`). **External:** S3-compatible bucket, SMTP provider.

**Proxy note:** The Caddy `apps/proxy` routes by path prefix (`/api`, `/live`, `/spaces`, `/god-mode`, `/*`) to internal hostnames. On Render you have two valid topologies:
- **(A) Replicate the proxy:** run one Caddy/`proxy` Web Service as the public entrypoint, `reverse_proxy` to the other services' *internal* Render URLs. Preserves the single-origin cookie/auth model (session cookies + `withCredentials` assume same origin) with least code change. **Recommended** — auth and the live-server cookie forwarding depend on same-origin.
- **(B) Drop the proxy:** expose each service on its own Render URL and wire `VITE_*_BASE_URL` to absolute URLs. Simpler infra but you must solve cross-origin cookies/CORS — and `.planning/codebase/CONCERNS.md` already flags CORS allow-all / `ALLOWED_HOSTS="*"` as security debt that must be hardened. Higher risk.

**Suggested build/deploy order on Render:**
```
1. Provision Postgres + Key Value (set noeviction) + external S3 bucket + SMTP creds
2. Build api image → run `migrator` job (migrate) ONCE          ← blocks everything below
3. Deploy api (web) → worker → beat                              ← api entrypoint registers instance,
                                                                   configure_instance, create_bucket
4. Deploy live (needs api URL for onAuthenticate)
5. Build+deploy static web / admin / space (need VITE_*_BASE_URL)
6. Deploy proxy (topology A) as public entrypoint, last
```
`migrator` MUST complete before api/worker/beat boot — their entrypoints call `wait_for_migrations` and will block otherwise.

---

## Scaling Considerations

| Scale | Adjustments |
|-------|-------------|
| Internal clients (handful of workspaces) | Single instance per role is plenty. Smallest paid Render tiers; `beat`=1 instance; web/worker/api at 1 each. Key Value handles both cache + broker. |
| Growth (more clients/workspaces) | Scale `api` and `worker` horizontally first (stateless). Split Key Value into separate cache vs broker instances if eviction pressure appears. `live` scales horizontally (Redis-synced awareness). |
| Heavy real-time / exports | Dedicated worker queue for exports/PDF; consider re-introducing RabbitMQ only if Redis broker eviction/ordering becomes a problem (Celery docs note Redis broker has visibility-timeout + monitoring caveats). |

### Scaling Priorities (for the rename/deploy, not the product)

1. **First bottleneck = the verification gate, not runtime.** The risk is a partial rename. Mitigate with the grep-for-`@plane/` gate (must be empty) before merging.
2. **Second = broker reliability.** If `noeviction` isn't set on Key Value, queued Celery jobs (emails, webhooks, activity) can silently drop under memory pressure. Set it at provision time.

---

## Anti-Patterns

### Anti-Pattern 1: Blind global find-replace of "plane"

**What people do:** `grep -rl plane | xargs sed -i 's/plane/bright-byte/g'`
**Why it's wrong:** Corrupts the `@/plane-web` / `@/plane-live` edition aliases, the Python `plane` package, the GitHub repo URL, AGPL copyright headers ("Plane Software, Inc."), and prose in docs. The scope token to match is the literal `@plane/` (scope + slash), nothing else.
**Do this instead:** Match `@plane/` exactly in imports (codemod) and as dep-keys/`name`/`extends` values (scripted, AST-aware where possible). Leave `@/plane-web`, Python `plane`, and AGPL headers untouched.

### Anti-Pattern 2: Hand-editing `pnpm-lock.yaml`

**What people do:** sed the lockfile to swap scopes.
**Why it's wrong:** The lockfile encodes integrity hashes and resolved workspace graph; manual edits desync it and break `--frozen-lockfile` CI.
**Do this instead:** Rewrite the source `package.json` files, then `pnpm install` to regenerate the lockfile.

### Anti-Pattern 3: Renaming the edition alias as part of the scope rename

**What people do:** Also rename `@/plane-web` → `@/bright-byte-web` in the same pass.
**Why it's wrong:** It's an internal path alias (tsconfig + heavily-used in ~hundreds of `@/plane-web/*` import sites), unrelated to the npm scope. Bundling it inflates the diff and risk for zero user-facing benefit. The CONCERNS doc already flags CE/EE boundary leakage; touching the seam invites regressions.
**Do this instead:** Leave it. If a fully on-brand alias is wanted, do it as a *separate, isolated* commit after the scope rename is green.

### Anti-Pattern 4: Removing billing components before ungating

**What people do:** Delete `ce/components/workspace/billing` first.
**Why it's wrong:** ~9 `core` files import that surface via `@/plane-web/*`; deleting the barrel breaks the build before you've replaced the call sites.
**Do this instead:** Ungate first (flip flag/subscription resolvers to "unlocked"), no-op the billing/license UI bodies while keeping their `index.ts` export surface, verify build, then prune the now-dead consumers last.

---

## Integration Points

### External Services (Render deployment)

| Service | Integration Pattern | Notes / gotchas |
|---------|---------------------|------------------|
| Render Postgres | `DATABASE_URL` env | `migrator` job runs `migrate` before any app boots |
| Render Key Value | `REDIS_URL` (cache/sessions) + `AMQP_URL=redis://…` (Celery broker) | **set `maxmemory-policy noeviction`**; same workspace + region for internal URL |
| S3-compatible bucket (external) | `AWS_S3_ENDPOINT_URL`, `AWS_*` creds, `AWS_S3_BUCKET_NAME`, `USE_MINIO=0` | Render has NO managed object storage; attachments require this |
| SMTP provider (external) | Django email settings env | invites + notifications fail silently without it |
| RabbitMQ | **eliminated** on Render | replaced by Key Value broker; keep `docker-compose.yml` RabbitMQ for local dev only |

### Internal Boundaries

| Boundary | Communication | Considerations |
|----------|---------------|----------------|
| frontends ↔ api | HTTP, session cookie, `withCredentials` | same-origin assumed → favor proxy topology (A) |
| live ↔ api | live calls `/api/users/me/` on WS auth + fetches/flushes doc binary | live needs api URL; auth = forwarded cookie |
| worker/beat ↔ api | shared Django code + shared broker/DB | identical image, different entrypoint command |
| packages ↔ apps | `workspace:*` via pnpm catalog | the entire rename's atomicity requirement lives here |

---

## Roadmap Implications (for the consuming roadmap)

- **Workstream A (scope rename) = one phase**, internally sequenced (names → deps → tsconfig/css → import codemod → install → verify). Its "definition of done" is a green `pnpm build && pnpm check:types && pnpm check:lint` plus an empty `@plane/` grep. Do not split across phases — it cannot be half-done.
- **Workstream B (EE/billing) depends on A** and should follow it. Small blast radius (~9 direct consumers); ungate-then-prune ordering.
- **Workstream C (Render) is independent** of A/B and can be developed in parallel, but **deploy** only after A is green (the images build the renamed packages). Key infra decisions to surface as phase tasks: Key-Value-as-broker (`AMQP_URL=redis://` + noeviction), external S3, external SMTP, proxy topology (A recommended), and the security hardening flagged in CONCERNS (`ALLOWED_HOSTS`, CORS, `SECRET_KEY`) which becomes load-bearing the moment real client data is served.
- **Out of scope (flag explicitly):** renaming the Python `plane` package, renaming the `@/plane-web` edition alias, and removing RabbitMQ from local `docker-compose.yml`.

---

## Sources

- Direct inspection of the tree: `pnpm-workspace.yaml`, `turbo.json`, `package.json`, `apps/web/tsconfig.json`, `apps/web/vite.config.ts`, `apps/{admin,space,live}/tsconfig.json`, `packages/typescript-config/`, `packages/codemods/package.json`, `apps/api/plane/settings/common.py`, `apps/api/plane/settings/storage.py`, `apps/api/bin/docker-entrypoint-*.sh`, `apps/proxy/Caddyfile.ce`, `docker-compose.yml` — HIGH
- `.planning/codebase/ARCHITECTURE.md`, `STRUCTURE.md`, `STACK.md`, `PROJECT.md` — HIGH
- Celery — Redis as broker/backend, eviction & visibility caveats: https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html — HIGH
- Render Key Value (redis:// scheme, `noeviction` for job queues, same-workspace/region internal URL): https://render.com/docs/key-value — HIGH
- Plane self-hosting (AIO requires external Postgres/Redis/RabbitMQ/S3; standard stack uses RabbitMQ+Valkey): https://deepwiki.com/makeplane/plane/6.4-self-hosting-guide — MEDIUM

---
*Architecture research for: Plane → Bright-Byte PMP rebrand (rename + ungate + Render)*
*Researched: 2026-06-01*
