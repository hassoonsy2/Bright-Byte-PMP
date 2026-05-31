<!-- refreshed: 2026-05-31 -->
# Architecture

**Analysis Date:** 2026-05-31

## System Overview

```text
┌───────────────────────────────────────────────────────────────────────┐
│                         Caddy Reverse Proxy                           │
│                      `apps/proxy/Caddyfile.ce`                        │
│  /spaces/* → space:3000   /god-mode/* → admin:3000                    │
│  /live/* → live:3000      /api/* /auth/* → api:8000                   │
│  /* → web:3000                                                        │
└──────┬───────────┬──────────┬──────────┬────────────┬────────────────┘
       │           │          │          │            │
       ▼           ▼          ▼          ▼            ▼
  ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌─────────────┐
  │  web    │ │ admin  │ │ space  │ │ live │ │     api     │
  │ :3000   │ │ :3001  │ │ :3002  │ │:3000 │ │   :8000     │
  │React    │ │React   │ │React   │ │Expr  │ │  Django     │
  │Router v7│ │Router  │ │Router  │ │+Hocus│ │  DRF + DRF  │
  └────┬────┘ └───┬────┘ └───┬────┘ └──┬───┘ └─────┬───────┘
       │          │          │          │            │
       └──────────┴──────────┴──────────┘      ┌────┴──────────┐
                       │                        │  PostgreSQL   │
               @plane/packages                  │  Redis        │
               (workspace:*)                    │  Celery       │
                                                │  RabbitMQ     │
                                                │  MinIO (S3)   │
                                                └───────────────┘
```

## Component Responsibilities

| Component | Responsibility | Key Entry Points |
|-----------|----------------|-----------------|
| `apps/web` | Main project management SPA (issues, cycles, modules, pages, analytics) | `apps/web/app/root.tsx`, `apps/web/app/routes.ts` |
| `apps/admin` | Instance admin panel (authentication config, workspace admin) | `apps/admin/app/` |
| `apps/space` | Public/published board view (intake, deploy boards) | `apps/space/app/` |
| `apps/live` | Collaborative document editing server (WebSocket + Hocuspocus) | `apps/live/src/start.ts` |
| `apps/proxy` | Caddy reverse proxy — routes all traffic, no custom code | `apps/proxy/Caddyfile.ce` |
| `apps/api` | Django REST API, Celery workers, DB schema | `apps/api/plane/urls.py` |
| `packages/*` | Shared libraries consumed by all frontend apps | `packages/*/src/index.ts` |

## Pattern Overview

**Overall:** Turborepo monorepo with a layered MVC-style frontend (MobX stores + React Router v7) and a Django REST Framework backend with Celery for async work and Hocuspocus for real-time collaboration.

**Key Characteristics:**
- Frontend apps are statically built SPAs (no SSR) served by `serve`, except `apps/space` which runs SSR via `@react-router/serve`
- All frontend state management uses MobX observable class stores; components consume stores through React Context and custom `useStore*` hooks
- The `@plane/` workspace packages form a shared dependency layer — apps reference them as `workspace:*` via pnpm catalog
- Edition variants (Community Edition vs Enterprise Edition) are toggled via path aliases: `@/plane-web/*` maps to `./ce/*` (CE build); an EE build would remap to `./ee/*`
- The Django backend exposes four URL namespaces: `/api/` (internal app), `/api/public/` (space/published), `/api/instances/` (license), `/api/v1/` (external REST API), `/auth/` (authentication)

## Layers

**Frontend Presentation Layer:**
- Purpose: React components, page layouts, route definitions
- Location: `apps/web/app/`, `apps/web/core/components/`, `apps/web/ce/components/`
- Contains: Route files (`layout.tsx`, `page.tsx`), feature components, layout wrappers
- Depends on: Store layer, service layer, shared packages
- Used by: React Router v7 routing engine

**Frontend Store Layer (MobX):**
- Purpose: All client-side state; single source of truth per entity
- Location: `apps/web/core/store/`, `apps/web/ce/store/`
- Contains: MobX observable classes (`*.store.ts`), `CoreRootStore`, `RootStore` (CE extension)
- Entry: `apps/web/core/lib/store-context.tsx` — creates singleton `RootStore`, provides it via `StoreContext`
- Depends on: Service layer, `@plane/types`, `@plane/shared-state`
- Used by: Hooks layer, components (via `useContext(StoreContext)`)

**Frontend Hooks Layer:**
- Purpose: Named accessors for store slices; thin wrappers over `useContext(StoreContext)`
- Location: `apps/web/core/hooks/store/`
- Pattern: `export const useInstance = (): IInstanceStore => useContext(StoreContext).instance`
- Depends on: Store layer
- Used by: All React components

**Frontend Service Layer:**
- Purpose: HTTP client classes; each extends `APIService` (abstract axios wrapper)
- Location: `apps/web/core/services/`
- Contains: One service class per domain (`IssueService`, `CycleService`, `WorkspaceService`, etc.)
- Depends on: `@plane/constants` (for `API_BASE_URL`), `@plane/types`
- Used by: Store layer (stores call services to fetch/mutate data)

**Edition Overlay Layer (`ce/` / `ee/`):**
- Purpose: CE-specific implementations of features that differ between editions
- Location: `apps/web/ce/` — components, hooks, store, types
- Alias mapping: `@/plane-web/*` → `./ce/*` (via `tsconfig.json`)
- Pattern: `ce/store/root.store.ts` extends `CoreRootStore`, adds CE-specific stores (e.g., `TimeLineStore`)
- Used by: All code that imports from `@/plane-web/*`

**Django API Layer:**
- Purpose: REST endpoints, serializers, ORM models, background tasks
- Location: `apps/api/plane/`
- Sub-modules: `app/` (main internal API), `api/` (external v1 API), `space/` (public boards), `license/` (instance mgmt), `authentication/` (auth flows)
- Contains: `views/` (extend `BaseViewSet`/`BaseAPIView`), `serializers/`, `urls/`, `db/models/`
- Depends on: PostgreSQL, Redis, Celery, RabbitMQ, MinIO

**Background Task Layer:**
- Purpose: Async processing via Celery (email notifications, webhooks, issue activities, exports)
- Location: `apps/api/plane/bgtasks/`
- Scheduler: `apps/api/plane/celery.py` (beat schedule for recurring tasks)

**Collaborative Editing Layer (Live):**
- Purpose: Real-time document collaboration via Hocuspocus + Yjs
- Location: `apps/live/src/`
- Entry: `apps/live/src/start.ts` → `Server` class → `HocusPocusServerManager` singleton
- Uses `@plane/decorators` for controller registration (`@Controller`, `@WebSocket`, `@Get`, `@Post`)
- Communicates with Django API to fetch/store document binary data

## Data Flow

### Frontend Request Lifecycle

1. Browser hits Caddy proxy — request routed to correct app container
2. React Router v7 matches route in `apps/web/app/routes.ts` (merges `coreRoutes` + `extendedRoutes`)
3. Route `layout.tsx` mounts, component calls store hook e.g. `useInstance()`
4. Store hook accesses `StoreContext` singleton — returns MobX observable store slice
5. Component triggers store action e.g. `store.issue.fetchIssues(workspaceSlug, projectId)`
6. Store action calls service method e.g. `IssueService.getIssuesFromServer()`
7. `APIService` (axios, `withCredentials: true`) sends HTTP request to `/api/workspaces/…`
8. On 401, interceptor redirects to sign-in page
9. Response data stored in MobX observables → React re-renders via `observer()`

### API Request Lifecycle (Django)

1. Caddy forwards `/api/*` to Django app on port 8000
2. `plane/urls.py` routes to `plane.app.urls`, `plane.api.urls`, `plane.space.urls`, etc.
3. Request passes through `TimezoneMixin` (activates user timezone) and `ReadReplicaControlMixin`
4. `BaseSessionAuthentication` validates session cookie
5. Permission class checks workspace/project role (`ROLE` enum, `allow_permission`)
6. ViewSet/APIView method executes business logic, queries ORM models
7. Serializer formats response; async side-effects dispatched to Celery (`issue_activity.delay()`)

### Real-Time Document Collaboration

1. Frontend `CollaborativeDocumentEditor` (from `@plane/editor`) establishes WebSocket to `/live/collaboration/`
2. Caddy routes `/live/*` to live server port 3000
3. `CollaborationController` (`@WebSocket("/")`) forwards to `HocusPocusServerManager`
4. Hocuspocus runs `onAuthenticate` — calls Django `/api/users/me/` to validate cookie/token
5. `Database` extension fetches document binary from Django API on connect; flushes on disconnect/debounce
6. `Redis` extension syncs Yjs awareness state across live server instances
7. `TitleSync` extension propagates title changes back to Django via service call

### Background Task Flow

1. Django view dispatches Celery task: `issue_activity.delay(type, event_data, …)`
2. RabbitMQ brokers task to Celery worker container
3. Worker executes task (sends emails, fires webhooks, creates audit log entries)
4. `celery beat` runs cron-scheduled tasks (email digest every 5 min, metrics push every 6 hours)

## Key Abstractions

**`CoreRootStore` / `RootStore`:**
- Purpose: Singleton container for all MobX domain stores; injected via `StoreContext`
- Location: `apps/web/core/store/root.store.ts` (core), `apps/web/ce/store/root.store.ts` (CE extends with `TimelineStore`)
- Pattern: Stores receive `this` (the root) as constructor arg for cross-store access

**`APIService` (abstract):**
- Purpose: Axios wrapper with `withCredentials`, 401 redirect interceptor
- Two copies: `apps/web/core/services/api.service.ts` (with 401 redirect), `packages/services/src/api.service.ts` (without — used by live/admin/space)
- Pattern: Domain services extend `APIService`, call `this.get/post/patch/delete`

**`BaseViewSet` / `BaseAPIView`:**
- Purpose: Django base classes providing auth, timezone, pagination, error handling
- Location: `apps/api/plane/app/views/base.py`
- Pattern: All API views extend one of these; `workspace_slug` and `project_id` exposed as properties

**Edition Path Alias (`@/plane-web/*`):**
- Purpose: Swap CE/EE implementations without touching core code
- Resolved via `tsconfig.json` path: `"@/plane-web/*": ["./ce/*"]`
- Pattern: Core code imports from `@/plane-web/store/...`; CE `ce/` dir provides CE implementation

**`@plane/decorators` Controller System:**
- Purpose: Decorator-based HTTP/WebSocket route registration for the live server
- Location: `packages/decorators/src/`
- Pattern: `@Controller("/path")` on class, `@Get("/sub")` / `@WebSocket("/sub")` on methods; `registerController(router, Controller, [deps])` wires them up

## Entry Points

**`apps/web` (SPA):**
- Location: `apps/web/app/root.tsx`
- Triggers: React Router hydration in browser
- Responsibilities: HTML shell, theme provider, `AppProvider` (StoreProvider → TranslationProvider → StoreWrapper → InstanceWrapper → SWRConfig)

**`apps/web` Route Tree:**
- Location: `apps/web/app/routes.ts` — merges `coreRoutes` + `extendedRoutes`
- Core routes: `apps/web/app/routes/core.ts` — all workspace/project/settings routes
- Extended routes: `apps/web/app/routes/extended.ts` — CE/EE additional routes

**`apps/api` (Django):**
- Location: `apps/api/plane/urls.py`
- Triggers: gunicorn/uvicorn ASGI workers
- Responsibilities: Routes all HTTP to correct Django app module

**`apps/live` (Node.js):**
- Location: `apps/live/src/start.ts`
- Triggers: `node src/start.ts`
- Responsibilities: Bootstraps `Server`, connects Redis, initializes Hocuspocus, registers controllers, listens on configured port

## Architectural Constraints

- **SSR:** `apps/web` and `apps/admin` are client-only SPAs (`ssr: false` in `react-router.config.ts`). `apps/space` uses SSR (`@react-router/serve`). No Next.js — all compat shims live in `apps/web/app/compat/next/` for legacy imports.
- **Global state:** One MobX `RootStore` singleton per app, initialized in `apps/web/core/lib/store-context.tsx`. `resetOnSignOut()` reinitializes all stores on logout.
- **Cross-store access:** Stores receive the root store as a constructor argument — do not use `useContext` inside store classes.
- **CE/EE isolation:** Core code must never directly import from `./ce/` or `./ee/` — always use the `@/plane-web/*` alias so the build target controls which implementation is resolved.
- **Package imports:** Apps import shared code via `@plane/*` workspace packages only, never via relative paths into `packages/`.
- **Python API is not in pnpm workspace:** `apps/api` and `apps/proxy` are excluded from the pnpm workspace (`pnpm-workspace.yaml`). They have no JS toolchain integration.
- **Turbo build order:** `build` task has `dependsOn: ["^build"]` — packages must build before apps. Packages output to `dist/`.

## Anti-Patterns

### Importing directly from `./ce/` instead of `@/plane-web/*`

**What happens:** A core file in `apps/web/core/` imports directly from `../../ce/store/something.ts`
**Why it's wrong:** Bypasses the edition alias mechanism. EE builds cannot override the import.
**Do this instead:** Import from `@/plane-web/store/something` — the tsconfig alias resolves it to the correct edition directory.

### Calling service methods from React components directly

**What happens:** A component calls `new IssueService().createIssue(...)` inside a handler
**Why it's wrong:** Bypasses MobX store — state is not updated, SWR cache is not invalidated
**Do this instead:** Call the store action: `const { createIssue } = useIssues()` → `createIssue(workspaceSlug, projectId, data)`

### Creating new stores inside component render

**What happens:** `const store = new SomeStore()` inside a component function body
**Why it's wrong:** Creates a new store on every render, discarding all accumulated state
**Do this instead:** Access via the root store: `const { someStore } = useContext(StoreContext)`

## Error Handling

**Frontend Strategy:** Global 401 interceptor in `APIService` redirects to sign-in. MobX store actions catch service errors and set observable error state. Components use `ErrorBoundary` exported from `apps/web/app/root.tsx`.

**Backend Strategy:** `BaseViewSet.handle_exception` catches `IntegrityError`, `ValidationError`, `ObjectDoesNotExist`, `KeyError` and returns typed JSON error responses with appropriate HTTP status codes. Uncaught exceptions return 500 with `"Something went wrong"`.

## Cross-Cutting Concerns

**Logging:**
- Frontend: `@plane/logger` (Winston-based) used in live server; browser apps use `console.*` only
- Backend: Python `logging` module via Django; Celery tasks log via `logger_task.py`

**Validation:**
- Frontend: `react-hook-form` with `zod` schemas at form level; store-level validation minimal
- Backend: DRF serializer validation; permission classes enforce role-based access

**Authentication:**
- Session cookie (`withCredentials: true` on all axios requests)
- Auth flows: email/password, magic link, GitHub, Google, GitLab, Gitea OAuth (all in `apps/api/plane/authentication/`)
- Live server authenticates by forwarding cookie to Django `/api/users/me/` endpoint

**i18n:**
- `@plane/i18n` package; `TranslationProvider` wraps the app; `useTranslation()` hook provides translated strings
- Locales stored in `packages/i18n/src/locales/`

---

*Architecture analysis: 2026-05-31*
