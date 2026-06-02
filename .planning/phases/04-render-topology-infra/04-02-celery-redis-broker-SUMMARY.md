---
phase: 04-render-topology-infra
plan: 02
status: complete
completed_at: 2026-06-02T23:12:11Z
requirements_completed: [DEPLOY-05]
commits:
  - 330d27425a
  - d1dfafb77f
  - ce8085f82e
---

# Summary: 04-02 Celery Redis Broker

## Outcome

Implemented explicit Celery broker selection for Render Key Value while preserving AMQP and local RabbitMQ fallback behavior.

## Completed Tasks

- Added `_resolve_celery_broker_url()` in `apps/api/plane/settings/common.py` with precedence: `CELERY_BROKER_URL`, then `AMQP_URL`, then RabbitMQ env fields.
- Added unit coverage for Redis-over-AMQP precedence, AMQP fallback, empty `CELERY_BROKER_URL`, and configured RabbitMQ fallback.
- Documented `CELERY_BROKER_URL` in root and backend env examples, including Render Key Value `noeviction` guidance.

## Verification

- `docker compose -f docker-compose-test.yml run --rm api-tests pytest plane/tests/unit/settings/test_celery_broker.py -m unit` passed: 4 tests.
- `grep -n "CELERY_BROKER_URL" apps/api/plane/settings/common.py apps/api/.env.example .env.example` found the runtime setting and both env examples.
- Deleted-file check across implementation commits returned no deleted files.

## Notes

- Local `pytest` could not run before containerization because backend dependencies were not installed on the host (`ModuleNotFoundError: No module named 'celery'`).
- A minimal ignored `apps/api/.env` was created so the documented Docker test stack could run without executing the broad `setup.sh`.
- The Docker test stack was torn down with `docker compose -f docker-compose-test.yml down -v` after verification.
