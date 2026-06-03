---
phase: 5
slug: security-hardening-agpl-gate
status: planned
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-03
updated: 2026-06-03
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Test design derived from 05-RESEARCH.md `## Validation Architecture`.

---

## Test Infrastructure

| Property                    | Value                                                                           |
| --------------------------- | ------------------------------------------------------------------------------- |
| **Framework (backend)**     | pytest (apps/api — `apps/api/pytest.ini`, `run_tests.py`, factory-boy fixtures) |
| **Framework (live server)** | Vitest 4.x (apps/live — `vitest.config.ts`, `tests/**/*.test.ts`)               |
| **Quick run command**       | `cd apps/api && python -m pytest <touched test files> -q`                       |
| **Full suite command**      | `cd apps/api && python -m pytest -q` (+ `cd apps/live && pnpm test` for SEC-02) |
| **Estimated runtime**       | < 60s for unit tests; < 120s for contract tests                                 |

---

## Sampling Rate

- **After every task commit:** Run the quick command scoped to the touched test file
- **After every plan wave:** Run the full suite for the affected app
- **Before `/gsd:verify-work`:** Full suite green + the grep/integrity gates below pass
- **Max feedback latency:** Per-task (every task has an `<automated>` verify command)

---

## Per-Task Verification Map

| Task ID  | Plan  | Wave | Requirement | Threat Ref    | Secure Behavior                                                                                                                 | Test Type              | Automated Command                                                                                                                                                                                                                                                                                                                          | File Exists        | Status     |
| -------- | ----- | ---- | ----------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------ | ---------- |
| 05-01 T1 | 05-01 | 1    | SEC-01      | T-5-01a/b/c   | Boot-time guard writes ALLOWED_HOSTS to render.yaml; guard block appended to common.py                                          | grep-gate              | `grep -n "ImproperlyConfigured\|_boot_errors" apps/api/plane/settings/common.py && grep -n "ALLOWED_HOSTS" render.yaml`                                                                                                                                                                                                                    | N/A                | ⬜ pending |
| 05-01 T2 | 05-01 | 1    | SEC-01      | T-5-01a/b/c/d | Guard raises on absent SECRET_KEY, wildcard ALLOWED_HOSTS, allow-all CORS+credentials; silent in DEBUG                          | unit                   | `cd apps/api && python -m pytest plane/tests/unit/settings/test_config_guard.py -m unit -v`                                                                                                                                                                                                                                                | ❌ W0              | ⬜ pending |
| 05-02 T1 | 05-02 | 1    | SEC-02      | T-5-02        | Four Vitest tests for auth-middleware: correct/wrong-value/wrong-length/missing (RED before fix)                                | unit                   | `cd apps/live && pnpm test -- --reporter=verbose`                                                                                                                                                                                                                                                                                          | ❌ W0              | ⬜ pending |
| 05-02 T2 | 05-02 | 1    | SEC-02      | T-5-02/b      | timingSafeEqual replaces !==; wrong-length returns 401 without RangeError; all 4 tests GREEN                                    | unit                   | `cd apps/live && pnpm test -- --reporter=verbose`                                                                                                                                                                                                                                                                                          | ❌ W0 → created T1 | ⬜ pending |
| 05-03 T1 | 05-03 | 2    | SEC-03      | T-5-03b/c     | No bare print() in 7 target files outside DEBUG guard                                                                           | grep-gate              | `grep -rn "^[[:space:]]*print(" apps/api/plane/app/views/base.py apps/api/plane/bgtasks/notification_task.py apps/api/plane/bgtasks/deletion_task.py apps/api/plane/settings/storage.py apps/api/plane/api/views/base.py apps/api/plane/space/views/base.py apps/api/plane/license/api/views/base.py \| grep -v "settings.DEBUG" \| wc -l` | N/A                | ⬜ pending |
| 05-03 T2 | 05-03 | 2    | SEC-03      | T-5-03a       | Checkpoint:decision for telemetry strategy (model default vs env-only)                                                          | checkpoint             | Human decision required                                                                                                                                                                                                                                                                                                                    | N/A                | ⬜ pending |
| 05-03 T3 | 05-03 | 2    | SEC-03      | T-5-03a/d     | is_telemetry_enabled default=False; OTLP_ENDPOINT="" in render.yaml; admin form updated; test_otlp_endpoint_not_plane_so passes | unit + grep-gate       | `cd apps/api && python -m pytest plane/tests/unit/settings/test_telemetry.py -m unit -q && grep -n "OTLP_ENDPOINT" render.yaml`                                                                                                                                                                                                            | ❌ W0              | ⬜ pending |
| 05-04 T1 | 05-04 | 2    | SEC-04      | T-5-04        | Checkpoint:decision for AGPL §13 source URL (public fork vs upstream)                                                           | checkpoint             | Human decision required                                                                                                                                                                                                                                                                                                                    | N/A                | ⬜ pending |
| 05-04 T2 | 05-04 | 2    | SEC-04      | T-5-04/b/c    | NOTICE exists with Plane Software attribution; source_disclosure view added; /source URL registered                             | grep-gate + file-check | `test -f NOTICE && grep -q "Plane Software" NOTICE && grep -c "source_disclosure" apps/api/plane/web/views.py apps/api/plane/web/urls.py`                                                                                                                                                                                                  | N/A                | ⬜ pending |
| 05-04 T3 | 05-04 | 2    | SEC-04      | T-5-04        | GET /source returns 200 with license + source + notice keys; source URL != plane.so                                             | contract               | `cd apps/api && python -m pytest plane/tests/contract/app/test_source_disclosure.py -m contract -v`                                                                                                                                                                                                                                        | ❌ W0              | ⬜ pending |
| 05-05 T1 | 05-05 | 3    | SEC-03/04   | T-5-05a/b     | Checkpoint:decision for real Bright-Byte support/docs URLs                                                                      | checkpoint             | Human decision required                                                                                                                                                                                                                                                                                                                    | N/A                | ⬜ pending |
| 05-05 T2 | 05-05 | 3    | SEC-03/04   | T-5-05a/b/c   | 16 plane.so frontend URLs replaced; AGPL /source link in auth footer; openapi.py updated                                        | grep-gate              | `grep -rn "plane\.so" apps/web/core/components/workspace/sidebar/help-section/root.tsx apps/web/core/components/power-k/config/help-commands.ts apps/web/app/layout.tsx apps/web/app/error/prod.tsx apps/admin/app/\(all\)/\(dashboard\)/sidebar-help-section.tsx \| grep -v "^[^:]*:#\|// \|/\*" \| wc -l`                                | N/A                | ⬜ pending |
| 05-05 T3 | 05-05 | 3    | SEC-03/04   | T-5-05a/b/d   | Visual confirm: /source reachable from auth footer; no plane.so links in UI; no broken surfaces                                 | human-verify           | Human checkpoint (visual + `git diff --quiet LICENSE.txt COPYRIGHT.txt`)                                                                                                                                                                                                                                                                   | N/A                | ⬜ pending |

_Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky_

---

## Wave 0 Requirements (test stubs to create BEFORE implementation)

These test files do not yet exist — they must be created (as failing/stub tests) before the implementation tasks run:

- [ ] `apps/api/plane/tests/unit/settings/test_config_guard.py` — Plan 05-01 Task 2 (SEC-01: 4 guard tests)
- [ ] `apps/live/tests/lib/auth-middleware.test.ts` — Plan 05-02 Task 1 (SEC-02: 4 auth-middleware tests; Task 1 IS the Wave 0 step)
- [ ] `apps/api/plane/tests/unit/settings/test_telemetry.py` — Plan 05-03 Task 3 (SEC-03: 1 OTLP endpoint test)
- [ ] `apps/api/plane/tests/contract/app/test_source_disclosure.py` — Plan 05-04 Task 3 (SEC-04: 2 /source contract tests)

Note: Per the plan structure, test creation and implementation are in the same plan tasks (TDD pattern with `tdd="true"` where applicable). The Wave 0 files are created within their respective plan tasks.

---

## Phase-Wide Integrity Gates (run before `/gsd:verify-work`)

These checks span all plans and must ALL pass before the phase is marked complete:

```bash
# 1. AGPL integrity (must be first — zero tolerance)
git diff --quiet LICENSE.txt COPYRIGHT.txt && echo "LICENSE CLEAN" || echo "LICENSE MODIFIED — BLOCKER"

# 2. addlicense check (same as CI copyright-check.yml)
addlicense -check -f COPYRIGHT.txt $(git ls-files '*.py' '*.ts' '*.tsx' | grep -v migrations | grep -v '\.d\.ts')

# 3. Broad print sweep (unconditional production paths)
grep -rn "print(" apps/api/plane/ --include="*.py" | grep -v "/migrations/" | grep -v "settings.DEBUG" | grep -v "# " | wc -l
# Should return 0 or only known-safe entries (management commands, test fixtures)

# 4. No telemetry.plane.so in OTLP env
grep -c "telemetry.plane.so" render.yaml
# Should return 0

# 5. /source endpoint registered
grep -c "source_disclosure" apps/api/plane/web/urls.py

# 6. NOTICE file with attribution
test -f NOTICE && grep -q "Plane Software" NOTICE && echo "NOTICE OK"

# 7. All unit tests green
cd apps/api && python -m pytest plane/tests/unit/settings/ -m unit -q
cd apps/live && pnpm test

# 8. Contract tests green
cd apps/api && python -m pytest plane/tests/contract/app/test_source_disclosure.py -m contract -q

# 9. No plane.so in frontend target files
grep -rn "plane\.so" \
  apps/web/core/components/workspace/sidebar/help-section/root.tsx \
  apps/web/core/components/power-k/config/help-commands.ts \
  apps/web/app/layout.tsx \
  apps/web/app/error/prod.tsx \
  apps/admin/app/\(all\)/\(dashboard\)/sidebar-help-section.tsx \
  | grep -v "^[^:]*:#\|// \|/\*" | wc -l
# Should return 0
```

---

## Manual-Only Verifications

| Behavior                                                                   | Requirement | Why Manual                                                                      | Test Instructions                                                                                                    |
| -------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| AGPL §13 offer is legally sufficient + points at real Corresponding Source | SEC-04      | Legal interpretation requires counsel; real source URL is a checkpoint:decision | Confirm `/source` (or footer link) resolves to the deployed version's source and counsel confirms compliance         |
| Telemetry truly silent on the live deployment                              | SEC-03      | Requires observing the deployed instance's egress in Render logs                | Confirm no outbound requests to `*.plane.so` in Render network logs after deploy                                     |
| Boot guard works on live deployment                                        | SEC-01      | Requires a Render deploy to observe the guard in action                         | Deploy without ALLOWED_HOSTS set and confirm the process fails to start; then set ALLOWED_HOSTS and confirm it boots |

---

## Nyquist Compliance Check

- [x] All tasks have `<automated>` verify commands OR are checkpoint tasks
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (checkpoints count as verified steps)
- [x] Wave 0 test stubs are created within their respective plan tasks (TDD approach)
- [x] No watch-mode flags in any verify command
- [x] Feedback latency target: per-task (< 60s for unit tests)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending execution

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or are checkpoint:decision/human-verify tasks
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING test references
- [x] No watch-mode flags
- [x] Feedback latency target set (per-task)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
