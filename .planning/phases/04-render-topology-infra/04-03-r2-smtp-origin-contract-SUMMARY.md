---
phase: 04-render-topology-infra
plan: "03"
subsystem: deployment-infra
tags: [render, r2, smtp, cors, cookies, origins, docs, env-contract]
dependency_graph:
  requires: [render-blueprint-topology, celery-redis-broker, bright-byte-hosting-domain]
  provides: [r2-smtp-origin-contract, render-deployment-runbook]
  affects:
    - docs/render-deployment.md
    - render.yaml
    - apps/*/.env.example
tech_stack:
  added: []
  patterns: [s3-compatible-r2, smtp-tls-exclusive, subdomain-origins, build-time-vite-env]
key_files:
  created: []
  modified:
    - docs/render-deployment.md
    - .env.example
    - apps/api/.env.example
    - apps/web/.env.example
    - apps/admin/.env.example
    - apps/space/.env.example
    - apps/live/.env.example
decisions:
  - "Task 3 checkpoint (final origins) resolved by the user's pmp.bright-byte.co subdomain decision — no separate pause needed"
  - "Runbook rewritten off the stale *.onrender.com placeholders (from the partial prior run) onto the finalized subdomain topology"
  - "render.yaml origin/CORS/cookie contract was already committed in the prior domain-wiring commit (7534c116fd); this plan finalizes the docs + env examples to match"
  - "Local localhost env defaults kept intact; production subdomain values added as guidance comments only"
metrics:
  completed: "2026-06-04"
  tasks_completed: 3
  files_changed: 6
  commits: 1
---

# Phase 04 Plan 03: R2 / SMTP / Origin Contract Summary

**One-liner:** Documented the R2 + SMTP + multi-origin deployment contract against the finalized `pmp.bright-byte.co` subdomain topology, and aligned all env examples so production values are discoverable without breaking local defaults (DEPLOY-03/04/06).

## Context

This plan was **partially executed in a prior run** (commit `3124fad74f` added a runbook) but never completed — no SUMMARY existed and the runbook still used `*.onrender.com` placeholders with `COOKIE_DOMAIN` empty. The hosting-domain decision (`pmp.bright-byte.co`, subdomains) landed afterward and was wired into `render.yaml` (commit `7534c116fd`). This run reconciles the docs/env layer with that decision and closes the plan.

## What Was Done — Commit `5d6e1a5dee`

### Task 1 — Render deployment runbook

Rewrote `docs/render-deployment.md` onto the subdomain topology with operator sections for: origin topology + DNS CNAMEs, Render resources, Cloudflare R2 (env table + CORS JSON policy + presigned PUT/GET verification), SMTP (env table, TLS/SSL exclusivity, `test_email` command, SPF/DKIM caveat), origins/cookies/CORS/OAuth, deploy order, and a verification checklist. Uses exact codebase env names (`AWS_S3_ENDPOINT_URL`, `EMAIL_HOST`, `COOKIE_DOMAIN`, `VITE_*`, etc.).

### Task 2 — Env-example origin contract

Added production-value guidance comments (subdomain origins) while keeping localhost defaults:

- `.env.example` + `apps/api/.env.example` — production `ALLOWED_HOSTS`/`CORS_ALLOWED_ORIGINS`/`COOKIE_DOMAIN`
- `apps/web|admin|space/.env.example` — commented production `VITE_*` origin matrix (identical across all three)
- `apps/live/.env.example` — production `API/WEB/LIVE_BASE_URL` + `CORS_ALLOWED_ORIGINS`

`render.yaml`'s R2/SMTP (`sync:false`), origin, cookie, live-CORS, and `VITE_*` contract was already in place from the domain-wiring commit.

### Task 3 (checkpoint:human-action — final origins) — RESOLVED

The blocking "confirm final deployed origins" gate was answered by the user's `pmp.bright-byte.co` subdomain decision (web=apex subdomain; api/live/admin/spaces subdomains; `COOKIE_DOMAIN=.pmp.bright-byte.co`). No separate pause was needed.

## Phase Gate Results

| Gate | Check                                                                 | Result             |
| ---- | --------------------------------------------------------------------- | ------------------ |
| 1    | Runbook contains R2/SMTP/origin/cookie/verification + exact env names | PASS               |
| 2    | `render.yaml` exposes R2/SMTP/CORS/VITE contract                      | PASS (17 matches)  |
| 3    | web/admin/space examples share the VITE matrix                        | PASS (8 keys each) |
| 4    | root/api examples have R2+SMTP+CORS+cookie; live has CORS             | PASS               |
| —    | localhost defaults still usable                                       | PASS               |

## Deviations from Plan

**Plan said "create" the runbook; it already existed (stale).** Treated as update-in-place: rewrote onto the subdomain topology rather than creating from scratch. Net effect matches the plan's intent.

## Known Stubs / Carried to 04-04

- R2 bucket, API tokens, and CORS policy are **manual** (Cloudflare dashboard) — `AWS_*` stay `sync:false`.
- SMTP host/user/password are **manual** (provider dashboard) — `EMAIL_*` creds stay `sync:false`; SPF/DKIM for `pmp.bright-byte.co` required.
- DNS CNAMEs + Render custom domains + OAuth redirect URIs are **manual**.
- Live-deploy verification (attachment upload, email delivery, onboarding UAT) is plan **04-04** and needs the instance actually up.

## Threat Flags

T-04-07 (R2 CORS/endpoint mismatch), T-04-08 (SMTP misconfig), T-04-09 (origin/cookie/CORS drift) — all documented with exact env contracts + verification steps. No code/secrets added to the repo.

## Self-Check: PASSED

- `docs/render-deployment.md` on subdomain topology, all sections present ✓
- 6 env-example files carry production subdomain guidance, localhost intact ✓
- Task 3 origin checkpoint satisfied ✓
- Commit `5d6e1a5dee` ✓
