# Coding Conventions

**Analysis Date:** 2026-05-31

## File Headers

Every TypeScript/JavaScript and Python source file must begin with the AGPL license header. This is enforced by the `copyright-check.yml` CI workflow using `addlicense`.

**TypeScript/JS header:**
```typescript
/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */
```

**Python header:**
```python
# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.
```

## Naming Patterns

### TypeScript / JavaScript

**Files:**
- React components: `kebab-case.tsx` (e.g., `cycle-list-group-header.tsx`, `delete-modal.tsx`)
- Stores: `kebab-case.store.ts` (e.g., `cycle.store.ts`, `analytics.store.ts`)
- Services: `kebab-case.service.ts` (e.g., `api.service.ts`, `cycle.service.ts`)
- Hooks: `use-kebab-case.ts` / `.tsx` (e.g., `use-multiple-select.ts`)
- Types files: `kebab-case.ts` (e.g., `navigation-preferences.ts`)
- Specs: `kebab-case.spec.ts`, tests: `kebab-case.test.ts`

**Functions:**
- camelCase for all regular functions and hooks (e.g., `renderFormattedPayloadDate`, `useMultipleSelect`)
- Function declarations for React components (not arrow functions assigned to `const`): `export function CycleForm(props: Props) { ... }`
- Observer-wrapped components use: `export const MyComponent = observer(function MyComponent(props: Props) { ... })`
- CONSTANT_CASE for module-level constant identifiers that are NOT React components (e.g., `DEFAULT_PERSONAL_PREFERENCES`, `PDF_HEADER`)

**Variables:**
- camelCase for local variables and parameters
- Unused parameters/variables prefixed with `_` (enforced by oxlint: `argsIgnorePattern: "^_"`)

**Types and Interfaces:**
- Types: `T` prefix — `TNavigationPreferences`, `TCyclePlotType`, `TProgressSnapshot`
- Interfaces: `I` prefix — `IWorkspace`, `ICycle`, `IEstimate`, `ICycleStore`
- Enums: `E` prefix — `ETabIndices`, `EWidgetKeys`, `EIssueGroupedAction`
- Avoid `enum` where possible; prefer `const` objects or union types per `.github/instructions/typescript.instructions.md`

**React Props types:**
- Local `type Props = { ... }` or named `type T<ComponentName>Props` pattern

### Python

**Files:** `snake_case.py` (e.g., `test_db_routing.py`, `test_authentication.py`)

**Classes:** PascalCase — test classes prefixed with `Test` (e.g., `TestReadReplicaRoutingMiddleware`)

**Functions/methods:** `snake_case`, test functions prefixed with `test_` (e.g., `test_middleware_initialization`)

## Code Style

### Formatting (TypeScript/JavaScript)

**Tool:** `oxfmt` v0.35.0  
**Config:** `.oxfmtrc.json` (root)

Key settings:
- `printWidth`: 120 characters
- `tabWidth`: 2 spaces
- `trailingComma`: `"es5"` (trailing commas in multi-line constructs)
- Tailwind class sorting enabled: `sortTailwindcss` using `packages/tailwind-config/index.css` as stylesheet
- Functions sorted by: `cn`, `clsx`, `cva`
- Exception: `packages/codemods/**/*` uses `printWidth: 80`

### Formatting (Python)

**Tool:** Ruff (via `ruff format`)  
**Config:** `apps/api/pyproject.toml`

Key settings:
- `line-length`: 120
- `indent-width`: 4
- `quote-style`: double quotes
- `indent-style`: spaces

### Linting (TypeScript/JavaScript)

**Tool:** `oxlint` v1.51.0  
**Config:** `.oxlintrc.json` (root)

Active plugins: `react`, `typescript`, `jsx-a11y`, `import`, `promise`, `unicorn`, `oxc`

Active rule categories (all `"warn"`): `correctness`, `suspicious`, `perf`

Key rules:
- `react/react-in-jsx-scope`: off (React 18 JSX transform)
- `react/prop-types`: off (TypeScript covers this)
- `unicorn/filename-case`: off
- `unicorn/no-null`: off
- `unicorn/prevent-abbreviations`: off
- `no-unused-vars`: warn, with `_` prefix ignore pattern for args/vars/caught errors/destructured arrays

Per-app max-warnings thresholds (each app runs `oxlint --max-warnings=<N> .`):
- `apps/web`: 11957
- `apps/admin`: 759
- `apps/space`: 676
- `apps/live`: 119
- `packages/propel`: 3605

### Linting (Python)

**Tool:** Ruff (`ruff check`)  
**Config:** `apps/api/pyproject.toml`

Active rules: `E` (pycodestyle), `F` (Pyflakes)  
Complexity: `max-complexity = 10`, `max-args = 8`, `max-statements = 50`  
Import sort: first-party `plane`, third-party `rest_framework`, relative imports banned from parent packages

## Import Organization

**TypeScript — standard grouping order (comment-separated):**

1. External packages (no comment) — e.g., `import { isPast } from "date-fns"`
2. `@plane/*` workspace packages — grouped by subpackage, with `// types`, `// helpers`, `// ui`, `// plane imports` comments
3. App-local imports via `@/` alias — with `// components`, `// services`, `// hooks`, `// store` comments

Example from `apps/web/core/store/cycle.store.ts`:
```typescript
import { isPast, isToday } from "date-fns";
import { sortBy, set, isEmpty } from "lodash-es";
import { action, computed, observable, makeObservable, runInAction } from "mobx";
import { computedFn } from "mobx-utils";
// types
import type { ICycle, TCyclePlotType } from "@plane/types";
import type { DistributionUpdates } from "@plane/utils";
import { orderCycles, getDate } from "@plane/utils";
// services
import { CycleService } from "@/services/cycle.service";
// store
import type { CoreRootStore } from "./root.store";
```

**`import type` is mandatory for type-only imports** — enforced by `verbatimModuleSyntax: true` in `packages/typescript-config/base.json`.

**Path Aliases:**
- `@/` → app root (e.g., `apps/web/`) for in-app imports
- `@plane/*` → workspace packages via `pnpm-workspace.yaml`

**Python imports** follow Ruff isort: stdlib → third-party → first-party (`plane`) → relative (same package only, no parent-relative imports).

## TypeScript Usage

TypeScript v5.8.3 with strict settings from `packages/typescript-config/base.json`:
- `strict: true`
- `exactOptionalPropertyTypes: true` — no implicit `undefined` on optional props
- `noImplicitReturns: true`
- `noUnusedLocals: true` / `noUnusedParameters: true`
- `verbatimModuleSyntax: true` — requires `import type` for type-only imports
- `isolatedModules: true`
- `noImplicitOverride: true`
- `moduleResolution: "bundler"` for frontend apps

Modern TS 5.x features per `.github/instructions/typescript.instructions.md`:
- Use `satisfies` operator for type validation without widening
- Prefer `const` objects and union types over `enum` (especially for `--erasableSyntaxOnly` compatibility)
- Use `import type` explicitly for all type imports
- Use `NoInfer<T>` to block inference for specific type arguments
- Use standard decorators (Stage 3), not legacy `experimentalDecorators`

## React Component Patterns

**Function declarations** (not arrow-function-assigned-to-const) for plain components:
```typescript
export function CycleForm(props: Props) { ... }
```

**Observer-wrapped components** (MobX) use named function expressions inside `observer()`:
```typescript
export const CycleDeleteModal = observer(function CycleDeleteModal(props: ICycleDelete) { ... });
```

**MobX stores** are classes using `makeObservable` with explicit `observable`/`action`/`computed` decorators. Store interfaces prefixed with `I` (e.g., `ICycleStore`).

**Tailwind classnames** always use the `cn()` utility from `@plane/utils` (not raw `clsx`). The `oxfmt` formatter auto-sorts Tailwind classes in `cn()`, `clsx()`, and `cva()` calls.

## Error Handling

**TypeScript services** use `.catch((error) => { throw error; })` chaining on axios calls (pattern in `apps/web/core/services/cycle.service.ts`) or `try/catch` blocks.

The abstract `APIService` (`apps/web/core/services/api.service.ts`) intercepts 401 responses globally and redirects to the sign-in page. Individual service methods propagate errors via `Promise.reject`.

**Python (Django API)** uses DRF exception handling. Tests mock external services with `unittest.mock.patch`.

**Effect-based error handling** (in `apps/live`): Uses the `effect` library with `Effect.gen`, `Effect.fail`, `Either`, and custom error types like `PdfTimeoutError` from `apps/live/src/schema/pdf-export.ts`. Utility wrappers live in `apps/live/src/services/pdf-export/effect-utils.ts`.

## Logging

**TypeScript (Node):** Winston via `@plane/logger` package (`packages/logger/src/config.ts`). Log level from `process.env.LOG_LEVEL` (default `"info"`). Structured JSON output via `format.json()`. Express middleware via `loggerMiddleware` from `packages/logger/src/middleware.ts`.

**Python:** Standard Django logging. No special wrapper.

## Comments

**When to Comment:**
- Section dividers within import blocks: `// types`, `// services`, `// store`, `// hooks`, `// components`
- Inline explanation for non-obvious logic
- JSDoc/TSDoc only on exported public APIs in `packages/`

**Python:** Google-style docstrings (`convention = "google"` in ruff). Fixtures have docstrings explaining their purpose.

## Commit Conventions

Commits follow Conventional Commits with optional scope and optional work item ID prefix:

```
[WORK-1234] type(scope): short description (#PR)
```

Types: `feat`, `fix`, `chore`, `refactor`, `docs`, `perf`  
Scope (optional): `api`, `web`, `i18n`, `deps`, `nginx`, `aio`  
Work item ID (optional): `[WEB-7447]`, `[GIT-174]` as prefix

Examples from recent git log:
- `fix: harden webhook/link/OAuth-avatar SSRF`
- `refactor(api): source API_KEY_RATE_LIMIT from settings`
- `[WEB-7447] feat: migrate CE telemetry from OTLP traces to OTLP metrics`
- `chore(deps): bump axios, uuid and add security overrides`

## Module Design

**Barrel files:** Used within `packages/` — e.g., `packages/logger/src/index.ts` re-exports from `./config` and `./middleware`. Also used in component subdirectories within apps (e.g., `apps/web/core/components/estimates/index.ts`).

**Exports:** Named exports preferred over default exports for components and utilities. Default exports are reserved for route modules and config files.

**Package naming:** All workspace packages use `@plane/<name>` scope (e.g., `@plane/types`, `@plane/ui`, `@plane/logger`).

---

*Convention analysis: 2026-05-31*
