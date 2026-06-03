---
phase: 05-security-hardening-agpl-gate
plan: "01"
subsystem: api/settings
tags: [security, django, settings, boot-guard, cors, agpl]
dependency_graph:
  requires: []
  provides:
    - boot-time security guard in common.py
    - ALLOWED_HOSTS env var wired in render.yaml
    - unit tests for all four guard conditions
  affects:
    - apps/api/plane/settings/common.py
    - apps/api/plane/settings/test.py
    - render.yaml
    - apps/api/plane/tests/unit/settings/test_config_guard.py
tech_stack:
  added: []
  patterns:
    - Django ImproperlyConfigured raised at settings-import time
    - Extracted helper function (check_boot_security) for unit-testable guard logic
key_files:
  created:
    - apps/api/plane/tests/unit/settings/test_config_guard.py
  modified:
    - apps/api/plane/settings/common.py
    - apps/api/plane/settings/test.py
    - render.yaml
decisions:
  - Extracted guard logic into check_boot_security() helper so tests can call it directly
    without reloading the Django settings module (avoids import-time side effects)
  - Guard checks DEBUG from the already-computed module-level variable; ALLOWED_HOSTS
    check is gated on `not debug` so wildcard is acceptable in local dev
  - test.py sets os.environ DEBUG=1 and a dummy SECRET_KEY before importing common so
    the guard stays silent during pytest runs — this is the only change to test.py
  - ALLOWED_HOSTS added only to bright-byte-api service in render.yaml; workers and
    migrator omitted because they do not receive HTTP traffic
metrics:
  duration: "~20 minutes"
  completed: "2026-06-03"
  tasks_completed: 2
  files_changed: 4
---

# Phase 05 Plan 01: Django Settings Security Guard Summary

Boot-time ImproperlyConfigured guard covering absent SECRET_KEY, wildcard ALLOWED_HOSTS (non-DEBUG), and CORS allow-all + credentials combination, with full unit test coverage.

## What Was Built

### Task 1: Boot-time guard + render.yaml ALLOWED_HOSTS

Added `check_boot_security()` helper and guard block to the bottom of `apps/api/plane/settings/common.py`. The helper accepts all relevant values as parameters (rather than reading globals directly) so it can be called from unit tests without triggering a full settings reload.

The guard block calls the helper with the module-level values, then raises `ImproperlyConfigured` only when `_boot_errors and not DEBUG`. When `DEBUG=True` (local dev or test), the block is completely silent — no raise, no print, no log.

Three conditions checked:

- **Condition A (SECRET_KEY)**: absent `SECRET_KEY` env var means Django falls back to `get_random_secret_key()`, generating an ephemeral key on every restart that invalidates all sessions and CSRF tokens
- **Condition B (ALLOWED_HOSTS)**: `"*" in ALLOWED_HOSTS` when `not DEBUG` allows host-header injection; wildcard is intentional and permitted in local/test
- **Condition C (CORS)**: `CORS_ALLOW_ALL_ORIGINS=True` combined with `CORS_ALLOW_CREDENTIALS=True` leaks session cookies to any cross-origin request; `globals().get("CORS_ALLOW_ALL_ORIGINS", False)` avoids NameError since the variable only exists in the `else` branch

Added `- key: ALLOWED_HOSTS` with `value: bright-byte-api.onrender.com` to the `bright-byte-api` service env block in `render.yaml`, immediately after the `SECRET_KEY` entry. Workers and beat/migrator services omitted — they do not serve HTTP traffic.

### Task 2: Unit tests for the guard

Created `apps/api/plane/tests/unit/settings/test_config_guard.py` with four `@pytest.mark.unit` tests:

- `test_boot_guard_requires_secret_key` — guard returns error when `SECRET_KEY` is absent from environ dict
- `test_boot_guard_rejects_allow_all_cors` — guard returns error when `cors_allow_all_origins=True` with credentials
- `test_boot_guard_rejects_wildcard_allowed_hosts` — guard returns error when `"*" in allowed_hosts` and `debug=False`
- `test_boot_guard_silent_in_debug` — no ALLOWED_HOSTS error when `debug=True`; fully safe config returns zero errors

Updated `apps/api/plane/settings/test.py` to call `os.environ.setdefault("DEBUG", "1")` and `os.environ.setdefault("SECRET_KEY", "test-only-...")` before `from .common import *`. This ensures the guard is silent during pytest because `DEBUG=1` is in the environment when `common.py` is imported.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical Functionality] Set os.environ before common import in test.py**

- **Found during:** Task 2 execution
- **Issue:** `test.py` does `from .common import *`, which runs the guard at module-import time with `DEBUG=0` (env default). The `DEBUG = True` override in test.py comes after the import, too late to suppress the guard. Tests failed with `ImproperlyConfigured`.
- **Fix:** Added `os.environ.setdefault("DEBUG", "1")` and a dummy `SECRET_KEY` to test.py before the common import. Using `setdefault` means real env vars set by CI or developers always take precedence.
- **Files modified:** `apps/api/plane/settings/test.py`
- **Commit:** 6f986c961f

## Phase Gate Verification

| Gate | Check                                            | Result             |
| ---- | ------------------------------------------------ | ------------------ |
| 1    | `grep -c "ImproperlyConfigured" common.py` ≥ 2   | 4                  |
| 2    | `grep -c "ALLOWED_HOSTS" common.py` ≥ 2          | 6                  |
| 3    | `grep -c "CORS_ALLOW_ALL_ORIGINS" common.py` ≥ 2 | 4                  |
| 4    | `grep -c "ALLOWED_HOSTS" render.yaml` ≥ 1        | 1                  |
| 5    | `git diff --quiet LICENSE.txt COPYRIGHT.txt`     | INTACT             |
| 6    | 4 unit tests pass                                | 4 passed, 0 failed |

## Commits

| Task   | Commit     | Message                                                                    |
| ------ | ---------- | -------------------------------------------------------------------------- |
| Task 1 | 8da5a00d6f | feat(05-01): add boot-time security guard and ALLOWED_HOSTS to render.yaml |
| Task 2 | 6f986c961f | test(05-01): add unit tests for boot-time security guard                   |

## Known Stubs

None — all guard conditions are fully wired and tested.

## Threat Flags

No new threat surface introduced. All changes harden existing surface identified in the threat model:

- T-5-01a mitigated (ALLOWED_HOSTS wildcard → guard + render.yaml value)
- T-5-01b mitigated (ephemeral SECRET_KEY → guard raises when absent)
- T-5-01c mitigated (CORS allow-all + credentials → guard raises)
- T-5-01d mitigated (DEBUG bypass → guard explicitly checks `not DEBUG`)

## Self-Check: PASSED

- `apps/api/plane/settings/common.py` — exists, contains `check_boot_security`, `_boot_errors`, `ImproperlyConfigured`
- `apps/api/plane/settings/test.py` — exists, contains `os.environ.setdefault("DEBUG", "1")`
- `apps/api/plane/tests/unit/settings/test_config_guard.py` — exists, 4 test functions present
- `render.yaml` — contains `key: ALLOWED_HOSTS` at line 43
- Commits 8da5a00d6f and 6f986c961f present in git log
- LICENSE.txt and COPYRIGHT.txt byte-identical (git diff exits 0)
