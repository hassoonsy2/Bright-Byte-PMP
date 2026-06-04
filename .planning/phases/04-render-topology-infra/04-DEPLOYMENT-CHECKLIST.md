# Phase 04 — Render Deployment & Onboarding UAT Checklist

Live evidence record for DEPLOY-01 … DEPLOY-07. Phase 4 is **not** complete until the
live sections below are filled with real (non-secret) evidence.

> ⚠️ **Never paste real secrets here.** Record service names, URLs, timestamps, masked
> identifiers (e.g. `AKIA…3F2`), log-excerpt summaries, and pass/fail only. No bearer
> tokens, passwords, cookie values, or private inbox contents.

Runbook: `docs/render-deployment.md` · Blueprint: `render.yaml` · Domain:
`pmp.bright-byte.co` (subdomains).

---

## A. Local pre-deploy gates (Task 2 — automated, done)

| Gate                        | Command                                                          | Outcome                                                | Date       |
| --------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------ | ---------- |
| Blueprint topology verifier | `node scripts/verify-render-blueprint.mjs`                       | ✅ `render.yaml topology verification passed` (exit 0) | 2026-06-04 |
| Celery broker settings test | `pytest plane/tests/unit/settings/test_celery_broker.py -m unit` | ✅ 4 passed                                            | 2026-06-04 |

Both local source gates are green; safe to proceed to dashboard deploy.

---

## B. Blueprint sync & services (DEPLOY-01)

Operator fills status/URL after Render Blueprint sync.

| Service              | Type         | Expected                      | Deploy status | Service URL     | Operator |
| -------------------- | ------------ | ----------------------------- | ------------- | --------------- | -------- |
| `bright-byte-api`    | web (docker) | green, migrator preDeploy ran |               |                 |          |
| `bright-byte-worker` | worker       | green                         |               | (no public URL) |          |
| `bright-byte-beat`   | worker       | green, **exactly 1 instance** |               | (no public URL) |          |
| `bright-byte-live`   | web (docker) | green, `/live/health` 200     |               |                 |          |
| `bright-byte-space`  | web (docker) | green, `/spaces/` 200         |               |                 |          |
| `bright-byte-web`    | static       | published                     |               |                 |          |
| `bright-byte-admin`  | static       | published, `/god-mode`        |               |                 |          |

- [ ] **DEPLOY-01** — all services deploy from the blueprint; exactly one beat. Beat instance count confirmed: **\_\_**

## C. Managed resources (DEPLOY-02)

| Resource                        | Plan (paid)           | Region | Wired via                         | Status | Operator |
| ------------------------------- | --------------------- | ------ | --------------------------------- | ------ | -------- |
| `bright-byte-postgres`          | basic-1gb             | oregon | `DATABASE_URL` (fromDatabase)     |        |          |
| `bright-byte-redis` (Key Value) | starter, `noeviction` | oregon | `REDIS_URL` + `CELERY_BROKER_URL` |        |          |

- [ ] **DEPLOY-02** — paid Postgres + paid Key Value provisioned and wired; Key Value eviction policy = `noeviction` confirmed in dashboard.

## D. Object storage — Cloudflare R2 (DEPLOY-03)

| Item                                                             | Evidence   | Operator |
| ---------------------------------------------------------------- | ---------- | -------- |
| Bucket created (name, masked)                                    |            |          |
| `AWS_S3_ENDPOINT_URL` set (account, masked)                      |            |          |
| Bucket CORS allows web/admin/spaces origins                      |            |          |
| Browser attachment **upload** (presigned PUT) succeeds           | timestamp: |          |
| Browser attachment **download/preview** (presigned GET) succeeds | timestamp: |          |

- [ ] **DEPLOY-03** — R2 provisioned; presigned PUT **and** GET verified from the browser (not just backend shell).

## E. Email — SMTP (DEPLOY-04)

| Item                                               | Evidence                           | Operator |
| -------------------------------------------------- | ---------------------------------- | -------- |
| `python manage.py test_email <you>` result         | `Email successfully sent` / error: |          |
| SPF/DKIM configured for `pmp.bright-byte.co`       |                                    |          |
| Real invite or magic-link email reached test inbox | timestamp + masked recipient:      |          |

- [ ] **DEPLOY-04** — transactional email delivers to a real inbox.

## F. Celery worker / beat (DEPLOY-05)

| Item                                               | Evidence | Operator |
| -------------------------------------------------- | -------- | -------- |
| Worker processed ≥1 real job (log excerpt summary) |          |          |
| Exactly one beat scheduler running                 |          |          |

- [ ] **DEPLOY-05** — worker processes jobs over the Redis broker; single beat.

## G. Origins / cookies / CORS / OAuth (DEPLOY-06)

| Item                                                              | Evidence  | Operator |
| ----------------------------------------------------------------- | --------- | -------- |
| 5 DNS CNAMEs created + custom domains attached (TLS issued)       |           |          |
| Sign-in works; session persists across `pmp` / `admin` / `spaces` |           |          |
| API calls from web/admin/space not blocked by CORS/CSRF           |           |          |
| Admin loads under `/god-mode`; Space under `/spaces`              |           |          |
| OAuth redirect round-trip (if any provider enabled)               | provider: |          |

- [ ] **DEPLOY-06** — multi-origin auth/cookies/CORS/OAuth all work across the deployed topology.

## H. Client onboarding UAT (DEPLOY-07)

End-to-end on a **test** client/workspace (no real client data until Phase 5 gate closes).

| Step                                                       | Evidence (timestamp) | Operator |
| ---------------------------------------------------------- | -------------------- | -------- |
| Sign in to `https://pmp.bright-byte.co`                    |                      |          |
| Create a test workspace / client                           |                      |          |
| Create a project                                           |                      |          |
| Upload + download an attachment (R2)                       |                      |          |
| Receive an email (invite / magic-link)                     |                      |          |
| Open a page/editor → live collaboration connects (`/live`) |                      |          |

- [ ] **DEPLOY-07** — a client can be onboarded end-to-end on the live shared instance.

---

## Sign-off

| Field                          | Value                                             |
| ------------------------------ | ------------------------------------------------- |
| Overall result                 | ☐ approved ☐ blocked                              |
| Deployed origins               | pmp / api / live / admin / spaces .bright-byte.co |
| Date                           |                                                   |
| Blockers (owner + next action) |                                                   |

> When all DEPLOY-01…07 boxes are checked with evidence, record the outcome and create
> `04-04-render-deploy-onboarding-uat-SUMMARY.md` (Task 5).
