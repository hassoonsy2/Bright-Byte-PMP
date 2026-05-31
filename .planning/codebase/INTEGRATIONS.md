# External Integrations

**Analysis Date:** 2026-05-31

## OAuth Providers

All OAuth credentials are stored in the `InstanceConfiguration` DB model and loaded via `plane.license.utils.instance_value.get_configuration_value()`. Environment variables are the fallback/seed defaults. Config keys are defined in `apps/api/plane/utils/instance_config_variables/core.py`.

**GitHub OAuth:**
- Purpose: User authentication and project importer (issues/data import from GitHub)
- Provider implementation: `apps/api/plane/authentication/provider/oauth/github.py`
- Views: `apps/api/plane/authentication/views/app/github.py`, `apps/api/plane/authentication/views/space/github.py`
- Config keys: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_ORGANIZATION_ID`, `ENABLE_GITHUB_SYNC`
- Env vars: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `GITHUB_ORGANIZATION_ID`, `GITHUB_ACCESS_TOKEN`
- Importer model: `apps/api/plane/db/models/importer.py` (service value: `"github"`)

**Google OAuth:**
- Purpose: User authentication
- Provider implementation: `apps/api/plane/authentication/provider/oauth/google.py`
- Views: `apps/api/plane/authentication/views/app/google.py`, `apps/api/plane/authentication/views/space/google.py`
- Config keys: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `ENABLE_GOOGLE_SYNC`
- Env vars: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

**GitLab OAuth:**
- Purpose: User authentication (self-hosted or gitlab.com)
- Provider implementation: `apps/api/plane/authentication/provider/oauth/gitlab.py`
- Views: `apps/api/plane/authentication/views/app/gitlab.py`, `apps/api/plane/authentication/views/space/gitlab.py`
- Config keys: `GITLAB_HOST` (default: `https://gitlab.com`), `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`, `ENABLE_GITLAB_SYNC`
- Env vars: `GITLAB_HOST`, `GITLAB_CLIENT_ID`, `GITLAB_CLIENT_SECRET`

**Gitea OAuth:**
- Purpose: User authentication (self-hosted Gitea instances)
- Provider implementation: `apps/api/plane/authentication/provider/oauth/gitea.py`
- Views: `apps/api/plane/authentication/views/app/gitea.py`, `apps/api/plane/authentication/views/space/gitea.py`
- Config keys: `IS_GITEA_ENABLED`, `GITEA_HOST`, `GITEA_CLIENT_ID`, `GITEA_CLIENT_SECRET`, `ENABLE_GITEA_SYNC`
- Env vars: `GITEA_HOST`, `GITEA_CLIENT_ID`, `GITEA_CLIENT_SECRET`

## Data Storage

**Primary Database:**
- PostgreSQL 15.7 (Docker image: `postgres:15.7-alpine`)
- Client: `psycopg` 3.3.0 + `dj-database-url` 2.1.0
- Connection env vars: `DATABASE_URL` (preferred) OR `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- Read replica support: enable with `ENABLE_READ_REPLICA=1`; connection via `DATABASE_READ_REPLICA_URL` or individual `POSTGRES_READ_REPLICA_*` vars
- ORM: Django ORM; migrations at `apps/api/plane/db/migrations/`
- Custom DB router: `apps/api/plane/utils/core/dbrouters.py` (read replica routing)

**Cache / Session Store:**
- Redis (Valkey 7.2.11 Docker image: `valkey/valkey:7.2.11-alpine`)
- Client: `redis` 5.0.4 + `django-redis` 5.4.0 (API), `ioredis` 5.7.0 (live server)
- Connection env var: `REDIS_URL`
- SSL: auto-detected when URL starts with `rediss://`
- Settings: `apps/api/plane/settings/common.py`, `apps/api/plane/settings/redis.py`

**File Storage (Object Storage):**
- Default: AWS S3 (via `boto3` 1.34.96 + `django-storages` 1.14.2)
- Self-hosted alternative: MinIO (S3-compatible; Docker image: `minio/minio`)
- Storage backend: `apps/api/plane/settings/storage.py` (`S3Storage` class)
- Env vars: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME`, `AWS_REGION`, `AWS_S3_ENDPOINT_URL`
- MinIO-specific: `USE_MINIO=1`, `MINIO_ENDPOINT_URL`, `MINIO_ENDPOINT_SSL`
- Presigned URLs: both upload (`generate_presigned_post`) and download (`generate_presigned_url`) supported
- Signed URL expiry: `SIGNED_URL_EXPIRATION` env var (default: 3600 seconds)
- File size limit: `FILE_SIZE_LIMIT` env var (default: 5,242,880 bytes = 5 MB)

## Message Queue

**RabbitMQ:**
- Docker image: `rabbitmq:3.13.6-management-alpine`
- Used as Celery broker
- Env vars: `AMQP_URL` (preferred) OR `RABBITMQ_HOST`, `RABBITMQ_PORT`, `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_VHOST`
- Celery config: `apps/api/plane/celery.py`
- Beat scheduler: `django_celery_beat.schedulers.DatabaseScheduler`

**Redis (also used as Celery result backend):**
- See Cache section above; also stores Celery task state

## Authentication

**Session-based:**
- Custom session engine: `plane.db.models.session` (DB-backed sessions)
- Cookie settings: `SESSION_COOKIE_AGE` (default: 604800 s = 7 days), `SESSION_COOKIE_DOMAIN`, `SESSION_COOKIE_NAME`
- Admin session: separate cookie `admin-session-id`, 1-hour TTL

**Magic link / email OTP:**
- Implemented in `apps/api/plane/authentication/views/app/magic.py`
- One-time code sent via SMTP; no third-party magic link service

**API Key authentication:**
- Custom throttle: `API_KEY_RATE_LIMIT` env var (default: `60/minute`)
- Middleware logging: `plane.middleware.logger.APITokenLogMiddleware`

**JWT:**
- `PyJWT` 2.12.0 used for token signing (password reset, etc.)

## AI / LLM Providers

Multi-provider AI integration. Config stored in `InstanceConfiguration`. Supported providers defined in `apps/api/plane/app/views/external/base.py`.

**Supported providers:**
- OpenAI (`openai` SDK 1.63.2): models `gpt-3.5-turbo`, `gpt-4o-mini` (default), `gpt-4o`, `o1-mini`, `o1-preview`
- Anthropic: models `claude-3-5-sonnet-20240620`, `claude-3-haiku-20240307`, `claude-3-opus-20240229`, `claude-3-sonnet-20240229`
- Google Gemini: models `gemini-pro`, `gemini-1.5-pro-latest`, `gemini-pro-vision`

**Config keys:** `LLM_API_KEY` (encrypted), `LLM_PROVIDER` (default: `openai`), `LLM_MODEL` (default: `gpt-4o-mini`)
**Deprecated:** `GPT_ENGINE` (use `LLM_MODEL` instead)
**Env vars:** `LLM_API_KEY`, `LLM_PROVIDER`, `LLM_MODEL`

## Email

**Transport:**
- Standard Django SMTP backend (`django.core.mail.backends.smtp.EmailBackend`)
- No third-party email service SDK — any SMTP provider can be configured
- Config keys: `ENABLE_SMTP`, `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT` (default: 587), `EMAIL_FROM`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`
- Default `EMAIL_FROM`: `Team Plane <team@mailer.plane.so>`
- Config managed via `apps/api/plane/license/utils/instance_value.py` `get_email_configuration()`

**Email tasks (Celery):**
- `apps/api/plane/bgtasks/email_notification_task.py` - Stacks + sends notifications (every 5 min)
- `apps/api/plane/bgtasks/project_invitation_task.py`
- `apps/api/plane/bgtasks/workspace_invitation_task.py`
- `apps/api/plane/bgtasks/magic_link_code_task.py`
- `apps/api/plane/bgtasks/forgot_password_task.py`
- `apps/api/plane/bgtasks/user_activation_email_task.py`

## Telemetry & Observability

**OpenTelemetry (OTLP):**
- Packages: `opentelemetry-api==1.28.1`, `opentelemetry-sdk==1.28.1`, `opentelemetry-instrumentation-django==0.49b1`, `opentelemetry-exporter-otlp==1.28.1`, `opentelemetry-exporter-otlp-proto-grpc==1.28.1`
- Metrics pushed on a configurable interval (default: every 360 min = 6 hours) via Celery beat task `push_instance_metrics`
- Task: `apps/api/plane/license/bgtasks/telemetry_metrics.py`
- Endpoint helpers: `apps/api/plane/utils/otlp_endpoints.py`
- Default endpoint: `https://telemetry.plane.so`
- Protocol: gRPC default (port 4317); override with `OTLP_METRICS_PROTOCOL=http`
- Env vars: `OTLP_ENDPOINT`, `OTLP_METRICS_PROTOCOL`, `OTEL_EXPORTER_OTLP_METRICS_INSECURE`, `METRICS_PUSH_INTERVAL_MINUTES`

**Scout APM:**
- Package: `scout-apm==3.1.0`
- Only active in production settings (`apps/api/plane/settings/production.py`)
- Env vars: `SCOUT_MONITOR`, `SCOUT_KEY`

**PostHog (Product Analytics):**
- Package: `posthog==3.5.0` (Python SDK, API only)
- Used in `apps/api/plane/bgtasks/event_tracking_task.py` for workspace/user events
- Config keys: `POSTHOG_API_KEY`, `POSTHOG_HOST`
- Env vars: `POSTHOG_API_KEY`, `POSTHOG_HOST`

**Microsoft Clarity (Session Recording):**
- Injected as inline `<script>` in web app
- Files: `apps/web/app/root.tsx`, `apps/web/app/layout.tsx`
- Env vars: `VITE_ENABLE_SESSION_RECORDER` (flag), `VITE_SESSION_RECORDER_KEY` (Clarity project key)

**Sentry:**
- Referenced in Turbo global env: `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`, `VITE_SENTRY_DSN`, `VITE_SENTRY_ENVIRONMENT`, `VITE_SENTRY_TRACES_SAMPLE_RATE`, `VITE_SENTRY_PROFILES_SAMPLE_RATE`, `VITE_SENTRY_REPLAYS_*`, `VITE_SENTRY_SEND_DEFAULT_PII`
- Note: Sentry SDK imports not detected in current source — env vars defined but integration appears to be wired in deployment configurations rather than in-repo code

## Outgoing Webhooks

- Users can configure per-workspace webhook URLs that Plane POSTs events to
- Event delivery: `apps/api/plane/bgtasks/webhook_task.py` (`webhook_send_task` Celery task)
- SSRF protection: IP pinning via `apps/api/plane/utils/url.py`; allowlists via `WEBHOOK_ALLOWED_IPS`, `WEBHOOK_ALLOWED_HOSTS`; blocklist via `WEBHOOK_DISALLOWED_DOMAINS`
- HMAC signing: optional `secret_key` on webhook, generates `X-Plane-Signature` header
- Logs: `WebhookLog` model; retention controlled by `WEBHOOK_LOG_RETENTION_DAYS` env var (default: 14 days)
- Auto-deactivation: webhook disabled after repeated failures; deactivation email sent to owner

## Third-Party Media / Content APIs

**Unsplash:**
- Purpose: Cover image search for projects and pages
- Endpoint: `https://api.unsplash.com/`
- View: `apps/api/plane/app/views/external/base.py` (`UnsplashEndpoint`)
- URL: `apps/api/plane/app/urls/external.py` (`/unsplash/`)
- Config key: `UNSPLASH_ACCESS_KEY` (encrypted in instance config)
- Env var: `UNSPLASH_ACCESS_KEY`

## Slack Integration

- Slack SDK: `slack-sdk==3.27.1`
- DB model: `apps/api/plane/db/models/integration/slack.py`
- Used for workspace-level Slack notifications (install/link flows via `plane.db.models.integration`)

## Real-Time Collaboration (Live Server)

- Hocuspocus server (`@hocuspocus/server` 2.15.2) handles WebSocket document sessions
- Extensions:
  - `@hocuspocus/extension-redis` - Redis-based document syncing across instances
  - `@hocuspocus/extension-database` - Persists document state to the API backend
  - `@hocuspocus/extension-logger` - Structured logging
- Client provider in editor: `@hocuspocus/provider` 2.15.2 (`packages/editor`)
- Yjs CRDT: `yjs`, `y-prosemirror`, `y-protocols`, `y-indexeddb` (client-side offline persistence)
- Image processing: `sharp` 0.34.3 (in `apps/live`, for image manipulation)

## PDF / Export

- `@react-pdf/renderer` 4.3.0 + `@react-pdf/types` - Client-side PDF generation in web/space apps
- `pdf-parse` 2.4.5 (devDependency in `apps/live`) - PDF text extraction
- `export-to-csv` 1.4.0 - CSV export in web app
- `openpyxl` 3.1.2 - Excel (xlsx) export from the API backend

## CI/CD & Deployment

**CI Pipelines (`.github/workflows/`):**
- `pull-request-build-lint-api.yml` - Python 3.12 ruff lint on PR
- `pull-request-build-lint-web-apps.yml` - pnpm install + TypeScript/lint check for JS apps on PR
- `build-branch.yml` - Docker build pipeline
- `feature-deployment.yml` - Feature branch deployment
- `codeql.yml` - CodeQL security scanning

**Deployment Infrastructure:**
- Docker Compose: `docker-compose.yml` (production), `docker-compose-local.yml` (local dev with MinIO), `docker-compose-test.yml`
- Reverse proxy: Caddy (Caddyfile in `apps/proxy/`)
- Kubernetes: `deployments/kubernetes/`
- Swarm: `deployments/swarm/`
- AIO (all-in-one): `deployments/aio/` and `apps/proxy/Caddyfile.aio.ce`

## Environment Variables Summary

**Required for production API:**
- `SECRET_KEY` - Django secret key
- `DATABASE_URL` or `POSTGRES_*` vars - Database connection
- `REDIS_URL` - Redis/Valkey connection
- `AMQP_URL` or `RABBITMQ_*` vars - RabbitMQ connection
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET_NAME` - File storage

**Optional integrations (all off by default):**
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` - Google OAuth
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` - GitHub OAuth
- `GITLAB_HOST` / `GITLAB_CLIENT_ID` / `GITLAB_CLIENT_SECRET` - GitLab OAuth
- `GITEA_HOST` / `GITEA_CLIENT_ID` / `GITEA_CLIENT_SECRET` - Gitea OAuth
- `LLM_API_KEY` / `LLM_PROVIDER` / `LLM_MODEL` - AI features
- `UNSPLASH_ACCESS_KEY` - Cover image search
- `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` - SMTP email
- `POSTHOG_API_KEY` / `POSTHOG_HOST` - Product analytics
- `SCOUT_KEY` - APM monitoring
- `OTLP_ENDPOINT` - OpenTelemetry metrics endpoint
- `VITE_ENABLE_SESSION_RECORDER` / `VITE_SESSION_RECORDER_KEY` - MS Clarity session recording

---

*Integration audit: 2026-05-31*
