---
phase: 05-security-hardening-agpl-gate
plan: "03"
subsystem: api-backend
tags: [security, telemetry, logging, privacy, django-migration, render]
dependency_graph:
  requires: []
  provides: [telemetry-disabled-by-default, print-free-backend, source-availability-url-env]
  affects:
    - apps/api/plane/license/models/instance.py
    - apps/api/plane/app/views/base.py
    - render.yaml
    - apps/admin/app/(all)/(dashboard)/general/form.tsx
tech_stack:
  added: []
  patterns: [stdlib-logging, log_exception, django-alterfield-migration, env-var-override]
key_files:
  created:
    - apps/api/plane/license/migrations/0007_disable_telemetry_default.py
    - apps/api/plane/tests/unit/settings/test_telemetry.py
  modified:
    - apps/api/plane/app/views/base.py
    - apps/api/plane/bgtasks/notification_task.py
    - apps/api/plane/bgtasks/deletion_task.py
    - apps/api/plane/settings/storage.py
    - apps/api/plane/api/views/base.py
    - apps/api/plane/space/views/base.py
    - apps/api/plane/license/api/views/base.py
    - apps/api/plane/license/models/instance.py
    - render.yaml
    - apps/admin/app/(all)/(dashboard)/general/form.tsx
decisions:
  - "Checkpoint resolved option-a-schema-migration: model default=False + Django migration 0007, not env-var-only"
  - "Existing Instance rows left for manual admin toggle (no data migration) — new deployments boot correct"
  - "Admin form: removed the dead developers.plane.so docs link entirely rather than pointing it at href='#' (cleaner than plan's suggestion)"
  - "OTLP_ENDPOINT='' in render.yaml overrides the hardcoded telemetry.plane.so fallback without deleting the beat task"
metrics:
  completed: "2026-06-04"
  tasks_completed: 3
  files_changed: 12
  commits: 2
---

# Phase 05 Plan 03: Print Cleanup + Telemetry Disable Summary

**One-liner:** Removed all bare `print()` from production-reachable Python paths and stopped new instances from phoning home to `telemetry.plane.so` (model default off + `OTLP_ENDPOINT=""`), closing SEC-03.

## What Was Done

### Task 1 (print → logger) — Commit `a542bb0dc9`

Replaced bare `print()` calls across seven backend modules:

- `app/views/base.py:79` — `print(e, traceback.format_exc())`/`print("Server Error")` → `log_exception(e)`; DEBUG query-count prints → `logger.debug(...)`
- `bgtasks/notification_task.py:673` — `print(e)` → `logger.exception(...)` (added module logger)
- `bgtasks/deletion_task.py:99` — `print(...)` → `logger.error(...)` (added module logger)
- `settings/storage.py:96` — `print(...)` → `log_exception(e)`
- `api/views/base.py`, `space/views/base.py`, `license/api/views/base.py` — DEBUG-gated query-count prints → `logger.debug(...)`

Verification grep returns **0** unconditional prints in the four critical files.

### Task 2 (checkpoint:decision) — Telemetry disable strategy

Resolved **option-a-schema-migration**: change the model default _and_ generate a Django migration, rather than the env-var-only path. Existing `Instance` rows are left for manual admin toggle (no data migration) — the intent is correct-by-default for all new deployments.

### Task 3 (telemetry disable + test) — Commit `09db8a5b5b`

- `license/models/instance.py:35` — `is_telemetry_enabled` default `True` → `False`
- `license/migrations/0007_disable_telemetry_default.py` — `AlterField` migration (applied by the `migrator` preDeploy service on next Render deploy)
- `render.yaml` — added `OTLP_ENDPOINT: ""` (disables phone-home) and `SOURCE_AVAILABILITY_URL: https://github.com/makeplane/plane` (consumed by Plan 05-04's `/source` endpoint)
- `admin/.../general/form.tsx` — consent text → "Allow Bright-Byte PMP to send anonymous usage data to our servers"; dead `developers.plane.so` telemetry-policy link removed
- `tests/unit/settings/test_telemetry.py` — 2 unit tests asserting `OTLP_ENDPOINT` override never resolves to a `plane.so` host

## Phase Gate Results

| Gate | Check                                            | Result          |
| ---- | ------------------------------------------------ | --------------- |
| 1    | No unconditional prints in 4 critical files      | PASS (0)        |
| 3    | `is_telemetry_enabled` default=False             | PASS            |
| 4    | `OTLP_ENDPOINT` in render.yaml                   | PASS            |
| 5    | `SOURCE_AVAILABILITY_URL` in render.yaml         | PASS            |
| 6    | Telemetry unit tests                             | PASS (2 passed) |
| 7    | Admin form: no "Let Plane" / developers.plane.so | PASS            |
| 8    | `git diff --quiet LICENSE.txt COPYRIGHT.txt`     | PASS            |

## Deviations from Plan

**1. Admin docs link removed instead of pointed at `href="#"`**

- **Plan said:** change `href="https://developers.plane.so/self-hosting/telemetry"` to `href="#"`.
- **Actual:** removed the `<a>` element entirely and reworded the surrounding sentence. A dead anchor (`href="#"`) is a worse UX than no link; no Bright-Byte telemetry docs page exists yet. Semantics preserved, brand corrected. Net better outcome.

**2. Local test run requires `REDIS_URL`**

- Running `pytest` under `plane.settings.test` triggers Django init which calls `redis_instance()`; with no `REDIS_URL` set locally it raises before any test runs. This is a **pre-existing env limitation** (the Plan-01 `test_config_guard.py` fails identically) — CI supplies `REDIS_URL`. Both telemetry tests pass with a dummy `REDIS_URL` set. No code change required.

## Known Stubs

- `SOURCE_AVAILABILITY_URL` defaults to upstream `makeplane/plane`; the real Bright-Byte fork URL is a checkpoint:decision owned by Plan 05-04 (`/source` endpoint).
- Existing `Instance` rows with `is_telemetry_enabled=True` are not bulk-flipped — admin toggles off in UI if a row predates this change.

## Threat Flags

SEC-03 mitigated: T-5-03a (telemetry phone-home), T-5-03b/c (print stack-trace disclosure), T-5-03d (misleading admin telemetry brand) all closed. No new packages (stdlib `logging` only).

## Self-Check: PASSED

- All seven Python files print-free outside DEBUG guards ✓
- `is_telemetry_enabled` default=False + migration 0007 ✓
- render.yaml OTLP_ENDPOINT="" + SOURCE_AVAILABILITY_URL ✓
- Admin consent rebranded, dead link removed ✓
- 2 telemetry unit tests pass ✓
- LICENSE.txt / COPYRIGHT.txt unchanged ✓
- Commits `a542bb0dc9` (Task 1) + `09db8a5b5b` (Task 3) ✓
