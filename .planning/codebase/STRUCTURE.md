# Directory Structure

**Analysis Date:** 2026-05-31

## Repository Type

pnpm + Turborepo monorepo. Two top-level workspaces: `apps/*` (deployable applications) and `packages/*` (shared libraries). Workspace globs are declared in `pnpm-workspace.yaml`; the task graph is in `turbo.json`. See [[STACK]] for tooling and [[ARCHITECTURE]] for how the pieces interact.

## Top-Level Layout

```
Bright-Byte-PMP/
├── apps/                      # Deployable applications
│   ├── admin/                 # Admin/instance-management UI (React Router SPA)
│   ├── api/                   # Django REST backend (Python) — the core
│   ├── live/                  # Real-time collaboration server (Node, Hocuspocus)
│   ├── proxy/                 # Caddy reverse proxy (Caddyfiles + Dockerfile)
│   ├── space/                 # Public "Plane Sites" / shared views UI (React Router SPA)
│   └── web/                   # Main application UI (React Router SPA) — the largest app
├── packages/                  # Shared workspace libraries (@plane/*)
├── deployments/               # Deployment configs
├── docs/                      # Documentation
├── docker-compose.yml         # Production-style compose
├── docker-compose-local.yml   # Local dev compose
├── docker-compose-test.yml    # Test DB/services compose
├── turbo.json                 # Turborepo task pipeline
├── pnpm-workspace.yaml         # Workspace + dependency catalog
└── setup.sh                   # Environment bootstrap script
```

## Applications (`apps/`)

### `apps/web` — Main UI (largest surface)

```
apps/web/
├── app/                       # React Router routes & entry points
│   ├── (all)/ (home)/         # Route groups (parenthesized segments)
│   ├── compat/next/           # Next.js compatibility shims (link/navigation/script)
│   ├── entry.client.tsx       # Client entry
│   ├── root.tsx / layout.tsx  # Root layout
│   └── provider.tsx           # App-wide providers
├── ce/                        # Community Edition implementation (→ @/plane-web)
│   ├── components/ hooks/ store/ types/
├── core/                      # Core app code (→ @/)
│   ├── components/            # Feature React components
│   ├── constants/
│   ├── hooks/
│   ├── layouts/
│   ├── lib/
│   ├── services/              # API client services (*.service.ts)
│   ├── store/                 # MobX stores (*.store.ts)
│   └── types/
├── helpers/                   # → @/helpers
├── styles/                    # → @/styles
├── public/  nginx/            # Static assets + nginx config
├── react-router.config.ts  vite.config.ts  tsconfig.json
└── Dockerfile.web / Dockerfile.dev
```

**Path aliases** (`apps/web/tsconfig.json`):

| Alias | Resolves to | Meaning |
|---|---|---|
| `@/*` | `./core/*` | Core app code |
| `@/app/*` | `./app/*` | Route layer |
| `@/helpers/*` | `./helpers/*` | Helpers |
| `@/styles/*` | `./styles/*` | Styles |
| `@/plane-web/*` | `./ce/*` | Edition layer (CE here; EE swaps the target) |

The `@/plane-web` → `./ce` mapping is the **Community/Enterprise Edition seam**: open-source builds resolve it to `ce/`, while Enterprise builds point the same alias at an `ee/` directory. Code in `core/` imports edition-specific behavior through `@/plane-web` so the core stays edition-agnostic. (Heavily used — see [[CONCERNS]] for boundary-leak debt.)

**Next.js compat shims** (`apps/web/vite.config.ts`): `next/link`, `next/navigation`, and `next/script` are aliased to local shims under `app/compat/next/` — residue of an in-progress Next.js → React Router migration.

### `apps/admin` & `apps/space` — Secondary UIs

Same React Router SPA shape as `web` but flatter (no `core/`/`ce/` split):

```
apps/admin/  (and apps/space/)
├── app/           # Routes
├── components/    # Components
├── helpers/ hooks/ lib/ store/ styles/ utils/
├── providers/     # (admin)
├── public/ nginx/
├── react-router.config.ts  vite.config.ts  tsconfig.json
└── Dockerfile.* / Dockerfile.dev
```

### `apps/api` — Django backend (Python)

```
apps/api/
├── manage.py
├── plane/                     # Django project root (package "plane")
│   ├── analytics/             # Analytics app
│   ├── api/                   # External/public REST API (token-authed)
│   ├── app/                   # Main app API (session/web-authed)
│   │   ├── middleware/  permissions/  serializers/  urls/  views/
│   ├── authentication/        # Auth backends & flows
│   ├── bgtasks/               # Celery background tasks
│   ├── db/                    # Models, managers, migrations
│   ├── license/               # Licensing
│   ├── middleware/            # Request middleware (DB routing, logging)
│   ├── seeds/                 # Seed data
│   ├── settings/              # Split settings (common/test/production)
│   ├── space/                 # Public-spaces API
│   ├── throttles/             # DRF rate limiting
│   ├── tests/                 # pytest suite (see [[TESTING]])
│   ├── utils/
│   ├── celery.py  urls.py  asgi.py  wsgi.py
├── requirements/  requirements.txt  pyproject.toml  pytest.ini
├── bin/  templates/  static/
└── Dockerfile.api / Dockerfile.dev
```

The `api/` vs `app/` split is the key distinction: `plane/api/` = the public token-authenticated API; `plane/app/` = the internal API consumed by the web frontend.

### `apps/live` — Real-time server (Node)

```
apps/live/
├── src/
│   ├── controllers/           # Route controllers (decorator-based)
│   ├── extensions/            # Hocuspocus / collaboration extensions
│   ├── lib/                   # auth-middleware, pdf rendering, helpers
│   ├── schema/                # Effect schemas (e.g. pdf-export)
│   ├── services/              # Business services (pdf-export, etc.)
│   ├── types/  utils/
│   ├── hocuspocus.ts          # Collaboration engine wiring
│   ├── redis.ts  server.ts  start.ts  env.ts
├── tests/                     # Vitest tests
├── vitest.config.ts  tsdown.config.ts  tsconfig.json
└── Dockerfile.live / Dockerfile.dev
```

### `apps/proxy` — Reverse proxy

Caddy-based. Contains only `Caddyfile.ce`, `Caddyfile.aio.ce`, and `Dockerfile.ce` — no application code.

## Shared Packages (`packages/`)

All published under the `@plane/*` scope. Most are built with `tsdown` (see `tsdown.config.ts`) and expose `src/` + a barrel `index.ts`.

| Package | Purpose |
|---|---|
| `@plane/constants` | Shared constant values |
| `@plane/decorators` | TS decorators (e.g. for `apps/live` controllers) |
| `@plane/editor` | Rich-text editor (CE/core/EE split inside `src/`) |
| `@plane/hooks` | Shared React hooks |
| `@plane/i18n` | Localization (`locales/`, `scripts/`, `src/`) |
| `@plane/logger` | Winston logging config + Express middleware |
| `@plane/propel` | UI/component library (large; has its own postcss + public assets) |
| `@plane/services` | Shared API service clients |
| `@plane/shared-state` | Cross-app state utilities |
| `@plane/tailwind-config` | Shared Tailwind theme (`index.css`, `variables.css`, `animations.css`) |
| `@plane/types` | Shared TypeScript types/interfaces/enums |
| `@plane/typescript-config` | Shared tsconfig presets (`base.json`, `react-*.json`, `nextjs.json`, etc.) |
| `@plane/ui` | Base UI primitives (`src/`, `styles/`) |
| `@plane/utils` | Shared utilities (incl. `cn()`, deprecated `theme-legacy.ts`) |
| `codemods` | jscodeshift codemods for migrations (not `@plane`-scoped; has Vitest tests) |

### CE / core / EE pattern inside packages

`packages/editor/src/` follows the same edition seam as `apps/web`:

```
packages/editor/src/
├── ce/        # Community implementation
├── core/      # Shared core
├── ee/        # Enterprise extensions
├── index.ts   # Barrel
└── lib.ts  styles/
```

## Naming Conventions (where to find things)

(Full rules in [[CONVENTIONS]].)

- React components: `kebab-case.tsx` — under `components/`
- MobX stores: `kebab-case.store.ts` — under `store/`
- API services: `kebab-case.service.ts` — under `services/`
- React hooks: `use-kebab-case.ts(x)` — under `hooks/`
- Python: `snake_case.py`, tests `test_*.py` — under `plane/<app>/` and `plane/tests/`
- Route groups in `apps/web/app`: parenthesized folders `(all)`, `(home)` (React Router convention)

## Where to add new code

| Task | Location |
|---|---|
| New web feature component | `apps/web/core/components/<feature>/` |
| New MobX store | `apps/web/core/store/<feature>.store.ts` |
| New frontend API service | `apps/web/core/services/<feature>.service.ts` (or `@plane/services`) |
| Edition-specific web behavior | `apps/web/ce/` (imported via `@/plane-web/*`) |
| New internal API endpoint | `apps/api/plane/app/views/` + `serializers/` + `urls/` |
| New public API endpoint | `apps/api/plane/api/` |
| New background job | `apps/api/plane/bgtasks/` (Celery) |
| New DB model | `apps/api/plane/db/models/` + migration |
| Shared cross-app utility | `packages/utils/src/` (or a more specific `@plane/*` package) |
| Shared type/interface | `packages/types/src/` |
| New live/collab controller | `apps/live/src/controllers/` |
| New Python test | `apps/api/plane/tests/{unit,contract,smoke}/` |

## Generated vs Committed

- **Committed:** `pnpm-lock.yaml`, all `src/`, configs, `requirements*.txt`, locale files
- **Generated (gitignored):** `dist/`, `build/`, `node_modules/`, `.turbo/`, Vite/tsdown outputs
- **Compat shims** (`apps/web/app/compat/next/`): committed, hand-written migration bridges

---

*Structure analysis: 2026-05-31*
