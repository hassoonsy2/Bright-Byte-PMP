---
phase: 04
slug: render-topology-infra
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-02
---

# Phase 04 - Validation Strategy

> Per-phase validation contract for Render topology, external infrastructure, and live onboarding verification.

---

## Test Infrastructure

| Property               | Value                                                                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Framework**          | Source assertions, YAML validation, TypeScript checks, Django checks, manual/live smoke tests                                     |
| **Config file**        | `render.yaml`, `.env.example`, `apps/api/.env.example`, app Dockerfiles                                                           |
| **Quick run command**  | `pnpm check:types` if code changes are made; otherwise `node -e "require('fs').accessSync('render.yaml')"` plus source assertions |
| **Full suite command** | `pnpm check && docker compose -f docker-compose-test.yml run --rm api-tests pytest -m unit` when code changes touch app behavior  |
| **Estimated runtime**  | ~60 seconds for source assertions; 5-20 minutes for full checks depending on Docker cache                                         |

---

## Sampling Rate

- **After every task commit:** Run the task's source assertions and any targeted unit/type checks.
- **After every plan wave:** Run `pnpm check:types` and `pnpm check:lint` if app or config TypeScript changed; run YAML/source assertions for `render.yaml` after every blueprint edit.
- **Before `$gsd-verify-work`:** Full phase verification must include live Render, R2, SMTP, worker/beat, WebSocket, auth cookie, and onboarding checks.
- **Max feedback latency:** 20 minutes for automated gates; live checks are manual and must be recorded with URLs/timestamps.

---

## Per-Task Verification Map

| Task ID  | Plan | Wave | Requirement | Threat Ref | Secure Behavior                                                       | Test Type     | Automated Command                                                                                     | File Exists              | Status  |
| -------- | ---- | ---- | ----------- | ---------- | --------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------- | ------------------------ | ------- | ------- |
| 04-01-01 | TBD  | 1    | DEPLOY-01   | T-04-01    | No hardcoded secrets in blueprint                                     | source        | `test -f render.yaml` and YAML/service-name assertions                                                | No                       | pending |
| 04-01-02 | TBD  | 1    | DEPLOY-02   | T-04-02    | Paid datastores; internal URLs preferred                              | source/manual | `grep -n "type: keyvalue\\                                                                            | databases:" render.yaml` | No      | pending |
| 04-02-01 | TBD  | 1    | DEPLOY-05   | T-04-03    | Broker does not drop queued jobs silently                             | source/unit   | Source assertion for `CELERY_BROKER_URL` or `AMQP_URL`; targeted Django settings test if code changes | No                       | pending |
| 04-02-02 | TBD  | 1    | DEPLOY-03   | T-04-04    | R2 credentials are secret; browser CORS restricted to deployed origin | source/manual | Source assertions for R2 env keys in docs/examples                                                    | No                       | pending |
| 04-02-03 | TBD  | 1    | DEPLOY-04   | T-04-05    | SMTP credentials are secret; TLS/SSL mode explicit                    | source/manual | Source assertions for SMTP env keys and `test_email` instructions                                     | No                       | pending |
| 04-03-01 | TBD  | 2    | DEPLOY-06   | T-04-06    | HTTPS-only browser origins; cookies scoped intentionally              | source/manual | Source assertions for `VITE_*`, `CORS_ALLOWED_ORIGINS`, `COOKIE_DOMAIN` guidance                      | No                       | pending |
| 04-04-01 | TBD  | 2    | DEPLOY-07   | T-04-07    | Live shared instance supports only intended tenant/workspace access   | manual        | Live onboarding checklist recorded in phase summary                                                   | No                       | pending |

_Status values: pending, green, red, flaky._

---

## Wave 0 Requirements

- [ ] `render.yaml` exists at repo root before blueprint source assertions run.
- [ ] `scripts/` or inline `node -e` assertions can parse `render.yaml` without network access.
- [ ] If Redis is chosen as Celery broker, add a focused settings test or source assertion proving `CELERY_BROKER_URL` overrides RabbitMQ fallback.
- [ ] If static-site build output is uncertain, verify local build output paths for `web` and `admin` before finalizing `staticPublishPath`.

---

## Manual-Only Verifications

| Behavior                             | Requirement          | Why Manual                                                                            | Test Instructions                                                                                                                     |
| ------------------------------------ | -------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Render blueprint sync/deploy         | DEPLOY-01, DEPLOY-02 | Requires Render workspace and paid resources                                          | Validate/sync `render.yaml`; record service/resource names, plans, region, and deploy status                                          |
| R2 presigned browser upload/download | DEPLOY-03            | Requires Cloudflare R2 bucket, credentials, and deployed browser origin               | Upload an attachment from deployed web app; confirm PUT succeeds, GET/download succeeds, and object exists in R2                      |
| SMTP delivery                        | DEPLOY-04            | Requires real SMTP provider and recipient inbox                                       | Run `python manage.py test_email <recipient>` or admin email test, then verify invite/magic-link reaches inbox                        |
| Celery worker/beat                   | DEPLOY-05            | Requires live broker and worker processes                                             | Confirm worker receives jobs; confirm exactly one beat process exists; trigger one email/cleanup-style job                            |
| Origin/cookie topology               | DEPLOY-06            | Browser cookie, CORS, CSRF, OAuth, and custom domain behavior are deployment-specific | Sign in through deployed web app; verify API calls, admin route, space route, live route, cookies, and OAuth redirect URIs if enabled |
| Client onboarding                    | DEPLOY-07            | End-to-end user workflow spans all services                                           | Create workspace/client, create project, upload attachment, invite user or request magic link, and record evidence                    |

---

## Validation Sign-Off

- [ ] All tasks have automated source assertions or explicit manual verification.
- [ ] Sampling continuity: no three consecutive implementation tasks without an automated source/type/lint check.
- [ ] Wave 0 covers missing local validation helpers before deploy work begins.
- [ ] No watch-mode commands in verification.
- [ ] Feedback latency under 20 minutes for automated checks.
- [ ] `nyquist_compliant: true` is set in frontmatter.

**Approval:** pending
