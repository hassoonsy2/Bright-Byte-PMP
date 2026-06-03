---
phase: 05-security-hardening-agpl-gate
plan: "02"
subsystem: live-server
tags: [security, tdd, timing-safe, auth-middleware, node-crypto]
dependency_graph:
  requires: []
  provides: [timing-safe-secret-compare]
  affects: [apps/live/src/lib/auth-middleware.ts]
tech_stack:
  added: []
  patterns: [tdd-red-green, vi.hoisted-mock, node:crypto-timingSafeEqual]
key_files:
  created:
    - apps/live/tests/lib/auth-middleware.test.ts
  modified:
    - apps/live/src/lib/auth-middleware.ts
decisions:
  - "Use vi.hoisted() to hoist mock factory before vi.mock — required for ESM module mocking in Vitest"
  - "Rename inner vi.hoisted variable to avoid no-shadow oxlint warning"
  - "Use vi.mocked(next) cast pattern to satisfy NextFunction type without unsafe any"
  - "node:crypto prefix (not bare crypto) — consistent with Node 22 ESM best practices"
metrics:
  duration_seconds: 559
  completed: "2026-06-03"
  tasks_completed: 2
  files_changed: 2
---

# Phase 05 Plan 02: Timing-Safe Secret Compare Summary

**One-liner:** Replaced string `!==` timing oracle with `crypto.timingSafeEqual` + length pre-check using Node built-in, closing SEC-02 vulnerability.

## What Was Done

### Task 1 (RED) — Commit `1342edca66`

Created `apps/live/tests/lib/auth-middleware.test.ts` with 5 Vitest unit tests covering:

1. Correct secret → `next()` called, no 401
2. Wrong-value same-length token → 401, `next()` not called
3. Wrong-length token → 401, `next()` not called, no `RangeError` thrown
4. Missing header → 401, `next()` not called
5. `timingSafeEqual` invoked for same-length secrets (the RED gate — fails against `!==` implementation)

The 5th test used `vi.mock("node:crypto", ...)` + `vi.hoisted()` to assert `timingSafeEqual` is called. This test was RED against the original `!==` implementation.

### Task 2 (GREEN) — Commit `51c7c22fe5`

Modified `apps/live/src/lib/auth-middleware.ts`:

- Added `import { timingSafeEqual } from "node:crypto";`
- Replaced `const secretKey = req.headers[...]; if (!secretKey || secretKey !== env.LIVE_SERVER_SECRET_KEY)` with timing-safe implementation
- Length pre-check (`provided.length === expected.length`) before `timingSafeEqual` prevents `RangeError` on mismatched-length inputs
- `try/catch` around `timingSafeEqual` as defensive safety net
- Removed `// TODO - Move to hmac` comment
- Also fixed test file: `vi.hoisted()` for mock factory, `vi.mocked(next)` for TypeScript type safety

All 5 auth-middleware tests pass GREEN. All 37 live server tests pass.

## Phase Gate Results

| Gate | Check                                                      | Result   |
| ---- | ---------------------------------------------------------- | -------- |
| 1    | `grep -c "timingSafeEqual" auth-middleware.ts` ≥ 1         | PASS (2) |
| 2    | `grep -n "secretKey !== env" auth-middleware.ts` returns 0 | PASS     |
| 3    | `grep -c 'from "node:crypto"' auth-middleware.ts` = 1      | PASS (1) |
| 4    | All 5 Vitest tests pass (0 failed)                         | PASS     |
| 5    | `pnpm exec tsc --noEmit` exits 0                           | PASS     |
| 6    | AGPL header byte-identical                                 | PASS     |
| 7    | `git diff --quiet LICENSE.txt COPYRIGHT.txt` exits 0       | PASS     |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Vitest vi.mock hoisting with variable reference**

- **Found during:** Task 1 verification run
- **Issue:** `vi.mock` factory function is hoisted before variable initialization. Initial test used `TEST_SECRET` constant directly in mock factory causing `ReferenceError: Cannot access 'TEST_SECRET' before initialization`.
- **Fix:** Used literal string `"test-secret-key-fixed-length-32c"` in mock factory (documented with comment explaining duplication reason).
- **Files modified:** `apps/live/tests/lib/auth-middleware.test.ts`

**2. [Rule 1 - Bug] ESM cannot spy on node:crypto exports**

- **Found during:** Task 1 verification run (first attempt used `vi.spyOn(nodeCrypto, "timingSafeEqual")`)
- **Issue:** `TypeError: Cannot spy on export "timingSafeEqual". Module namespace is not configurable in ESM.`
- **Fix:** Switched to `vi.mock("node:crypto", ...)` with a `vi.hoisted()` mock function so the RED/GREEN gate works correctly.
- **Files modified:** `apps/live/tests/lib/auth-middleware.test.ts`

**3. [Rule 1 - Bug] no-shadow oxlint violation in vi.hoisted factory**

- **Found during:** Task 2 pre-commit hook
- **Issue:** Inner variable `mockTimingSafeEqual` inside `vi.hoisted(() => { const mockTimingSafeEqual = ... })` shadows the destructured outer variable of the same name.
- **Fix:** Renamed inner variable to `fn` and returned as `{ mockTimingSafeEqual: fn }`.
- **Files modified:** `apps/live/tests/lib/auth-middleware.test.ts`
- **Commit:** `51c7c22fe5`

**4. [Rule 1 - Bug] TypeScript type error — vi.fn() not assignable to NextFunction**

- **Found during:** Task 2 TypeScript compile check
- **Issue:** `vi.fn()` mock does not satisfy Express `NextFunction` type signature `(err?: any): void`.
- **Fix:** Added `import type { NextFunction } from "express"`, typed `next` as `NextFunction`, cast `vi.fn() as unknown as NextFunction`, and used `vi.mocked(next)` for assertions.
- **Files modified:** `apps/live/tests/lib/auth-middleware.test.ts`
- **Commit:** `51c7c22fe5`

## Known Stubs

None. The implementation is complete and wired.

## Threat Flags

No new security surfaces introduced. SEC-02 (T-5-02 timing oracle) mitigated as planned.

## Self-Check: PASSED

- `apps/live/src/lib/auth-middleware.ts` — modified, contains `timingSafeEqual` ✓
- `apps/live/tests/lib/auth-middleware.test.ts` — created, contains 5 tests ✓
- RED commit `1342edca66` exists ✓
- GREEN commit `51c7c22fe5` exists ✓
- All 37 live server tests pass ✓
- TypeScript strict-mode compiles clean ✓
- AGPL header unchanged ✓
