# Render Deployment Runbook — Bright-Byte PMP

Operator guide for deploying Bright-Byte PMP to Render from `render.yaml`, with the
three external dependencies Render does not provide (object storage, SMTP, DNS/custom
domains). Everything here uses the **exact** environment variable names the codebase
already reads — do not invent new names.

> Scope: Phase 4 (topology + infra). Security hardening (stable `SECRET_KEY`,
> `ALLOWED_HOSTS`/CORS guard, telemetry) is Phase 5 and is noted only where it affects
> whether a deploy boots.

---

## 1. Origin topology

Production runs as **first-class Render service origins on subdomains** of
`pmp.bright-byte.co` — no Caddy/reverse proxy. The hosting domain decision is recorded
in `render.yaml`; this table is the single source of truth for every origin/CORS/cookie
value below.

| Service          | Render service                           | Public origin                       | Base path   |
| ---------------- | ---------------------------------------- | ----------------------------------- | ----------- |
| Web (main SPA)   | `bright-byte-web` (static)               | `https://pmp.bright-byte.co`        | `/`         |
| API (Django)     | `bright-byte-api` (web)                  | `https://api.pmp.bright-byte.co`    | `/api`      |
| Live (WebSocket) | `bright-byte-live` (web)                 | `https://live.pmp.bright-byte.co`   | `/live`     |
| Admin            | `bright-byte-admin` (static)             | `https://admin.pmp.bright-byte.co`  | `/god-mode` |
| Space (SSR)      | `bright-byte-space` (web)                | `https://spaces.pmp.bright-byte.co` | `/spaces`   |
| Worker / Beat    | `bright-byte-worker`, `bright-byte-beat` | — (no public origin)                | —           |

Shared session cookie across subdomains: `COOKIE_DOMAIN=.pmp.bright-byte.co` (leading dot).

### DNS (manual)

Create one CNAME per public service pointing at its Render-assigned `*.onrender.com`
target (shown in the Render dashboard after the blueprint syncs), then add each domain
under **Render service → Settings → Custom Domains** so TLS certs issue:

```
pmp.bright-byte.co         CNAME -> bright-byte-web.onrender.com
api.pmp.bright-byte.co     CNAME -> bright-byte-api.onrender.com
live.pmp.bright-byte.co    CNAME -> bright-byte-live.onrender.com
admin.pmp.bright-byte.co   CNAME -> bright-byte-admin.onrender.com
spaces.pmp.bright-byte.co  CNAME -> bright-byte-space.onrender.com
```

---

## 2. Render resources (provisioned by `render.yaml`)

- **Postgres** — `bright-byte-postgres` (`basic-1gb`). Wired to every service via
  `DATABASE_URL` (`fromDatabase`).
- **Key Value (Redis/Valkey)** — `bright-byte-redis` (`starter`, `maxmemoryPolicy:
noeviction`). Backs both `REDIS_URL` and `CELERY_BROKER_URL`. `noeviction` is required
  so Celery does not lose queued jobs (see plan 04-02 / `.env.example`).
- **Migrations** — run as the API service `preDeployCommand`
  (`./bin/docker-entrypoint-migrator.sh`); applies pending migrations (incl. the
  telemetry-default migration `license/0007`) before each release.
- **Beat** — exactly one `bright-byte-beat` instance (`numInstances: 1`); never scale it.

---

## 3. Object storage — Cloudflare R2 (manual)

Bright-Byte uses an S3-compatible backend (`apps/api/plane/settings/storage.py`,
`S3Storage`). For R2 keep `USE_MINIO=0` and `AWS_REGION=auto`.

Variables (set as **secrets** in the Render dashboard — they are `sync: false` in
`render.yaml` on **both** `bright-byte-api` and `bright-byte-worker`):

| Variable                | Value                                           | Source                              |
| ----------------------- | ----------------------------------------------- | ----------------------------------- |
| `USE_MINIO`             | `0`                                             | already set in `render.yaml`        |
| `AWS_REGION`            | `auto`                                          | already set in `render.yaml`        |
| `AWS_S3_ENDPOINT_URL`   | `https://<account_id>.r2.cloudflarestorage.com` | Cloudflare → R2 → account endpoint  |
| `AWS_S3_BUCKET_NAME`    | bucket name                                     | Cloudflare → R2 → bucket            |
| `AWS_ACCESS_KEY_ID`     | R2 access key id                                | Cloudflare → R2 → Manage API tokens |
| `AWS_SECRET_ACCESS_KEY` | R2 secret access key                            | Cloudflare → R2 → Manage API tokens |
| `SIGNED_URL_EXPIRATION` | `3600`                                          | already set in `render.yaml`        |

### R2 CORS (required for browser presigned PUT/GET)

Set the bucket CORS policy (Cloudflare → R2 → bucket → Settings → CORS) to allow the
three browser origins and the verbs the client uses:

```json
[
  {
    "AllowedOrigins": [
      "https://pmp.bright-byte.co",
      "https://admin.pmp.bright-byte.co",
      "https://spaces.pmp.bright-byte.co"
    ],
    "AllowedMethods": ["PUT", "GET", "HEAD"],
    "AllowedHeaders": ["Content-Type", "Content-Length", "Authorization", "x-amz-*"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3600
  }
]
```

**Verify:** in the app, upload an attachment to a work item, reload, and confirm the
file opens (presigned GET). A CORS/endpoint/bucket mismatch shows as a failed PUT in the
browser network tab (threat T-04-07).

---

## 4. Email — SMTP (manual)

Email config is read by `get_email_configuration()` and consumed by Celery email tasks
and `manage.py test_email`. TLS and SSL are **mutually exclusive** — set exactly one.

| Variable              | Notes                                   | `render.yaml`                   |
| --------------------- | --------------------------------------- | ------------------------------- |
| `EMAIL_HOST`          | SMTP host                               | `sync: false` (api/worker/beat) |
| `EMAIL_HOST_USER`     | SMTP username                           | `sync: false`                   |
| `EMAIL_HOST_PASSWORD` | SMTP password                           | `sync: false`                   |
| `EMAIL_PORT`          | `587` (STARTTLS) or `465` (SSL)         | `value: "587"`                  |
| `EMAIL_USE_TLS`       | `1` for port 587, else `0`              | `value: "1"`                    |
| `EMAIL_USE_SSL`       | `1` for port 465, else `0`              | `value: "0"`                    |
| `EMAIL_FROM`          | `Bright-Byte PMP <info@bright-byte.co>` | already set                     |

If the provider requires implicit TLS on port 465, use `EMAIL_PORT=465`,
`EMAIL_USE_TLS=0`, `EMAIL_USE_SSL=1`.

**Sender domain:** `EMAIL_FROM` uses `bright-byte.co` (root domain). Configure SPF + DKIM (and
DMARC) for that domain at your DNS/SMTP provider or invites and magic links will land in
spam or bounce (threat T-04-08).

**Verify:** from the API service shell on Render:

```bash
python manage.py test_email you@example.com
```

It prints `Email successfully sent` on success, or `Error: Email could not be delivered
due to ...` with the SMTP failure reason. Then confirm a real invite/magic-link email
lands in an inbox.

---

## 5. Origins, cookies, CORS, OAuth

These must all describe the **same** HTTPS topology as section 1, or you get login loops,
blocked XHR, or broken live collaboration (threat T-04-09).

### Backend (`bright-byte-api`) — already in `render.yaml`

| Variable               | Value                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| `ALLOWED_HOSTS`        | `api.pmp.bright-byte.co,bright-byte-api.onrender.com`                                           |
| `CORS_ALLOWED_ORIGINS` | `https://pmp.bright-byte.co,https://admin.pmp.bright-byte.co,https://spaces.pmp.bright-byte.co` |
| `COOKIE_DOMAIN`        | `.pmp.bright-byte.co`                                                                           |
| `WEB_URL`              | `https://api.pmp.bright-byte.co`                                                                |
| `APP_BASE_URL`         | `https://pmp.bright-byte.co` (`APP_BASE_PATH=/`)                                                |
| `ADMIN_BASE_URL`       | `https://admin.pmp.bright-byte.co` (`ADMIN_BASE_PATH=/god-mode`)                                |
| `SPACE_BASE_URL`       | `https://spaces.pmp.bright-byte.co` (`SPACE_BASE_PATH=/spaces`)                                 |
| `LIVE_BASE_URL`        | `https://live.pmp.bright-byte.co` (`LIVE_BASE_PATH=/live`)                                      |

Notes:

- `ALLOWED_HOSTS` keeps the `bright-byte-api.onrender.com` host so Render's internal
  health check (which uses the `.onrender.com` hostname) still passes Django's host check.
  The Phase 5 boot guard rejects `ALLOWED_HOSTS='*'`, so the explicit list is required.
- `CORS_ALLOWED_ORIGINS` also seeds `CSRF_TRUSTED_ORIGINS` (`common.py`) — list only the
  **browser** origins (web, admin, space), not the API or live host.
- `COOKIE_DOMAIN` drives both `SESSION_COOKIE_DOMAIN` and `CSRF_COOKIE_DOMAIN`; the
  leading dot is what lets the session cookie work across all subdomains.

### Live (`bright-byte-live`) — already in `render.yaml`

`CORS_ALLOWED_ORIGINS` lists the same three browser origins; `API_BASE_URL`,
`WEB_BASE_URL`, and `LIVE_BASE_URL` point at the section-1 origins. After deploy, check
`https://live.pmp.bright-byte.co/live/health` and a browser collaboration session.

### Frontend static builds (`VITE_*`) — baked at build time

`bright-byte-web`, `bright-byte-admin`, and `bright-byte-space` bake the full origin
matrix into the bundle at build time, so a topology change requires a **rebuild**, not
just an env edit. All three carry the identical matrix:

| Variable              | Value                                                                 |
| --------------------- | --------------------------------------------------------------------- |
| `VITE_API_BASE_URL`   | `https://api.pmp.bright-byte.co` (`VITE_API_BASE_PATH=/api`)          |
| `VITE_WEB_BASE_URL`   | `https://pmp.bright-byte.co` (`VITE_WEB_BASE_PATH=/`)                 |
| `VITE_ADMIN_BASE_URL` | `https://admin.pmp.bright-byte.co` (`VITE_ADMIN_BASE_PATH=/god-mode`) |
| `VITE_SPACE_BASE_URL` | `https://spaces.pmp.bright-byte.co` (`VITE_SPACE_BASE_PATH=/spaces`)  |
| `VITE_LIVE_BASE_URL`  | `https://live.pmp.bright-byte.co` (`VITE_LIVE_BASE_PATH=/live`)       |

### OAuth redirect URIs (manual, only if a provider is enabled)

For each enabled provider (Google, GitHub, GitLab, Gitea), register the redirect URI
against the **API** origin in the provider dashboard, e.g.
`https://api.pmp.bright-byte.co/auth/<provider>/callback/`. Mismatched redirect URIs fail
the OAuth handshake.

---

## 6. Deploy order

1. Push `render.yaml`; create the Blueprint in Render (provisions Postgres, Key Value,
   and all services).
2. Set the dashboard secrets: R2 (`AWS_*`), SMTP (`EMAIL_*`), and any OAuth client
   secrets, on **both** `bright-byte-api` and `bright-byte-worker` where applicable.
3. First deploy runs the migrator `preDeployCommand` automatically (API service deploys
   before workers).
4. Add the five custom domains and create the matching DNS CNAMEs (section 1).
5. Set R2 bucket CORS (section 3) and SMTP SPF/DKIM (section 4).
6. Rebuild the static sites after any `VITE_*` origin change.
7. Run verification (section 7).

---

## 7. Verification checklist

- [ ] All Render services are healthy; exactly one `bright-byte-beat` instance is running.
- [ ] API migrations completed before serving traffic.
- [ ] `https://pmp.bright-byte.co` loads the web app over TLS; `https://api.pmp.bright-byte.co/`
      returns the API health response; admin loads under `/god-mode`, Space under `/spaces`.
- [ ] Sign in works and the session persists across `pmp` and `admin`/`spaces` subdomains
      (confirms `COOKIE_DOMAIN`); API calls are not blocked by CORS or CSRF.
- [ ] Create a project and a work item (confirms DB + API); a worker processes a queued job.
- [ ] Upload and re-open an attachment (confirms R2 presigned PUT/GET + CORS).
- [ ] `python manage.py test_email <you>` reports success, and an invite/magic-link email
      arrives (confirms SMTP + sender domain auth).
- [ ] Live health (`/live/health`) and a WebSocket collaboration session work.
- [ ] If OAuth is enabled, complete one provider login round-trip.
