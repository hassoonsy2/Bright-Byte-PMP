# Testing

**Analysis Date:** 2026-05-31

## Overview

The monorepo has **two distinct test stacks**, split by language:

- **Python / Django** (`apps/api`) — pytest + pytest-django. This is the most developed test suite (~25 `test_*.py` files across unit/contract/smoke layers).
- **TypeScript / Node** — Vitest, but only in two locations: `apps/live` and `packages/codemods`.

> **Critical gap:** The frontend apps (`apps/web`, `apps/admin`, `apps/space`) and most shared packages have **no test files**. There are only **4 TS/JS test files** in the entire repo. See [[CONCERNS]] for the test-coverage gap analysis.

> **Critical gap:** **CI does not run any tests.** The PR workflows (`.github/workflows/pull-request-build-lint-api.yml`, `pull-request-build-lint-web-apps.yml`) run only linting (`ruff check`, `oxlint`) and type checks (`tsc --noEmit`). No `pytest`, `vitest`, or `turbo run test` step exists in any workflow. Tests must be run manually.

## Python (Django API) — Primary Suite

### Framework

- **pytest** with `pytest-django`
- Config: `apps/api/pytest.ini`
- Settings module: `plane.settings.test` (`DJANGO_SETTINGS_MODULE`)

### pytest.ini configuration

```ini
[pytest]
DJANGO_SETTINGS_MODULE = plane.settings.test
python_files = test_*.py
python_classes = Test*
python_functions = test_*

markers =
    unit: Unit tests for models, serializers, and utility functions
    contract: Contract tests for API endpoints
    smoke: Smoke tests for critical functionality
    slow: Tests that are slow and might be skipped in some contexts

addopts =
    --strict-markers
    --reuse-db
    --nomigrations
    -vs
```

Key behaviors:
- `--reuse-db` — reuses the test database between runs for speed
- `--nomigrations` — builds schema directly from models, skipping migrations
- `--strict-markers` — unregistered markers raise an error

### Test structure

Tests live under `apps/api/plane/tests/`, organized by **test type**:

```
apps/api/plane/tests/
├── conftest.py              # Shared fixtures
├── smoke/                   # Critical-path smoke tests
│   └── test_auth_smoke.py
├── unit/                    # Models, serializers, utils, middleware
│   ├── middleware/          # test_db_routing.py, test_logger.py
│   ├── settings/            # test_retention.py, test_storage.py
│   ├── utils/               # test_url.py, test_uuid.py
│   ├── models/              # test_issue_comment_modal.py, test_workspace_model.py
│   ├── bg_tasks/            # test_url_security.py, test_ssrf_advisories.py, etc.
│   └── serializers/         # test_label.py, test_workspace.py, test_issue_recent_visit.py
└── contract/                # API endpoint contract tests
    ├── app/                 # test_workspace_app.py, test_authentication.py, test_project_app.py, test_api_token.py
    └── api/                 # test_cycles.py, test_labels.py, test_projects.py
```

Note: several `bg_tasks` tests are security-focused (`test_url_security.py`, `test_ssrf_advisories.py`, `test_work_item_link_task.py`) — they back the recent SSRF-hardening work (see git log and [[CONCERNS]]).

### Fixtures & mocking

Fixtures are defined in `apps/api/plane/tests/conftest.py`:
- `django_db_setup` (session-scoped) — DB bootstrap
- `api_client` — unauthenticated `rest_framework.test.APIClient`
- `user_data` / `create_user` — standard test user (`test@plane.so`)
- `api_token` — `APIToken` instance for external-API auth tests

All fixtures carry Google-style docstrings. External services are mocked with `unittest.mock.patch` (per [[CONVENTIONS]]).

### Running Python tests

- Wrapper: `apps/api/run_tests.sh` → delegates to `apps/api/tests/run_tests.sh`
- Python runner: `apps/api/run_tests.py`
- Direct: `cd apps/api && pytest` (uses `pytest.ini` defaults)
- Test DB stack: see `docker-compose-test.yml` at repo root

## TypeScript (Vitest)

### apps/live

- Config: `apps/live/vitest.config.ts`
- Environment: `node`, `globals: true`
- Includes: `tests/**/*.test.ts`, `tests/**/*.spec.ts`
- Coverage: v8 provider, reporters `text` / `json` / `html`, covers `src/**/*.ts`
- Path alias: `@` → `./src`
- Scripts (`apps/live/package.json`):
  - `test` → `vitest run`
  - `test:watch` → `vitest`
  - `test:coverage` → `vitest run --coverage`
- Test files:
  - `apps/live/tests/lib/pdf/pdf-rendering.test.ts`
  - `apps/live/tests/services/pdf-export/effect-utils.test.ts`

### packages/codemods

- Config: `packages/codemods/vitest.config.ts` (environment `node`)
- Script: `test` → `vitest run`
- Test files (`.spec.ts`):
  - `packages/codemods/tests/remove-directives.spec.ts`
  - `packages/codemods/tests/function-declaration.spec.ts`

These validate the jscodeshift codemods used in the Next.js → React Router migration.

### Frontend apps (web / admin / space)

`apps/web/vite.config.ts`, `apps/admin/vite.config.ts`, and `apps/space/vite.config.ts` are **build-only** Vite configs (React Router) — they contain **no `test` block** and have **no test files**. There is no component/unit test harness wired for the frontend.

## Test naming conventions

- **Python:** files `test_*.py`, classes `Test*`, functions `test_*` (enforced by `pytest.ini`)
- **TypeScript:** `*.test.ts` / `*.test.tsx` (apps/live), `*.spec.ts` (codemods). Per [[CONVENTIONS]], both `.test.` and `.spec.` suffixes are the documented patterns.

## Turbo pipeline

`turbo.json` defines a `test` task:

```json
"test": {
  "dependsOn": ["^build"],
  "outputs": []
}
```

`turbo run test` would run tests in any package exposing a `test` script (currently only `apps/live` and `packages/codemods`). **No CI workflow invokes this task.**

## Coverage gaps (summary)

- No frontend test coverage (`apps/web`, `apps/admin`, `apps/space`)
- Most shared packages (`ui`, `utils`, `hooks`, `services`, `types`, `editor`, etc.) have no tests
- CI runs no tests at all — regressions are caught only by lint/type checks or manual runs
- See [[CONCERNS]] → "Test Coverage Gaps" for the detailed breakdown

---

*Testing analysis: 2026-05-31*
