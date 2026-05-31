# Concerns

**Analysis Date:** 2026-05-31

This document catalogs technical debt, known issues, security concerns, and fragile areas. File:line references are verified against the codebase at HEAD `3f57fefdb4`. Counts are exact at analysis time and will drift.

## Tech Debt

### 1. Next.js → React Router migration incomplete
The web app is mid-migration from Next.js to React Router (Vite). Compatibility shims live at `apps/web/app/compat/next/` and are wired via Vite aliases in `apps/web/vite.config.ts` (`next/link`, `next/navigation`, `next/script`).
- **260+ files** in `apps/web/core/` still import from `next/navigation` / `next/link`, resolved only through the compat shims.
- `next/image` is **not** aliased — currently no usages remain, so it is latent rather than broken, but any reintroduced `next/image` import would fail to resolve.

### 2. CE/EE boundary leakage
**200+ files** (330+ import statements) inside `apps/web/core/` import from `@/plane-web` (the edition seam → `apps/web/ce/`). `core/` is supposed to stay edition-agnostic. One leak is explicitly TODO-flagged at `apps/web/core/components/issues/issue-detail/label/root.tsx`. See [[STRUCTURE]] for the `@/plane-web` alias.

### 3. Permission enum migration stalled
`apps/web/core/store/user/base-permissions.store.ts:29` defines a stop-gap union type with an explicit removal TODO:
```typescript
type ETempUserRole = TUserPermissions | EUserWorkspaceRoles | EUserProjectRoles; // TODO: Remove this once we have migrated user permissions to enums to plane constants package
```

### 4. Export task bypasses file-asset table
`apps/api/plane/bgtasks/export_task.py:40` — `upload_to_s3` is TODO-flagged to migrate to the new storage method with a file-asset-table entry:
```python
# TODO: Change the upload_to_s3 function to use the new storage method with entry in file asset table
```

### 5. IssueCreateSerializer ManyToMany pattern acknowledged suboptimal
`apps/api/plane/app/serializers/issue.py` (above `IssueCreateSerializer`, ~line 79):
```python
##TODO: Find a better way to write this serializer
## Find a better approach to save manytomany?
```

### 6. Unstable type re-export
`packages/types/src/index.ts:32` re-exports a transitional module:
```typescript
export * from "./issues/base"; // TODO: Remove this after development and the refactor/mobx-store-issue branch is stable
```

### 7. Deprecated legacy theme module
`packages/utils/src/theme-legacy.ts` ("Legacy Theme System") is still part of the `@plane/utils` surface.

### 8. Clipboard fallback debt
`document.execCommand("copy")` deprecated fallback present in **2 files** under `apps/web`/`packages`.

### General marker density
~60 `TODO/FIXME/HACK/XXX` markers in `apps/web/core` TypeScript alone — a useful proxy for accumulated intent-to-revisit debt.

## Known Bugs / Risk Areas

### 1. Cycle hard-delete
`apps/api/plane/app/views/cycle/base.py:501` performs `cycle.delete()` (hard delete). Combined with the related `.delete()` at line 509, this risks breaking OneToOne/related-record integrity rather than soft-deleting.

### 2. Route-coupled UI state
Several UI behaviors derive from route path strings (empty states, mobile header), making them brittle to route renames — e.g. profile/view empty states keyed off route param names.

### 3. Unsaved-changes guard bypass
Browser back/forward navigation can bypass the unsaved-changes guard in form flows.

### 4. Estimate key uniqueness
Estimate key uniqueness is not validated, allowing potential duplicate keys.

## Security Concerns

> Context: recent git history shows active SSRF hardening (`fix: harden webhook/link/OAuth-avatar SSRF (#9163)`) and rate-limit work. Several items below are insecure **defaults** intended to be overridden in production via env vars — but they are footguns if deployed unconfigured.

### 1. Permissive `ALLOWED_HOSTS` default
`apps/api/plane/settings/common.py:76`:
```python
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")
```
Defaults to `*` if the env var is unset.

### 2. CORS allow-all fallback with credentials
`apps/api/plane/settings/common.py:163` sets `CORS_ALLOW_CREDENTIALS = True`, and line 171 has a `CORS_ALLOW_ALL_ORIGINS = True` fallback path. Allow-all origins + credentials is a dangerous combination if the fallback is hit.

### 3. Ephemeral `SECRET_KEY`
`apps/api/plane/settings/common.py:29`:
```python
SECRET_KEY = os.environ.get("SECRET_KEY", get_random_secret_key())
```
If `SECRET_KEY` is unset, a new key is generated on every restart — invalidating sessions/tokens and breaking signed-value continuity.

### 4. Non-constant-time secret comparison (live server)
`apps/live/src/lib/auth-middleware.ts:34` is annotated `// TODO - Move to hmac` and compares the secret with `!==`:
```typescript
if (!secretKey || secretKey !== env.LIVE_SERVER_SECRET_KEY) { ... }
```
Should use a timing-safe comparison (`crypto.timingSafeEqual`).

### 5. Suppressed CVE (mitigation confirmed)
`.trivyignore` suppresses `CVE-2026-30242` (SSRF in webhook URL serializer). The rationale is documented as a false-positive/already-mitigated case — **not** an unaddressed vulnerability, but worth re-confirming on dependency bumps.

### 6. `print()` in backend code
**13 Python files** under `apps/api/plane` contain `print(...)` calls — some in error/exception paths. These bypass structured logging (`@plane/logger` / Django logging — see [[CONVENTIONS]]) and can leak detail to stdout.

### 7. Loose `Promise<any>` service typings
Service methods in `packages/services/src` return `Promise<any>` (e.g. `ai/ai.service.ts:47`, `auth/auth.service.ts:94`, `auth/sites-auth.service.ts:48`), erasing response-shape safety at API boundaries.

## Performance / Scaling

### Oversized modules (hard to maintain, slow to load/parse)
| File | Lines |
|---|---|
| `apps/api/plane/api/views/issue.py` | 2542 |
| `apps/web/core/store/issue/helpers/base-issues.store.ts` | 1965 |
| `apps/api/plane/bgtasks/issue_activities_task.py` | 1604 |

These are the dominant hotspots; the issue domain concentrates the most complexity across both backend and frontend.

### Other
- Debug-only query-count instrumentation present (acceptable, but noise in prod if toggled).
- Issue activity background processing (`issue_activities_task.py`) is large and synchronous-heavy — a scaling watch item.

## Fragile Areas (handle with care)

- The CE/EE alias seam (`@/plane-web`) — changes ripple across 200+ files.
- The Next.js compat shims (`apps/web/app/compat/next/`) — removing them prematurely breaks 260+ importers.
- Issue domain stores/views (the 1500–2500 line files above).
- Settings defaults (`apps/api/plane/settings/common.py`) — insecure-by-default values rely on correct env configuration.
- Cycle deletion path (hard delete with related cascades).

## Test Coverage Gaps

(See [[TESTING]] for full detail.)
- **No CI test execution** — PR workflows run only lint + type checks; no `pytest`/`vitest`/`turbo run test` step exists.
- **No frontend tests** — `apps/web`, `apps/admin`, `apps/space` have zero test files.
- **Only 4 TS test files** repo-wide (all in `apps/live` and `packages/codemods`).
- Most `@plane/*` packages (`ui`, `utils`, `hooks`, `services`, `types`, `editor`) are untested.
- The most complex modules (issue views/stores) have no direct unit coverage.

## Notes on Defaults vs. Real Issues

Several "security" items (1–3) are **insecure defaults** meant to be overridden by env vars in production deployments (see `.env.example` and the docker-compose files). They are flagged as concerns because they fail open if misconfigured, not because the shipped production config is necessarily vulnerable. Item 4 (non-constant-time comparison) and item 6 (`print()`) are genuine code-level issues regardless of deployment config.

---

*Concerns analysis: 2026-05-31*
