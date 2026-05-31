# Technology Stack

**Analysis Date:** 2026-05-31

## Languages

**Primary:**
- TypeScript 5.8.3 - All frontend apps (`apps/web`, `apps/admin`, `apps/space`), the real-time server (`apps/live`), and all `packages/*`
- Python 3.12.x - Django API backend (`apps/api`)

**Secondary:**
- CSS (Tailwind 4.1.17) - Styling for frontend apps via `packages/tailwind-config`

## Runtime

**Environment:**
- Node.js 22.18.0 (pinned via `engines.node` in `package.json` and `.mise.toml`)

**Python:**
- Python 3.12.x (pinned in `.github/workflows/pull-request-build-lint-api.yml`)

## Package Manager

**JavaScript:**
- pnpm 11.3.0 (pinned via `packageManager` field in `package.json`)
- Lockfile: `pnpm-lock.yaml` (present)
- Workspace config: `pnpm-workspace.yaml`
- Catalog: All shared dependency versions are centralized in the `catalog:` section of `pnpm-workspace.yaml` — packages reference `"catalog:"` instead of version strings. This is the canonical version source for all JS/TS dependencies.

**Python:**
- pip with `requirements/` split files: `base.txt`, `production.txt`, `local.txt`, `test.txt`

## Monorepo Tooling

**Orchestrator:**
- Turborepo 2.9.14 (`turbo.json` at root)
- Remote cache: disabled (`"remoteCache": { "enabled": false }`)
- Tasks: `build`, `dev`, `start`, `clean`, `check`, `check:lint`, `check:types`, `check:format`, `fix`, `fix:lint`, `fix:format`, `test`
- Global env tracked: `VITE_*`, `SENTRY_*`, `NODE_ENV`, `LOG_LEVEL`, `APP_VERSION` (see `turbo.json` `globalEnv`)

**Runtime version manager:**
- mise (`/.mise.toml`) — pins `node = "22.18.0"`

## Frameworks

**Frontend apps (web, admin, space):**
- React 18.3.1 - UI rendering
- React Router 7.12.0 + `@react-router/dev` 7.13.1 - Routing and build (replaces Next.js)
  - `apps/web` and `apps/admin`: SSR disabled (`ssr: false`), static client bundle only
  - `apps/space`: SSR enabled, served via `@react-router/serve`
- Vite 7.3.2 - Build tool for frontend apps (`vite.config.ts` in each app)

**Backend (api):**
- Django 4.2.30 - Web framework (`apps/api/plane/`)
- Django REST Framework 3.15.2 - API layer
- Django Channels 4.1.0 - ASGI/WebSocket support (via `plane/asgi.py`)
- Celery 5.4.0 + django-celery-beat 2.6.0 - Background tasks and scheduled jobs
- Gunicorn 23.0.0 (production WSGI server) + uvicorn 0.29.0 (ASGI)

**Real-time server (live):**
- Express 4.22.0 - HTTP server
- Hocuspocus 2.15.2 (`@hocuspocus/server`) - WebSocket collaboration server built on Yjs
- Effect 3.20.0 + `@effect/platform-node` - Functional effect system used for request handling
- Yjs 13.6.20 - CRDT-based real-time collaboration

## State Management (Frontend)

- MobX 6.12.0 + mobx-react 9.1.1 - Client-side observable state
- SWR 2.2.4 - Server state / data fetching

## Editor

- TipTap 2.22.3 (with 15+ extensions) - Rich text editing (`packages/editor`)
- Yjs + y-prosemirror + Hocuspocus provider - Real-time collaborative editing
- ProseMirror - Underlying document model

## UI Component Packages

- `@plane/ui` - Internal shared components (BlueprintJS, Radix, Headless UI, Lucide icons)
- `@plane/propel` - Design-system components (charts via Recharts, calendar, command palette, etc.)
- `@atlaskit/pragmatic-drag-and-drop` 1.7.4 - Drag-and-drop primitives
- Tailwind CSS 4.1.17 - Utility-first CSS (configured in `packages/tailwind-config`)
- Framer Motion 12.23.0 - Animations
- Storybook 9.1.19 - Component development (`packages/ui` has `storybook` script)

## Workspace Packages

| Package | Purpose | Build Tool |
|---------|---------|-----------|
| `@plane/constants` | Shared constants | tsdown |
| `@plane/decorators` | TypeScript decorators (used by `live`) | tsdown |
| `@plane/editor` | TipTap-based rich text editor | tsc + tsdown |
| `@plane/hooks` | Shared React hooks | tsdown |
| `@plane/i18n` | i18next-based internationalization | tsdown + tsx scripts |
| `@plane/logger` | Winston-based logger for Node apps | tsdown |
| `@plane/propel` | Design system UI components | tsdown |
| `@plane/services` | API client layer (axios-based) | tsdown |
| `@plane/shared-state` | Cross-app shared state | tsdown |
| `@plane/tailwind-config` | Shared Tailwind + PostCSS config | — |
| `@plane/types` | Shared TypeScript type definitions | tsdown |
| `@plane/typescript-config` | Shared tsconfig bases | — |
| `@plane/ui` | Legacy shared UI components (Blueprint, Radix) | tsdown |
| `@plane/utils` | Shared utility functions | tsdown |

## Build Tooling

**JavaScript/TypeScript:**
- `tsdown` 0.16.0 - Primary bundler for all workspace packages (ESM output)
- `vite` 7.3.2 - Bundler for frontend apps (via `@react-router/dev` plugin)
- `tsc` 5.8.3 - Type checking; some packages run `tsc && tsdown` to emit `.d.ts` first

**Python:**
- `ruff` (via pyproject.toml) - Linting and formatting for `apps/api`

**Code Quality:**
- `oxlint` 1.51.0 - Fast JS/TS linter (replaces ESLint)
- `oxfmt` 0.35.0 - JS/TS formatter
- `husky` 9.1.7 + `lint-staged` 16.2.7 - Pre-commit hooks (run oxfmt + oxlint on staged files)

## Testing

**JavaScript/TypeScript:**
- Vitest 4.0.8 + `@vitest/coverage-v8` - Test runner (used in `apps/live`)

**Python:**
- pytest (via `pytest.ini` and `run_tests.py` in `apps/api`)
- factory-boy (Faker-based fixtures in `apps/api/plane/tests/`)

## Configuration Files

**Root:**
- `package.json` - Root workspace config, root-level devDependencies, lint-staged config
- `pnpm-workspace.yaml` - Workspace package globs + full dependency catalog
- `turbo.json` - Build pipeline, global env vars, remote cache settings
- `.mise.toml` - Node.js version pin (22.18.0)
- `turbo.json` references `.npmrc`, `.oxfmtrc.json`, `.oxlintrc.json` as global dependencies

**API (Django):**
- `apps/api/pyproject.toml` - ruff linting/formatting config
- `apps/api/plane/settings/common.py` - Base Django settings
- `apps/api/plane/settings/production.py` - Production overrides (Scout APM, JSON logging)
- `apps/api/plane/settings/local.py` - Local/dev overrides
- `apps/api/plane/settings/storage.py` - S3/MinIO storage backend

**Frontend apps:**
- `apps/web/vite.config.ts`, `apps/admin/vite.config.ts`, `apps/space/vite.config.ts` - Vite + React Router plugin
- `apps/web/react-router.config.ts` - React Router app config (SSR off for web/admin)

## Platform Requirements

**Development:**
- Node.js 22.18.0 (use mise to pin)
- pnpm 11.3.0
- Python 3.12.x (for API development)
- Docker + Docker Compose (for local infrastructure: Postgres, Redis/Valkey, RabbitMQ, MinIO)

**Production:**
- Docker-based deployment via `docker-compose.yml`
- Services: `web`, `admin`, `space`, `api`, `worker`, `beat-worker`, `migrator`, `live`, `proxy` (Caddy)
- Infrastructure: `plane-db` (Postgres 15.7), `plane-redis` (Valkey 7.2.11), `plane-mq` (RabbitMQ 3.13.6), `plane-minio` (MinIO)
- Kubernetes deployment configs in `deployments/kubernetes/`
- Docker Swarm configs in `deployments/swarm/`

---

*Stack analysis: 2026-05-31*
