# Phase 4: Render Topology + Infra - Research

**Researched:** 2026-06-02
**Status:** Complete
**Phase requirements:** DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05, DEPLOY-06, DEPLOY-07

## Research Question

What needs to be known to plan a Render deployment for the full Bright-Byte PMP stack, using the current monorepo Docker/runtime shape, while filling the Render gaps for object storage, SMTP, and Celery broker?

## Executive Summary

Plan Phase 4 as an infrastructure/configuration phase with one small application-settings change only if the Redis Celery broker option is chosen. The repo already has service-specific Dockerfiles and entrypoints for `api`, `worker`, `beat-worker`, `migrator`, `live`, `space`, `web`, and `admin`, plus env support for `DATABASE_URL`, `REDIS_URL`, `AMQP_URL`, S3-compatible storage, SMTP config, and baked Vite base URLs.

Recommended target:

- Render `render.yaml` at repo root, defining one shared production topology.
- Render paid Postgres and paid Render Key Value in the same region, with internal URLs injected into services.
- Cloudflare R2 as the external S3-compatible attachment store, using `AWS_S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com`, `AWS_REGION=auto`, `USE_MINIO=0`, and bucket CORS for browser presigned uploads/downloads.
- Transactional SMTP through an external provider on authenticated TLS/STARTTLS, with `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, and `EMAIL_FROM`.
- Celery broker: prefer the small Redis-broker change that honors an explicit `CELERY_BROKER_URL` and points it at Render Key Value with `noeviction`, unless the owner wants RabbitMQ semantics enough to pay for CloudAMQP or operate RabbitMQ separately.
- Proxy/origin: do not reproduce the Docker Compose Caddy proxy on Render for v1. Use first-class Render service URLs/custom domains and choose a single public app origin plus path-based API/live/admin/space settings where the current app supports them. Verify auth cookies and OAuth redirect URIs from the final deployed origins, not from local assumptions.

## External Platform Facts

Sources checked:

- Render Blueprint YAML reference: https://render.com/docs/blueprint-spec
- Render Docker deploys: https://render.com/docs/docker
- Render Background Workers: https://render.com/docs/background-workers
- Render Key Value: https://render.com/docs/key-value
- Render Private Network: https://render.com/docs/private-network
- Render WebSockets: https://render.com/docs/websocket
- Render free tier limitations: https://render.com/free
- Cloudflare R2 S3 API: https://developers.cloudflare.com/r2/api/s3/
- Cloudflare R2 presigned URLs: https://developers.cloudflare.com/r2/api/s3/presigned-urls/
- Cloudflare R2 CORS: https://developers.cloudflare.com/r2/buckets/cors/

Render blueprint facts relevant to the plan:

- `render.yaml` supports `services`, `databases`, `envVarGroups`, and project/environment grouping.
- Service `type` includes `web`, `worker`, `pserv`, `cron`, and `keyvalue`; static sites are `type: web` with `runtime: static`.
- Docker services use `runtime: docker`, `dockerfilePath`, `dockerContext`, and optional `dockerCommand`.
- Static sites do not run Dockerfiles; they need a build command and `staticPublishPath`. This conflicts with a literal reading of "web + admin Static Sites from existing Dockerfiles". For planning, satisfy the "Static Sites" requirement by deriving build commands, publish paths, and baked `VITE_*` values from the Dockerfiles instead of deploying `web` and `admin` as Docker web services.
- `preDeployCommand` runs after build and before start, but the repo's current migrator is a separate Docker command (`./bin/docker-entrypoint-migrator.sh`). A dedicated `migrator` job/service plan is still needed because the roadmap explicitly asks for `migrator (preDeploy)`.
- Render can inject values from Postgres via `fromDatabase.property: connectionString` and can add shared environment groups to multiple services.
- Render Key Value uses Valkey-compatible `redis://`/`rediss://` URLs. Render recommends `noeviction` for job queues so queued jobs are not evicted.
- Render private networking gives internal addresses/URLs to web services, private services, Postgres, and Key Value. Background workers can initiate private network requests but cannot receive inbound traffic.
- Render web services can accept public WebSocket connections; clients should use `wss://` in production.
- Free Render Postgres expires after 30 days, and free web services cannot send outbound traffic on common SMTP ports. This phase must use paid tiers for production-like verification.

Cloudflare R2 facts relevant to the plan:

- R2 supports the S3-compatible API used by `boto3` and `django-storages`.
- R2 examples use endpoint URL `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` and `region_name="auto"`.
- Presigned URLs work against the S3 API domain, not custom domains.
- Browser-based presigned PUT/GET/HEAD needs R2 bucket CORS allowing the deployed app origin and the headers/methods the browser sends.

## Codebase Findings

### Current service topology

Existing local topology is in `docker-compose.yml` and `docker-compose-local.yml`:

- `web`: `apps/web/Dockerfile.web`, nginx static runtime on port 3000.
- `admin`: `apps/admin/Dockerfile.admin`, nginx static runtime under `/god-mode`.
- `space`: `apps/space/Dockerfile.space`, SSR via `react-router-serve` on port 3000.
- `api`: `apps/api/Dockerfile.api`, ASGI/gunicorn entrypoint on `${PORT:-8000}`.
- `worker`: same API image with `./bin/docker-entrypoint-worker.sh`.
- `beat-worker`: same API image with `./bin/docker-entrypoint-beat.sh`; exactly one beat is required.
- `migrator`: same API image with `./bin/docker-entrypoint-migrator.sh`.
- `live`: `apps/live/Dockerfile.live`, Node WebSocket/collaboration service on port 3000.
- Compose-only services to replace on Render: Postgres, Valkey, RabbitMQ, MinIO, Caddy proxy.

### Existing deployment-relevant env support

Backend settings in `apps/api/plane/settings/common.py` already support:

- `DATABASE_URL` via `dj_database_url`.
- `REDIS_URL`, including `rediss` TLS handling for Django cache/Redis use.
- `AMQP_URL` for Celery broker, falling back to RabbitMQ host/user/password/vhost.
- S3-compatible storage via `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`, `AWS_REGION`, `AWS_S3_ENDPOINT_URL`, `USE_MINIO`.
- Base URL/cookie topology via `WEB_URL`, `APP_BASE_URL`, `APP_BASE_PATH`, `ADMIN_BASE_URL`, `ADMIN_BASE_PATH`, `SPACE_BASE_URL`, `SPACE_BASE_PATH`, `LIVE_BASE_URL`, `LIVE_BASE_PATH`, `COOKIE_DOMAIN`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS`.
- SMTP values are read through instance configuration helpers and tasks: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `EMAIL_FROM`.

Frontend build facts:

- `apps/web/Dockerfile.web`, `apps/admin/Dockerfile.admin`, and `apps/space/Dockerfile.space` bake public `VITE_*` values during build.
- `apps/admin/vite.config.ts` uses `VITE_ADMIN_BASE_PATH` as Vite `base`.
- `apps/space/vite.config.ts` uses `VITE_SPACE_BASE_PATH` as Vite `base`.
- `apps/web/vite.config.ts` exposes `VITE_*` but has no `base` override.
- Static-site Render services must set all public `VITE_*` envs before build, not after deploy.

Live service facts:

- `apps/live/src/env.ts` requires `API_BASE_URL` and `LIVE_SERVER_SECRET_KEY`, accepts `CORS_ALLOWED_ORIGINS`, `LIVE_BASE_PATH`, and `REDIS_URL`.
- `apps/live/src/redis.ts` supports a full `REDIS_URL`.
- `apps/live/src/server.ts` mounts routes under `LIVE_BASE_PATH`.
- `apps/live/src/lib/auth-middleware.ts` currently compares `LIVE_SERVER_SECRET_KEY` with `!==`; Phase 5 owns constant-time hardening, but Phase 4 must generate and wire the same secret into API/live.

## Recommended Architecture Decisions

### D-04-01: Render service layout

Use one `render.yaml` with these resources:

- `bright-byte-postgres`: Render Postgres, paid plan, internal-only access.
- `bright-byte-key-value`: Render Key Value, paid plan, `maxmemoryPolicy: noeviction` if used for Celery broker.
- `bright-byte-api`: Docker web service from `apps/api/Dockerfile.api`.
- `bright-byte-worker`: Docker background worker from `apps/api/Dockerfile.api`, `dockerCommand: ./bin/docker-entrypoint-worker.sh`.
- `bright-byte-beat`: Docker background worker from `apps/api/Dockerfile.api`, `dockerCommand: ./bin/docker-entrypoint-beat.sh`, exactly one instance.
- `bright-byte-migrator`: migration hook/job using the API Docker image and `./bin/docker-entrypoint-migrator.sh`; if Render cannot model this exactly as a separate pre-deploy service in blueprint semantics, attach the migrator command as `preDeployCommand` to `bright-byte-api` and document that this is the concrete implementation of roadmap "migrator (preDeploy)".
- `bright-byte-live`: Docker web service from `apps/live/Dockerfile.live`.
- `bright-byte-space`: Docker web service from `apps/space/Dockerfile.space` because Space is SSR.
- `bright-byte-web`: Render static site built from the monorepo with output `apps/web/build/client`.
- `bright-byte-admin`: Render static site built from the monorepo with output `apps/admin/build/client` or `apps/admin/build/client/god-mode` depending on actual build output after verifying locally.

### D-04-02: Broker choice

Prefer Render Key Value as the Celery broker for v1 if a small settings patch is accepted:

- Add explicit `CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL")` support before the RabbitMQ fallback in `apps/api/plane/settings/common.py`.
- Set `CELERY_BROKER_URL` to a Redis URL using a dedicated database/index or prefix if supported.
- Keep `REDIS_URL` for cache/live/runtime Redis.
- Use Render Key Value `noeviction`.
- Verify `celery -A plane inspect ping` against the worker and execute one email or cleanup task.

Reasons:

- Avoids operating RabbitMQ as a stateful private service on Render.
- Avoids an additional CloudAMQP account for v1.
- The repo already depends on `redis==5.0.4`.
- Render specifically recommends `noeviction` for job queues.

Fallback if Redis broker is rejected: use CloudAMQP and set `AMQP_URL`; this requires no app code change but adds a new external dependency. Self-running RabbitMQ on Render is the highest operational burden and should be a last resort.

### D-04-03: Object storage

Use Cloudflare R2:

- `AWS_S3_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com`
- `AWS_REGION=auto`
- `AWS_S3_BUCKET_NAME=<bucket>`
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` from an R2 API token with bucket-scoped permissions.
- `USE_MINIO=0`
- R2 bucket CORS allows the deployed app origin, methods `GET`, `PUT`, `HEAD`, and headers `Content-Type`, checksum/cache headers if used by the browser.

Verification must include both API-generated presigned upload and browser upload/download from the deployed origin.

### D-04-04: SMTP

Use an external transactional SMTP provider rather than trying to send directly from Render. Configure:

- `EMAIL_HOST`
- `EMAIL_PORT=587` and `EMAIL_USE_TLS=1` for STARTTLS, unless the chosen provider requires `465` and `EMAIL_USE_SSL=1`.
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_FROM="Bright-Byte PMP <noreply@real-domain>"`

Verification must use `python manage.py test_email <recipient>` or the admin email configuration flow, then validate an invite or magic-link email reaches a real inbox.

### D-04-05: Proxy/origin topology

Do not ship the Compose Caddy proxy unchanged for Render v1. Render already terminates TLS and routes public traffic to each service/static site. The plan should explicitly choose public origins and bake them consistently.

Recommended v1 topology:

- Public web app: `https://pmp.<domain>` or Render static site URL.
- API: `https://api-pmp.<domain>` or Render service URL, with `VITE_API_BASE_URL` set to that origin and `VITE_API_BASE_PATH=/api`.
- Admin: `https://admin-pmp.<domain>/god-mode` or equivalent; set both backend `ADMIN_BASE_URL`/`ADMIN_BASE_PATH` and frontend `VITE_ADMIN_BASE_URL`/`VITE_ADMIN_BASE_PATH`.
- Space: `https://space-pmp.<domain>/spaces`; set backend and frontend equivalents.
- Live: `https://live-pmp.<domain>/live`; set `LIVE_BASE_URL`, `LIVE_BASE_PATH`, `API_BASE_URL`, `VITE_LIVE_BASE_URL`, and `VITE_LIVE_BASE_PATH`.
- `CORS_ALLOWED_ORIGINS` includes every browser origin, comma-separated, all HTTPS in production.
- `COOKIE_DOMAIN` should be unset for distinct Render subdomains during first deploy; only set to a shared parent domain after custom domains are attached and auth is verified.

Path-only single-origin deployment would require a Render reverse proxy or routing layer equivalent to `apps/proxy/Caddyfile.ce`; it is more moving parts and not the best first Render deployment.

## Implementation Planning Notes

Likely plan split:

1. Blueprint and env contract: create `render.yaml`, env group placeholders, service topology, paid datastore definitions, and docs for required dashboard secrets.
2. Broker/storage/SMTP integration: implement broker decision, R2 env/CORS instructions, SMTP env/test path, and update examples/runbook.
3. Origin/base URL build contract: set exact `VITE_*`, backend URL/cookie/CORS/CSRF values, OAuth redirect checklist, and static-site publish paths.
4. Live deployment verification: deploy/sync blueprint, run migrations, verify workers/beat, WebSocket, attachment upload/download, email, and client workspace onboarding.

Plan should avoid editing Phase 5 hardening items except where required for deployment:

- Do not harden `SECRET_KEY` boot guard in Phase 4 unless needed to deploy; Phase 5 owns SEC-01.
- Do not change live secret comparison to constant-time in Phase 4; Phase 5 owns SEC-02.
- Do not remove telemetry/print statements here; Phase 5 owns SEC-03.
- Do not add AGPL offer here; Phase 5 owns SEC-04.

## Risks and Mitigations

| Risk                                            | Impact                                                                | Mitigation                                                                                                                      |
| ----------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Static-site vs Docker wording conflict          | Planner could create an invalid Render static-site definition         | Treat web/admin as `runtime: static`; derive build commands/env from Dockerfiles; document the non-Docker static-site exception |
| `VITE_*` values are baked at build time         | Changing runtime env after deploy will not update frontend URLs       | Set all public env vars before first static-site build and force rebuild after changes                                          |
| Redis broker may share capacity with cache/live | Full Key Value could reject writes with `noeviction`                  | Use paid tier, monitor memory, consider separate Key Value for Celery if queues grow                                            |
| R2 presigned URL CORS missing                   | Attachment uploads fail only in browser                               | Include bucket CORS task and browser PUT/GET verification                                                                       |
| SMTP provider ports or credentials wrong        | Invites/magic links silently fail                                     | Add explicit test-email task and end-to-end invite/magic-link check                                                             |
| Cookie domain set too early                     | Auth works on one service but fails across others                     | Leave `COOKIE_DOMAIN` unset until custom domains share a parent domain; test session cookie after sign-in                       |
| Beat scaled above one instance                  | Duplicate scheduled tasks/emails/cleanup                              | Plan must assert exactly one `bright-byte-beat` instance                                                                        |
| Render free tiers accidentally used             | Database expiry, cold starts, SMTP port blocks, WebSocket instability | Blueprint must set paid plans and verification must inspect plan names                                                          |

## Validation Architecture

Phase 4 has both automated source/config validation and required manual/live verification.

Automated checks to plan:

- `render.yaml` parses as YAML and contains exactly the expected service/resource names.
- `render.yaml` has `bright-byte-api`, `bright-byte-worker`, `bright-byte-beat`, `bright-byte-live`, `bright-byte-space`, `bright-byte-web`, `bright-byte-admin`, and migrator/preDeploy coverage.
- Worker and beat services use `type: worker`; exactly one beat service exists.
- Docker services reference existing Dockerfiles:
  - `apps/api/Dockerfile.api`
  - `apps/live/Dockerfile.live`
  - `apps/space/Dockerfile.space`
- Static sites have build commands and publish paths that match verified local build outputs.
- Render datastore definitions use paid plans, not `free`.
- Env examples/runbook include `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL` or `AMQP_URL`, R2 keys, SMTP keys, `LIVE_SERVER_SECRET_KEY`, `SECRET_KEY`, `CORS_ALLOWED_ORIGINS`, base URLs, and `VITE_*` build vars.
- If Redis broker is implemented, backend tests or source assertions prove `CELERY_BROKER_URL` overrides the AMQP/RabbitMQ fallback.
- `pnpm check:types` and `pnpm check:lint` pass if code changes are made.

Manual/live checks to plan:

- Render blueprint validates or syncs successfully in the Render dashboard/CLI.
- `api` deploy runs migrations before serving requests.
- `worker` processes a queued job and `beat` schedules without duplicate beat instances.
- `live` accepts a `wss://` connection at the configured `/live` path.
- A client can sign in, create a workspace/project, upload an attachment through R2 presigned browser flow, and receive an invite or magic-link email.
- Auth cookies work across the chosen web/admin/api/space/live origins.
- OAuth redirect URIs in the provider dashboard match the final deployed callback URLs if OAuth is enabled.

## Open Items for Planner

- Confirm actual Render blueprint field name for Key Value maxmemory policy before writing final YAML; current docs describe Key Value blueprint support but the exact field should be copied from the current reference while editing.
- Confirm static publish paths by running or inspecting `pnpm turbo run build --filter=web` and `--filter=admin`, because admin may publish under `apps/admin/build/client` with `/god-mode` handled by Vite base.
- Decide whether `bright-byte-migrator` is represented as a true service/job or as `preDeployCommand` on `bright-byte-api`; roadmap success requires pre-deploy migration behavior, not an always-running migrator.
- Decide final public domains before deployment. Use Render `onrender.com` URLs for first smoke test if custom DNS is not ready.

## Research Complete

The phase is plannable with the decisions and constraints above. The highest-value plan guardrails are: paid Render resources, explicit broker choice, R2 CORS verification, baked frontend envs, exactly one beat, and a live end-to-end onboarding test.
