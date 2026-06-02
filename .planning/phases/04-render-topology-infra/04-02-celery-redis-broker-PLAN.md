---
phase: 04-render-topology-infra
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - apps/api/plane/settings/common.py
  - apps/api/plane/tests/unit/settings/test_celery_broker.py
  - apps/api/.env.example
  - .env.example
autonomous: true
requirements: [DEPLOY-05]
user_setup: []
must_haves:
  truths:
    - "Celery can use Render Key Value as the broker through explicit CELERY_BROKER_URL while retaining AMQP_URL and local RabbitMQ fallback compatibility."
    - "The Redis broker choice is documented in env examples so Render can use REDIS_URL/CELERY_BROKER_URL consistently."
    - "A unit test proves broker precedence and prevents regression to RabbitMQ-only settings."
  artifacts:
    - path: "apps/api/plane/settings/common.py"
      provides: "Runtime broker resolution"
      contains: "CELERY_BROKER_URL"
    - path: "apps/api/plane/tests/unit/settings/test_celery_broker.py"
      provides: "Unit coverage for broker env precedence"
      contains: "_resolve_celery_broker_url"
  key_links:
    - from: "render.yaml"
      to: "apps/api/plane/settings/common.py"
      via: "CELERY_BROKER_URL env"
      pattern: "CELERY_BROKER_URL"
    - from: "apps/api/.env.example"
      to: "apps/api/plane/settings/common.py"
      via: "documented broker override"
      pattern: "CELERY_BROKER_URL"
---

<objective>
Implement the Phase 4 Celery broker decision by allowing Celery to use Render Key Value through `CELERY_BROKER_URL`.

Purpose: Render has managed Key Value but no managed RabbitMQ. A small explicit Redis broker setting avoids self-running RabbitMQ and keeps local RabbitMQ defaults intact.
Output: Tested broker-resolution code plus env examples that make Render's Redis broker wiring unambiguous.
</objective>

<execution_context>
@$HOME/.codex/get-shit-done/workflows/execute-plan.md
@$HOME/.codex/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/04-render-topology-infra/04-RESEARCH.md
@.planning/phases/04-render-topology-infra/04-VALIDATION.md
@.planning/phases/04-render-topology-infra/04-PATTERNS.md
@apps/api/plane/settings/common.py
@apps/api/plane/settings/redis.py
@apps/api/plane/celery.py
@apps/api/plane/tests/unit/settings/test_retention.py
@apps/api/.env.example
@.env.example
</context>

<constraints>
- Preserve existing local RabbitMQ behavior when neither `CELERY_BROKER_URL` nor `AMQP_URL` is set.
- Preserve existing `AMQP_URL` support as the second-precedence option for anyone choosing CloudAMQP later.
- Do not replace Redis cache settings or live-server Redis settings; this plan only makes the Celery broker selectable.
- Do not add a self-run RabbitMQ service to Render.
- Do not modify Phase 5 security concerns such as `SECRET_KEY`, telemetry, or live secret comparison.
</constraints>

<threat_model>
<threat id="T-04-04" severity="high" requirement="DEPLOY-05">
<risk>Celery continues to ignore Render Redis and tries to connect to RabbitMQ-only defaults, so workers deploy but cannot process jobs.</risk>
<mitigation>Add explicit `CELERY_BROKER_URL` precedence before `AMQP_URL` and RabbitMQ fallback; test all three branches.</mitigation>
</threat>
<threat id="T-04-05" severity="high" requirement="DEPLOY-05">
<risk>Queued jobs are silently evicted when Redis is used with an eviction policy unsuitable for a broker.</risk>
<mitigation>Document and verify that Render Key Value must be paid with `noeviction`; final deploy checklist confirms the setting before onboarding.</mitigation>
</threat>
<threat id="T-04-06" severity="medium" requirement="DEPLOY-05">
<risk>A broad settings reload test destabilizes Django test startup or leaks env changes between tests.</risk>
<mitigation>Extract a small `_resolve_celery_broker_url` helper and test it directly with `monkeypatch`, matching the existing `_retention_days` unit-test pattern.</mitigation>
</threat>
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Add explicit Celery broker resolver</name>
  <read_first>
    - apps/api/plane/settings/common.py
    - apps/api/plane/settings/redis.py
    - apps/api/plane/celery.py
  </read_first>
  <files>apps/api/plane/settings/common.py</files>
  <action>
    In `apps/api/plane/settings/common.py`, add a helper named `_resolve_celery_broker_url()` near the existing RabbitMQ/Celery settings. The helper must return `os.environ["CELERY_BROKER_URL"]` when set and non-empty, then `AMQP_URL` when set and non-empty, then the current RabbitMQ URL built from `RABBITMQ_USER`, `RABBITMQ_PASSWORD`, `RABBITMQ_HOST`, `RABBITMQ_PORT`, and `RABBITMQ_VHOST`. Set the module-level `CELERY_BROKER_URL` constant from the helper. Keep existing serializer/import settings unchanged.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "_resolve_celery_broker_url\|CELERY_BROKER_URL" apps/api/plane/settings/common.py</automated>
  </verify>
  <acceptance_criteria>
    - `common.py` contains `_resolve_celery_broker_url`.
    - `CELERY_BROKER_URL` env has precedence over `AMQP_URL`.
    - `AMQP_URL` remains supported.
    - RabbitMQ env fallback remains byte-equivalent in behavior when no broker URL is set.
  </acceptance_criteria>
  <done>Celery broker resolution supports Render Redis without breaking local RabbitMQ defaults.</done>
</task>

<task type="auto">
  <name>Task 2: Cover broker precedence with unit tests</name>
  <read_first>
    - apps/api/plane/tests/unit/settings/test_retention.py
    - apps/api/plane/settings/common.py
    - apps/api/pytest.ini
  </read_first>
  <files>apps/api/plane/tests/unit/settings/test_celery_broker.py</files>
  <action>
    Create `apps/api/plane/tests/unit/settings/test_celery_broker.py` using the existing unit-test style. Import `_resolve_celery_broker_url` from `plane.settings.common`, use `pytest.mark.unit`, and use `monkeypatch` to test: explicit Redis URL in `CELERY_BROKER_URL` wins over `AMQP_URL`; `AMQP_URL` is used when `CELERY_BROKER_URL` is absent; local RabbitMQ fallback uses the configured RabbitMQ env fields; empty `CELERY_BROKER_URL` does not shadow `AMQP_URL`.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP/apps/api && pytest plane/tests/unit/settings/test_celery_broker.py -m unit</automated>
  </verify>
  <acceptance_criteria>
    - The new test file has at least four unit tests for precedence and fallback.
    - The targeted pytest command exits 0.
    - Tests do not require Render, Redis, RabbitMQ, or network access.
  </acceptance_criteria>
  <done>Broker precedence is covered by focused settings tests.</done>
</task>

<task type="auto">
  <name>Task 3: Document broker env in examples</name>
  <read_first>
    - apps/api/.env.example
    - .env.example
    - .planning/phases/04-render-topology-infra/04-RESEARCH.md
  </read_first>
  <files>apps/api/.env.example, .env.example</files>
  <action>
    Add `CELERY_BROKER_URL` to the backend and root env examples next to the Redis/RabbitMQ settings. For local examples, set it to an empty value or commented example that preserves RabbitMQ fallback. Add a Render note that production should set `CELERY_BROKER_URL` to the Render Key Value internal Redis URL and that the Key Value eviction policy must be `noeviction`.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "CELERY_BROKER_URL\|noeviction" apps/api/.env.example .env.example</automated>
  </verify>
  <acceptance_criteria>
    - `apps/api/.env.example` contains `CELERY_BROKER_URL`.
    - `.env.example` contains `CELERY_BROKER_URL`.
    - Both examples state Render Redis broker usage requires `noeviction`.
  </acceptance_criteria>
  <done>Broker env wiring is discoverable before Render deploy.</done>
</task>

</tasks>

<verification>
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP/apps/api && pytest plane/tests/unit/settings/test_celery_broker.py -m unit`
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "CELERY_BROKER_URL" apps/api/plane/settings/common.py apps/api/.env.example .env.example`
</verification>

<success_criteria>

- Celery supports Redis broker through `CELERY_BROKER_URL`.
- AMQP and local RabbitMQ fallback remain compatible.
- Unit tests prove precedence and fallback.
- Env examples warn about `noeviction`.
  </success_criteria>

<output>
After completion, create `.planning/phases/04-render-topology-infra/04-02-celery-redis-broker-SUMMARY.md`
</output>
