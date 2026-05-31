# Stack Research

**Domain:** Deploying the Plane (Bright-Byte PMP) multi-service monorepo on Render.com as a single shared instance
**Researched:** 2026-06-01
**Confidence:** HIGH (Render specifics verified against official docs; one decisive code fact verified in-repo: Celery broker is AMQP-only)

> Scope note: This is a BROWNFIELD deployment-dimension research file. It does NOT re-document Plane's internal stack (see `.planning/codebase/STACK.md`). It answers only: *how does this exact stack map onto Render.com in 2026, and what new infra must we provision?*

---

## TL;DR (read this first)

1. **One `render.yaml` Blueprint** defines everything: 1 Django web service, 1 Celery worker, 1 Celery beat worker, 1 pre-deploy migrator, 1 Node/Hocuspocus `live` web service, 3 frontend services (`web` + `admin` as static sites, `space` as a Node web service), 1 managed Postgres, 1 managed Key Value (Redis/Valkey). All built from the **existing Dockerfiles** — no rewrite.
2. **Render has NO managed object storage** → provision **Cloudflare R2** (recommended) for attachments. HIGH-impact gap.
3. **Render has NO managed RabbitMQ**, and **Plane's Celery broker is hard-coded to AMQP** (`apps/api/plane/settings/common.py:309-312`) — there is no Redis-broker code path. This is the single biggest gotcha. → Use **CloudAMQP** (managed RabbitMQ add-on) OR run RabbitMQ as a Render private service. A 3-line code change to allow a Redis broker is the cleaner long-term fix (see Pitfalls).
4. **Render has NO managed SMTP** → provision **Resend** (recommended) or Brevo for invites/notifications.
5. **The frontends bake `VITE_*` URLs at BUILD time** (Docker build args), not runtime. Render env vars set on a static site are NOT injected into an already-built bundle. You must pass the public URLs as Docker `buildArgs` / `envVars` consumed during `turbo run build`. HIGH-impact gotcha.
6. **Caddy (`apps/proxy`) is replaced by Render's router + a single custom domain.** Render gives each service its own `*.onrender.com` URL and does path-based routing per static-site `routes`. You do NOT deploy the Caddy proxy on Render.
7. **Do NOT use any Render Free tier for production**: free Postgres expires after 30 days with no backups; free web services cold-start (~1 min) after 15 min idle, which breaks the live WebSocket server and Celery responsiveness.

---

## Recommended Stack

### Core Technologies (Render resources)

| Technology | Version / Plan | Purpose | Why Recommended |
|------------|----------------|---------|-----------------|
| **Render Blueprint (`render.yaml`)** | Blueprint spec (2026) | Single IaC file defining all services + datastores | One-file, version-controlled, reproducible deploy of the whole multi-service stack; native to Render. (HIGH) |
| **Render Web Service (Docker)** — API | `runtime: docker`, `dockerfilePath: ./apps/api/Dockerfile.api`, plan `standard`+ | Django ASGI app (gunicorn + uvicorn workers) | Reuses existing `Dockerfile.api` verbatim; web service gets a public URL, health checks, zero-downtime deploys. (HIGH) |
| **Render Background Worker (Docker)** — Celery worker | `type: worker`, same Dockerfile, `dockerCommand: ./bin/docker-entrypoint-worker.sh` | Async tasks (email, webhooks, exports, activity) | Render `worker` type = no public port, exactly what Celery needs. Same image as API. (HIGH) |
| **Render Background Worker (Docker)** — Celery beat | `type: worker`, `dockerCommand: ./bin/docker-entrypoint-beat.sh` | Cron-scheduled tasks (5-min email digest, daily cleanups, metrics push) | Beat must be a **single** long-running process (`numInstances: 1`) — never scale it. (HIGH) |
| **Render Web Service (Docker)** — live | `runtime: docker`, `dockerfilePath: ./apps/live/Dockerfile.live`, plan `starter`+ | Hocuspocus real-time collab (WebSocket) | Render web services support inbound WebSockets natively, no config. Reuses `Dockerfile.live`. (HIGH) |
| **Render Static Site** — web | `runtime: static`, publish `apps/web/build/client` | Main SPA (client-only, `ssr:false`) | `apps/web` builds to a static client bundle; Render static sites are free-CDN, fast, with SPA rewrite to `/index.html`. (HIGH) |
| **Render Static Site** — admin | `runtime: static`, publish `apps/admin/build/client` | Instance-admin SPA (client-only) | Same rationale as `web`. Served under `/god-mode`. (HIGH) |
| **Render Web Service (Docker)** — space | `runtime: docker`, `dockerfilePath: ./apps/space/Dockerfile.space` | Public board view — **SSR**, runs `react-router-serve` | `apps/space` is the one frontend with `ssr: true`; it is a real Node server, so it must be a web service, NOT a static site. (HIGH) |
| **Render Postgres** | Postgres **17** (13–18 available), plan `pro-4gb`+ | Primary relational DB | Managed, automated backups (paid tiers), internal connection string injected via `fromDatabase`. (HIGH) |
| **Render Key Value** | **Valkey 8** (Redis-compatible), paid plan (disk persistence) | Cache, session store, Celery result backend, Hocuspocus Redis sync | Drop-in Redis replacement; new instances run Valkey 8. Paid tier persists to disk. `type: keyvalue`. (HIGH) |

### Supporting / External Services (the gaps Render does NOT provide)

| Service | Recommendation | Purpose | When / Why |
|---------|----------------|---------|------------|
| **Object storage (S3-compatible)** | **Cloudflare R2** | Attachments, uploads, exports (Plane uses `boto3` + `django-storages` S3 backend) | Render has no managed object store. R2 = zero egress fees, full S3 API incl. presigned PUT/GET (which Plane requires), simple flat pricing. (HIGH) |
| **Celery broker** | **CloudAMQP** (managed RabbitMQ) — or self-run RabbitMQ private service | Celery message broker | Plane's broker is **AMQP-only in code**; Render has no managed RabbitMQ. CloudAMQP "Little Lemur" (free/shared) for dev, a paid dedicated plan for prod. (HIGH) |
| **SMTP** | **Resend** (or Brevo) | Invites, magic-link OTP, notifications, password reset | Plane uses Django's plain SMTP backend; any SMTP host works. Resend has a clean API, 3,000 emails/mo free, modern DX. Brevo = 300/day forever free. (MEDIUM) |

---

## Concrete `render.yaml` Skeleton

This is the prescriptive blueprint structure. Field names verified against the [Render Blueprint YAML reference](https://render.com/docs/blueprint-spec). `rootDir` is **not** used because every Dockerfile expects the **repo root** as the Docker build context (see the `COPY . .` + `turbo prune` pattern in each Dockerfile) — so `dockerContext: .` and a repo-root-relative `dockerfilePath`.

```yaml
# render.yaml  (repo root)

databases:
  - name: brightbyte-pg
    plan: pro-4gb            # NEVER free for prod (free expires in 30 days, no backups)
    region: oregon           # keep ALL resources in one region for free internal networking
    postgresMajorVersion: "17"
    databaseName: plane
    user: plane
    # ipAllowList omitted => internal-only access (recommended)

services:
  # ---------- Redis / Valkey ----------
  - type: keyvalue
    name: brightbyte-kv
    plan: standard           # paid => disk persistence; free does NOT persist
    region: oregon
    maxmemoryPolicy: noeviction   # safe default for a session/result store
    ipAllowList: []          # internal-only

  # ---------- Django API (web) ----------
  - type: web
    name: brightbyte-api
    runtime: docker
    region: oregon
    plan: standard
    dockerfilePath: ./apps/api/Dockerfile.api
    dockerContext: ./apps/api          # NOTE: api Dockerfile context is ./apps/api (see compose)
    dockerCommand: ./bin/docker-entrypoint-api.sh
    healthCheckPath: /api/instances/   # public, unauthenticated instance endpoint
    # Run DB migrations once per deploy, before traffic shifts:
    preDeployCommand: ./bin/docker-entrypoint-migrator.sh
    autoDeploy: true
    envVars:
      - fromGroup: brightbyte-shared
      - key: PORT
        value: "8000"
      - key: GUNICORN_WORKERS
        value: "2"
      - key: DATABASE_URL
        fromDatabase: { name: brightbyte-pg, property: connectionString }
      - key: REDIS_URL
        fromService: { type: keyvalue, name: brightbyte-kv, property: connectionString }
      - key: SECRET_KEY
        generateValue: true            # Django SECRET_KEY (was ephemeral — MUST be stable)
      - key: LIVE_SERVER_SECRET_KEY
        generateValue: true
      # --- Broker (NO managed RabbitMQ on Render) ---
      - key: AMQP_URL
        sync: false                    # paste CloudAMQP URL at create time
      # --- Object storage (R2) ---
      - key: AWS_ACCESS_KEY_ID
        sync: false
      - key: AWS_SECRET_ACCESS_KEY
        sync: false
      - key: AWS_S3_BUCKET_NAME
        value: brightbyte-uploads
      - key: AWS_S3_ENDPOINT_URL
        sync: false                    # https://<accountid>.r2.cloudflarestorage.com
      - key: AWS_REGION
        value: auto                    # R2 uses "auto"
      - key: USE_MINIO
        value: "0"
      # --- SMTP ---
      - key: EMAIL_HOST
        value: smtp.resend.com
      - key: EMAIL_HOST_USER
        value: resend
      - key: EMAIL_HOST_PASSWORD
        sync: false
      - key: EMAIL_PORT
        value: "587"
      - key: EMAIL_USE_TLS
        value: "1"
      - key: EMAIL_FROM
        value: "Bright-Byte PMP <no-reply@yourdomain.com>"

  # ---------- Celery worker ----------
  - type: worker
    name: brightbyte-worker
    runtime: docker
    region: oregon
    plan: standard
    dockerfilePath: ./apps/api/Dockerfile.api
    dockerContext: ./apps/api
    dockerCommand: ./bin/docker-entrypoint-worker.sh
    envVars:
      - fromGroup: brightbyte-shared
      - key: DATABASE_URL
        fromDatabase: { name: brightbyte-pg, property: connectionString }
      - key: REDIS_URL
        fromService: { type: keyvalue, name: brightbyte-kv, property: connectionString }
      - key: AMQP_URL
        sync: false
      # (repeat AWS_* / EMAIL_* / SECRET_KEY as needed — workers send email + touch S3)

  # ---------- Celery beat (scheduler) ----------
  - type: worker
    name: brightbyte-beat
    runtime: docker
    region: oregon
    plan: starter
    numInstances: 1                    # CRITICAL: exactly one beat process, never scale
    dockerfilePath: ./apps/api/Dockerfile.api
    dockerContext: ./apps/api
    dockerCommand: ./bin/docker-entrypoint-beat.sh
    envVars:
      - fromGroup: brightbyte-shared
      - key: DATABASE_URL
        fromDatabase: { name: brightbyte-pg, property: connectionString }
      - key: REDIS_URL
        fromService: { type: keyvalue, name: brightbyte-kv, property: connectionString }
      - key: AMQP_URL
        sync: false

  # ---------- Live (Hocuspocus WebSocket) ----------
  - type: web
    name: brightbyte-live
    runtime: docker
    region: oregon
    plan: starter
    dockerfilePath: ./apps/live/Dockerfile.live
    dockerContext: .                   # live Dockerfile context is repo root (turbo prune)
    envVars:
      - key: PORT
        value: "3000"
      - key: API_BASE_URL
        fromService: { type: web, name: brightbyte-api, property: hostport }
      - key: LIVE_SERVER_SECRET_KEY
        fromService: { type: web, name: brightbyte-api, property: ... } # see note below
      - key: REDIS_URL
        fromService: { type: keyvalue, name: brightbyte-kv, property: connectionString }

  # ---------- Space (SSR Node server) ----------
  - type: web
    name: brightbyte-space
    runtime: docker
    region: oregon
    plan: starter
    dockerfilePath: ./apps/space/Dockerfile.space
    dockerContext: .
    # build-time public URLs baked into the SSR bundle:
    # (Docker build args — see "build-time env" gotcha)

  # ---------- Web (static SPA) ----------
  - type: web
    runtime: static
    name: brightbyte-web
    # built via Docker OR via build command; if static-built, publish:
    staticPublishPath: apps/web/build/client
    buildCommand: pnpm install --frozen-lockfile && pnpm turbo run build --filter=web
    routes:
      - type: rewrite
        source: /*
        destination: /index.html       # SPA fallback
    envVars:
      - key: VITE_API_BASE_URL
        value: https://pmp.yourdomain.com      # baked at BUILD time
      - key: VITE_LIVE_BASE_URL
        value: https://pmp.yourdomain.com
      # ...all other VITE_* base URLs

  # ---------- Admin (static SPA) ----------
  - type: web
    runtime: static
    name: brightbyte-admin
    staticPublishPath: apps/admin/build/client
    buildCommand: pnpm install --frozen-lockfile && pnpm turbo run build --filter=admin
    routes:
      - type: rewrite
        source: /*
        destination: /index.html

envVarGroups:
  - name: brightbyte-shared
    envVars:
      - key: DEBUG
        value: "0"
      - key: DJANGO_SETTINGS_MODULE
        value: plane.settings.production
      - key: ALLOWED_HOSTS               # HARDEN: was "*" — set real hosts
        value: pmp.yourdomain.com
      - key: WEB_URL
        value: https://pmp.yourdomain.com
      - key: APP_BASE_URL
        value: https://pmp.yourdomain.com
      - key: CORS_ALLOWED_ORIGINS
        value: https://pmp.yourdomain.com
```

> **Two decisions baked into the skeleton:**
> - **Domain strategy:** Either give each service its own subdomain (`api.`, `live.`, `app.`) and set the `VITE_*` URLs accordingly, OR put everything behind one custom domain using a thin routing layer. Render static sites can `rewrite`/`proxy` via `routes`, but Render does NOT replicate Caddy's full single-host path multiplexing across heterogeneous services. The simplest correct model on Render is **subdomain-per-service** (api/live/space each get their own host; web is the apex). Confirm exact routing in the deploy phase.
> - **`build vs Docker` for static frontends:** You can either keep the existing nginx-based `Dockerfile.web`/`Dockerfile.admin` (deploy as `runtime: docker` web services) or use Render's native `runtime: static` with a `buildCommand`. Static sites are cheaper (free CDN) and simpler, but the build must run from repo root with pnpm/Turbo. **Recommend `runtime: static`** for web/admin to get free global CDN; keep Docker only if the nginx config carries headers you need.

---

## How Plane's Docker / compose assets map onto Render

| docker-compose service | Render mapping | Build asset reused | Notes |
|------------------------|----------------|--------------------|-------|
| `api` | `type: web` (docker) | `apps/api/Dockerfile.api` + `docker-entrypoint-api.sh` | gunicorn+uvicorn on `$PORT`; `collectstatic` runs in entrypoint. |
| `worker` | `type: worker` (docker) | same image, `docker-entrypoint-worker.sh` | No public port. |
| `beat-worker` | `type: worker` (docker), `numInstances: 1` | same image, `docker-entrypoint-beat.sh` | Single instance only. |
| `migrator` | **`preDeployCommand`** on the API service | `docker-entrypoint-migrator.sh` | Render's pre-deploy hook replaces the one-shot migrator container. Runs once per deploy before cutover. |
| `live` | `type: web` (docker) | `apps/live/Dockerfile.live` | WebSocket; context = repo root. |
| `web` | `type: web` `runtime: static` (or docker) | `apps/web/Dockerfile.web` (nginx) | Static client bundle → Render CDN. |
| `admin` | `type: web` `runtime: static` (or docker) | `apps/admin/Dockerfile.admin` | Same. |
| `space` | `type: web` (docker) | `apps/space/Dockerfile.space` | **SSR** — must be a Node server, not static. |
| `proxy` (Caddy) | **DROPPED** | — | Replaced by Render's router + custom domain + static-site `routes`. Do NOT deploy Caddy. |
| `plane-db` (Postgres 15.7) | **Render Postgres** (managed, v17) | — | `DATABASE_URL` via `fromDatabase`. |
| `plane-redis` (Valkey 7.2) | **Render Key Value** (Valkey 8) | — | `REDIS_URL` via `fromService` connectionString. |
| `plane-mq` (RabbitMQ) | **CloudAMQP** (external) or private service | — | Render has NO managed RabbitMQ. `AMQP_URL`. |
| `plane-minio` (MinIO/S3) | **Cloudflare R2** (external) | — | Render has NO managed object store. `AWS_*` + `AWS_S3_ENDPOINT_URL`. |

**Build-context subtlety (verified in repo):** the `api` Dockerfile's compose context is `./apps/api` (`COPY plane plane/` etc. — repo-root not needed), whereas `live`, `web`, `space`, `admin` Dockerfiles use **repo root** context with `turbo prune --scope=<app>`. On Render set `dockerContext` accordingly: `./apps/api` for the API image, `.` (repo root) for the JS apps.

---

## Required Environment Variables (production Render deploy)

### API + workers (Django) — required

| Var | Source on Render | Notes |
|-----|------------------|-------|
| `SECRET_KEY` | `generateValue: true` | **Must be stable** — was ephemeral by default (security debt in CONCERNS). Set once, reuse across api/worker/beat. |
| `DATABASE_URL` | `fromDatabase` connectionString | Internal URL; Plane uses `dj-database-url`. |
| `REDIS_URL` | `fromService` keyvalue connectionString | Cache, sessions, Celery result backend, live sync. Internal `redis://`. |
| `AMQP_URL` | `sync: false` (CloudAMQP) | **Required** — broker is AMQP-only in code. Without it Celery tries `amqp://...@localhost` and silently fails. |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | `sync: false` | R2 API token. |
| `AWS_S3_BUCKET_NAME` | value | e.g. `brightbyte-uploads`. |
| `AWS_S3_ENDPOINT_URL` | `sync: false` | R2: `https://<accountid>.r2.cloudflarestorage.com`. |
| `AWS_REGION` | value `auto` | R2 expects `auto`. |
| `USE_MINIO` | value `0` | Off — we use R2 directly, not MinIO. |
| `ALLOWED_HOSTS` | value (real host) | **HARDEN** — never leave `*`. |
| `CORS_ALLOWED_ORIGINS` | value (real origins) | **HARDEN** — no allow-all fallback. |
| `WEB_URL` / `APP_BASE_URL` | value (public URL) | Used in email links + S3 custom-domain logic. |
| `DEBUG` | value `0` | Production. |
| `DJANGO_SETTINGS_MODULE` | value `plane.settings.production` | Enables Scout/JSON logging path. |
| `GUNICORN_WORKERS` | value `2`–`4` | Tune to plan CPU. |
| `PORT` | value `8000` | Render injects `$PORT`; entrypoint already reads `${PORT:-8000}`. |
| `LIVE_SERVER_SECRET_KEY` | `generateValue` (shared with live) | Shared secret between API and live server. |

### SMTP (invites/notifications) — required for the product to function

`ENABLE_SMTP`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT` (587), `EMAIL_FROM`, `EMAIL_USE_TLS=1`. Note: Plane reads most of these from `InstanceConfiguration` (DB) with env as the seed/fallback — set them as env so `configure_instance` seeds them on first boot, then they're editable in the admin app.

### Live server — required

`PORT=3000`, `API_BASE_URL` (internal hostport of the API service), `REDIS_URL` (shared Key Value for cross-instance Yjs sync), `LIVE_SERVER_SECRET_KEY` (must match API's).

### Frontends (build-time only — `VITE_*`)

`VITE_API_BASE_URL`, `VITE_WEB_BASE_URL`, `VITE_ADMIN_BASE_URL`, `VITE_ADMIN_BASE_PATH=/god-mode`, `VITE_SPACE_BASE_URL`, `VITE_SPACE_BASE_PATH=/spaces`, `VITE_LIVE_BASE_URL`, `VITE_LIVE_BASE_PATH=/live`. **These are compiled into the bundle at `pnpm turbo run build` — they are NOT runtime vars.** Set them as the static-site `buildCommand` env or as Docker `buildArgs`.

### Optional integrations (off by default)

`GOOGLE_CLIENT_ID/SECRET`, `GITHUB_CLIENT_ID/SECRET`, `GITLAB_*`, `GITEA_*` (OAuth); `LLM_API_KEY/LLM_PROVIDER/LLM_MODEL` (Byte AI); `UNSPLASH_ACCESS_KEY` (covers); `POSTHOG_*`, `SCOUT_KEY`, `SENTRY_DSN`, `OTLP_ENDPOINT` (telemetry). Set `OTLP_ENDPOINT=""` / disable the metrics push if you don't want data going to `telemetry.plane.so`.

---

## Object Storage: Recommendation & Rationale

**Recommend: Cloudflare R2** (HIGH confidence on capability; MEDIUM on it being "best for you").

| Recommended | Alternative | When to use the alternative |
|-------------|-------------|------------------------------|
| **Cloudflare R2** | AWS S3 | Use S3 if you need a specific AWS region for compliance, S3 Object Lock, or deep AWS-ecosystem integration. S3 charges $0.09/GB egress — costly for an attachment-heavy PM tool. |
| **Cloudflare R2** | Backblaze B2 | B2 is the cheapest storage ($/GB) and egress is free **only through Cloudflare's CDN**; raw B2 egress is ~$0.01/GB. Pick B2 if storage volume dominates and you're already fronting with Cloudflare. |

**Why R2 specifically:**
- **Zero egress fees.** Attachments/exports are downloaded repeatedly; S3 egress would be the dominant cost. (HIGH)
- **Full S3 API incl. presigned URLs.** Plane requires both presigned POST (upload) and presigned GET (download) via `boto3` — R2 supports both. (HIGH — confirmed R2 implements the S3 presign API; MEDIUM on edge-case parity.)
- **Flat, predictable pricing** and a generous free tier for getting started.
- **Caveat to flag for the deploy phase:** R2 computes multipart-upload ETags differently from S3. If any Plane code asserts S3-style multipart ETags it could misbehave; Plane's uploads are small (5 MB default `FILE_SIZE_LIMIT`), so multipart is unlikely to trigger — but verify during testing. (MEDIUM)

**Config:** Set `AWS_S3_ENDPOINT_URL` to the R2 S3 endpoint, `AWS_REGION=auto`, `USE_MINIO=0`, and create the bucket (the API entrypoint runs `create_bucket`, but pre-creating it in R2 is safer). Leave `MINIO_ENDPOINT_SSL` unset.

---

## SMTP: Recommendation & Rationale

**Recommend: Resend** (MEDIUM confidence — choice is preference-driven; all options work via plain SMTP).

| Recommended | Alternative | When to use the alternative |
|-------------|-------------|------------------------------|
| **Resend** | Brevo | Brevo's 300 emails/day-forever free tier beats Resend if you want zero ongoing cost and low volume; also bundles marketing/CRM. |
| **Resend** | Postmark | Postmark if deliverability is mission-critical (median <10s, top inbox placement) — worth it for invite/auth emails specifically. |
| **Resend** | Amazon SES | SES if you want lowest cost at high volume and don't mind more setup (domain verification, sandbox exit). |

Plane uses Django's stock SMTP backend, so any provider's SMTP credentials drop in. Resend wins on developer experience + a 3,000 emails/month free tier, which comfortably covers a multi-client invite/notification load. Whatever you pick, **verify your sending domain (SPF/DKIM/DMARC)** or invite emails will land in spam.

---

## What NOT to Use

| Avoid | Why | Use instead |
|-------|-----|-------------|
| **Render Free Postgres** for prod | Expires after **30 days** (14-day grace, then deleted), 1 GB cap, **no backups** | `pro-4gb`+ paid Postgres |
| **Render Free web services** for api/live | Cold-start ~1 min after 15 min idle → dropped WebSockets, slow first request, missed Celery responsiveness | `starter`/`standard`+ paid |
| **Free Key Value** for prod | No disk persistence → Celery results / sessions lost on restart | Paid Key Value (disk-backed) |
| **Deploying the Caddy proxy (`apps/proxy`)** | Render already routes + terminates TLS; Caddy would be a redundant, single-point bottleneck and conflicts with Render's port model | Render router + custom domain + static-site `routes` |
| **Relying on Redis as the Celery broker without a code change** | Plane's `common.py` builds an `amqp://` URL only; there is no `REDIS_URL`-as-broker branch | CloudAMQP/RabbitMQ, OR add a broker-from-Redis code path (see Pitfalls) |
| **Setting `VITE_*` as runtime env on static sites** | Vite inlines them at build; runtime env is ignored by an already-built bundle | Pass as `buildCommand` env / Docker `buildArgs` |
| **`numInstances > 1` on the beat worker** | Duplicate beat schedulers → duplicate scheduled tasks (double emails, double cleanups) | `numInstances: 1` always |
| **`ALLOWED_HOSTS="*"` / CORS allow-all** (current defaults) | Security debt flagged in CONCERNS; unacceptable for real client data | Explicit host + origin allowlists |

---

## Pitfalls / Gotchas (deploy-phase research flags)

1. **Celery broker is AMQP-only (HIGH).** `apps/api/plane/settings/common.py:309-312`. Options, in order of cleanliness:
   - **(a)** Provision CloudAMQP, set `AMQP_URL` → zero code change, extra vendor + cost.
   - **(b)** Run RabbitMQ as a Render **private service** (`type: pserv`, `runtime: image`, `rabbitmq:3.13-management-alpine`) with a persistent disk → no extra vendor, more ops.
   - **(c)** Add ~3 lines so `CELERY_BROKER_URL = REDIS_URL` when no AMQP is configured (Celery fully supports a Redis broker) → reuses Render Key Value, no extra infra. **Recommended long-term**, but it's a code change to a brownfield repo — flag for an explicit decision.
2. **Build-time `VITE_*` (HIGH).** Covered above. The riskiest mismatch source: changing your public domain later requires a **rebuild** of web/admin/space, not just an env edit.
3. **No single-host path routing like Caddy (MEDIUM).** Decide subdomain-per-service vs single-domain-with-rewrites early; it determines every `VITE_*_BASE_URL` and `*_BASE_PATH` value and the OAuth redirect URIs.
4. **Migrations via `preDeployCommand` (MEDIUM).** Use the migrator entrypoint as the API service's pre-deploy command so schema changes apply once before cutover; the api/worker/beat entrypoints already `wait_for_migrations`, so they'll block until it's done.
5. **`collectstatic` + Django static (LOW).** The api entrypoint runs `collectstatic`; `/static/*` is served by Django itself (whitenoise/Django), so the API web service must serve those routes — fine on Render.
6. **WebSocket sticky sessions (MEDIUM).** Render's LB assigns WS connections randomly across instances; the Hocuspocus Redis extension already syncs state across instances via `REDIS_URL`, so multi-instance `live` is safe **only** with Key Value wired up. If you scale `live` past 1 instance, the shared `REDIS_URL` is mandatory.
7. **Region pinning (LOW).** Put Postgres, Key Value, and all services in the **same Render region** so internal networking is free and low-latency; cross-region uses public URLs.
8. **Telemetry egress (LOW).** Default OTLP endpoint is `telemetry.plane.so`; disable or repoint for a private client deployment.

---

## Version Compatibility

| Component | Version on Render | Compatible with Plane's expectation | Notes |
|-----------|-------------------|--------------------------------------|-------|
| Postgres | **17** (13–18 offered) | Plane ships on 15.7; Django 4.2 + psycopg 3 support PG 17 fine | Pick 17 (or 16 for conservatism); avoid 18 until validated. |
| Key Value | **Valkey 8** | Plane targets Valkey 7.2 / Redis 5 client; Valkey 8 is a Redis drop-in | `redis-py` 5.0.4 and `ioredis` 5.7 both work with Valkey 8. (HIGH) |
| RabbitMQ (CloudAMQP) | 3.13.x | Plane targets 3.13.6 | Match major/minor where possible. |
| Node | 22 (in Dockerfiles) | Pinned 22.18.0 | Render builds from your Dockerfile, so the pinned version is honored. |
| Python | 3.12.10 (in Dockerfile.api) | Pinned 3.12.x | Same — Docker build controls it. |

---

## Sources

- [Render Blueprint YAML Reference](https://render.com/docs/blueprint-spec) — service `type`/`runtime`/`plan` values, `fromService`/`fromDatabase`/`fromGroup`, `generateValue`, `sync:false`, `databases:`, static `routes`. (HIGH)
- [Render Key Value docs](https://render.com/docs/key-value) + [changelog: Valkey 8](https://render.com/changelog/new-render-key-value-instances-run-valkey-8) — `type: keyvalue`, Valkey 8, persistence, `connectionString`. (HIGH)
- [Render Postgres docs](https://render.com/docs/postgresql-creating-connecting) — PG 13–18, connection strings, max connections by RAM. (HIGH)
- [Render free Postgres expiry changelog](https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90) — 30-day expiry, 14-day grace, no backups. (HIGH)
- [Render WebSockets docs](https://render.com/docs/websocket) + [free WS changelog](https://render.com/changelog/free-web-services-now-remain-active-while-receiving-websocket-messages) — native WS, free spin-down behavior. (HIGH)
- [Render Monorepo Support](https://render.com/docs/monorepo-support) + [Docker on Render](https://render.com/docs/docker) — `rootDir`, `dockerfilePath`, `dockerContext`. (HIGH)
- [CloudAMQP plans](https://www.cloudamqp.com/plans.html) — managed RabbitMQ, Little Lemur free/shared tier. (MEDIUM)
- Object storage comparisons: [Mixpeek 2026](https://mixpeek.com/blog/object-storage-comparison-2026), [APIScout R2/S3/B2 2026](https://apiscout.dev/guides/cloudflare-r2-vs-aws-s3-vs-backblaze-b2-cost-guide-2026), [FlowVerify cost breakdown](https://www.flowverify.co/blog/cloudflare-r2-vs-s3-vs-backblaze-b2-cost-breakdown) — egress, presign, ETag caveat. (MEDIUM)
- SMTP comparisons: [Brevo: best transactional 2026](https://www.brevo.com/blog/best-transactional-email-services/), [buildmvpfast email pricing](https://www.buildmvpfast.com/api-costs/email) — free tiers, deliverability. (MEDIUM)
- **In-repo (HIGH):** `apps/api/plane/settings/common.py:300-312` (AMQP-only broker), `apps/api/Dockerfile.api`, `apps/live/Dockerfile.live`, `apps/web/Dockerfile.web`, `apps/space/Dockerfile.space`, `apps/proxy/Caddyfile.ce`, `docker-compose.yml`, `apps/api/bin/docker-entrypoint-*.sh`, `apps/*/.env.example`.

---
*Stack research for: Render.com deployment of the Bright-Byte PMP (Plane) monorepo*
*Researched: 2026-06-01*
