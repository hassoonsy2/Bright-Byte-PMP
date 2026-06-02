---
phase: 04
slug: render-topology-infra
status: draft
created: 2026-06-03
---

# Phase 04 Pattern Map

## Existing Deployment Shape

- Local orchestration is defined in `docker-compose.yml` and `docker-compose-local.yml`. The Render blueprint should preserve the service split from Compose rather than inventing a new runtime: API web, Celery worker, exactly one Celery beat, live WebSocket, Space SSR, web static, admin static, and migrations before API deploy.
- API, worker, beat, and migrator share the API image built from `apps/api/Dockerfile.api`. Runtime behavior is selected by the entrypoint scripts in `apps/api/bin/`.
- `apps/live/Dockerfile.live` and `apps/space/Dockerfile.space` require the monorepo root as Docker build context because they copy pruned workspace packages.
- `apps/web/Dockerfile.web` and `apps/admin/Dockerfile.admin` prove the intended static outputs: `apps/web/build/client` and `apps/admin/build/client`. Render static sites cannot run Docker images, so the blueprint should use equivalent pnpm/turbo build commands and publish paths.

## Configuration Patterns

- Backend settings live in `apps/api/plane/settings/common.py`. Existing env parsing favors direct `os.environ.get(...)`, small helper functions when parsing is testable, and fallback behavior that preserves local Docker defaults.
- Redis is already consumed through `REDIS_URL` in Django cache settings and `apps/api/plane/settings/redis.py`. If Redis is the Celery broker on Render, add explicit `CELERY_BROKER_URL` support instead of overloading unrelated RabbitMQ variables.
- Object storage is already S3-compatible through `apps/api/plane/settings/storage.py`. Cloudflare R2 should use `AWS_S3_ENDPOINT_URL`, `AWS_S3_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION=auto`, and `USE_MINIO=0`.
- SMTP is configured through instance values seeded from `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`, and `EMAIL_USE_SSL`. `EMAIL_FROM` is already part of the Bright-Byte branding defaults.
- Browser-origin topology is split between backend envs (`WEB_URL`, `APP_BASE_URL`, `ADMIN_BASE_URL`, `ADMIN_BASE_PATH`, `SPACE_BASE_URL`, `SPACE_BASE_PATH`, `LIVE_BASE_URL`, `LIVE_BASE_PATH`, `COOKIE_DOMAIN`, `CORS_ALLOWED_ORIGINS`) and Vite build-time envs (`VITE_*`). The plan must keep those pairs consistent.

## Test And Verification Patterns

- API settings unit tests live under `apps/api/plane/tests/unit/settings/` and use `pytest.mark.unit` plus `monkeypatch` or `patch.dict` for env parsing.
- For deployment config, there is no existing root script directory. Creating `scripts/verify-render-blueprint.mjs` is acceptable if it stays small, deterministic, offline, and does not require network access.
- Phase validation already calls for source assertions first, then live/manual checks for Render, R2, SMTP, workers, WebSocket auth, cookies, and onboarding.

## UI Pattern Guidance

- `04-UI-SPEC.md` says Phase 4 should not create a new deployment dashboard or redesign. If a later task touches UI copy, it must use the existing internal app patterns, design tokens, and `@bright-byte/ui` components.
- Phase 4 implementation should be mostly infrastructure, docs, env examples, and verification artifacts. Any visible UI change is suspicious unless it directly fixes deployed origin behavior.

## Risks To Carry Into Plans

- Static-site path handling is the biggest blueprint trap: admin is built for `/god-mode`, while web is rooted at `/`. The plan should force a verifier to prove publish paths and rewrites explicitly.
- Redis-as-broker is only safe if Render Key Value is on a paid plan with `noeviction`; otherwise Celery jobs can be evicted silently.
- Real success cannot be proven locally. The final plan must include human checkpoints for Render dashboard sync, R2 bucket/CORS/credentials, SMTP credentials, custom domains/OAuth redirect URIs, and a live onboarding record.
