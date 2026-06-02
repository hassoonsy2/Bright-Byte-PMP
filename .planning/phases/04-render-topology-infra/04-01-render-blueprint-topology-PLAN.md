---
phase: 04-render-topology-infra
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - render.yaml
  - scripts/verify-render-blueprint.mjs
autonomous: true
requirements: [DEPLOY-01, DEPLOY-02]
user_setup: []
must_haves:
  truths:
    - "A root render.yaml defines the complete Phase 4 service topology: api, worker, beat, live, space, web, admin, and api preDeploy migration."
    - "Render Postgres and Render Key Value are declared on paid, non-free plans and all app services reference those managed resources."
    - "The blueprint does not hardcode real secrets; secret values are generated, synced from other services, or marked for Render dashboard entry."
  artifacts:
    - path: "render.yaml"
      provides: "Version-controlled Render blueprint for DEPLOY-01 and DEPLOY-02"
      contains: "bright-byte-api"
    - path: "scripts/verify-render-blueprint.mjs"
      provides: "Offline source assertion for Render topology"
      contains: "bright-byte-beat"
  key_links:
    - from: "render.yaml"
      to: "apps/api/Dockerfile.api"
      via: "api, worker, beat Docker services"
      pattern: "dockerfilePath: ./apps/api/Dockerfile.api"
    - from: "render.yaml"
      to: "apps/api/bin/docker-entrypoint-migrator.sh"
      via: "api preDeployCommand"
      pattern: "docker-entrypoint-migrator.sh"
    - from: "render.yaml"
      to: "apps/web/build/client and apps/admin/build/client"
      via: "staticPublishPath"
      pattern: "static"
---

<objective>
Create the source-controlled Render blueprint foundation for the full Bright-Byte PMP stack.

Purpose: Phase 4 cannot deploy repeatably until the runtime topology is expressed in `render.yaml` and verified offline before any dashboard sync.
Output: A root `render.yaml` with the required services/resources and a deterministic verifier script that catches topology drift without network access.
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
@docker-compose.yml
@docker-compose-local.yml
@apps/api/Dockerfile.api
@apps/api/bin/docker-entrypoint-api.sh
@apps/api/bin/docker-entrypoint-worker.sh
@apps/api/bin/docker-entrypoint-beat.sh
@apps/api/bin/docker-entrypoint-migrator.sh
@apps/live/Dockerfile.live
@apps/space/Dockerfile.space
@apps/web/Dockerfile.web
@apps/admin/Dockerfile.admin
@apps/web/package.json
@apps/admin/package.json
@apps/space/package.json
</context>

<constraints>
- Do not add a Caddy-style reverse proxy service in Phase 4; use first-class Render service URLs and custom domains.
- Do not add self-hosted Postgres, Redis, RabbitMQ, or MinIO services to Render. Postgres and Key Value must be managed Render resources; R2/SMTP are external and handled in later plans.
- Render static sites must use build commands and publish paths, not the nginx Docker runtime.
- Use placeholders or generated values for secrets. Never put real credentials in `render.yaml`.
- Keep Phase 5 hardening out of this plan except where deployment correctness requires explicit env wiring.
</constraints>

<threat_model>
<threat id="T-04-01" severity="high" requirement="DEPLOY-01">
<risk>The blueprint omits one runtime process or runs multiple beat schedulers, causing missing live behavior or duplicate scheduled jobs.</risk>
<mitigation>Declare separate services for `bright-byte-api`, `bright-byte-worker`, `bright-byte-beat`, `bright-byte-live`, `bright-byte-space`, `bright-byte-web`, and `bright-byte-admin`; verifier asserts exactly one beat service and `docker-entrypoint-beat.sh` appears once.</mitigation>
</threat>
<threat id="T-04-02" severity="high" requirement="DEPLOY-02">
<risk>A free or ephemeral datastore is accidentally used for production, risking data loss or Celery job eviction.</risk>
<mitigation>Declare Render managed Postgres and Render Key Value on non-free plans; verifier rejects `free` datastore plans and requires services to consume managed resource connection strings.</mitigation>
</threat>
<threat id="T-04-03" severity="medium" requirement="DEPLOY-01">
<risk>Static-site outputs do not match the Vite base paths, especially admin under `/god-mode`, producing broken assets after deploy.</risk>
<mitigation>Encode static build commands, publish paths, and rewrite rules explicitly; verifier checks web publishes `apps/web/build/client` and admin publishes a `/god-mode`-compatible output.</mitigation>
</threat>
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Draft Render blueprint topology</name>
  <read_first>
    - .planning/phases/04-render-topology-infra/04-RESEARCH.md
    - docker-compose.yml
    - docker-compose-local.yml
    - apps/api/Dockerfile.api
    - apps/live/Dockerfile.live
    - apps/space/Dockerfile.space
    - apps/web/Dockerfile.web
    - apps/admin/Dockerfile.admin
  </read_first>
  <files>render.yaml</files>
  <action>
    Create `render.yaml` at the repo root. Define managed resources named `bright-byte-postgres` and `bright-byte-redis` using paid, non-free plans. Define Docker services `bright-byte-api`, `bright-byte-worker`, `bright-byte-beat`, `bright-byte-live`, and `bright-byte-space`. Use `./apps/api/Dockerfile.api` with `./apps/api` context for API, worker, and beat. Use root context for live and space. Set API `preDeployCommand` to run `./bin/docker-entrypoint-migrator.sh`. Override worker and beat commands with `./bin/docker-entrypoint-worker.sh` and `./bin/docker-entrypoint-beat.sh`. Define static services `bright-byte-web` and `bright-byte-admin` with pnpm/turbo build commands and publish paths derived from the Dockerfiles. Keep all secret values generated or dashboard-synced, never literal credentials.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && test -f render.yaml</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "bright-byte-api\|bright-byte-worker\|bright-byte-beat\|bright-byte-live\|bright-byte-space\|bright-byte-web\|bright-byte-admin" render.yaml</automated>
  </verify>
  <acceptance_criteria>
    - `render.yaml` contains all seven Render services by exact name.
    - `render.yaml` contains `docker-entrypoint-migrator.sh`, `docker-entrypoint-worker.sh`, and `docker-entrypoint-beat.sh`.
    - `render.yaml` contains `apps/api/Dockerfile.api`, `apps/live/Dockerfile.live`, and `apps/space/Dockerfile.space`.
    - `render.yaml` does not contain a real password, access key, SMTP secret, or R2 secret.
  </acceptance_criteria>
  <done>The Render blueprint declares the full stack and managed resources without hardcoded secrets.</done>
</task>

<task type="auto">
  <name>Task 2: Add offline blueprint verifier</name>
  <read_first>
    - render.yaml
    - package.json
    - .planning/phases/04-render-topology-infra/04-VALIDATION.md
  </read_first>
  <files>scripts/verify-render-blueprint.mjs</files>
  <action>
    Create `scripts/verify-render-blueprint.mjs`. Use the `yaml` package if available from the workspace; otherwise implement a narrow verifier that reads `render.yaml` and asserts required strings and counts. The script must run with `node scripts/verify-render-blueprint.mjs`, perform no network calls, and exit nonzero with clear messages if a required service, Dockerfile path, entrypoint, static publish path, paid datastore plan, or generated/synced secret marker is missing. Reject more than one `bright-byte-beat` service and reject any datastore plan that is exactly `free`.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && node scripts/verify-render-blueprint.mjs</automated>
  </verify>
  <acceptance_criteria>
    - The verifier exits 0 against the new `render.yaml`.
    - The verifier asserts exactly one beat scheduler.
    - The verifier asserts Postgres and Key Value exist and are not on `free`.
    - The verifier asserts `bright-byte-web` and `bright-byte-admin` are static services, not Docker services.
  </acceptance_criteria>
  <done>Offline topology verification is available and green.</done>
</task>

<task type="auto">
  <name>Task 3: Reconcile static-site paths before handoff</name>
  <read_first>
    - render.yaml
    - apps/web/vite.config.ts
    - apps/admin/vite.config.ts
    - apps/web/Dockerfile.web
    - apps/admin/Dockerfile.admin
  </read_first>
  <files>render.yaml, scripts/verify-render-blueprint.mjs</files>
  <action>
    Review web and admin static output handling. Web should publish the Vite client build at root. Admin must preserve the `/god-mode` base path from `VITE_ADMIN_BASE_PATH`; if Render static publishing cannot mount `apps/admin/build/client` at `/god-mode` directly, make the build command copy the client build into a render-only directory containing `god-mode/` and publish that directory. Add rewrite rules in `render.yaml` for single-page app fallback without shadowing API, live, or Space origins.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && node scripts/verify-render-blueprint.mjs</automated>
  </verify>
  <acceptance_criteria>
    - `render.yaml` has a web static publish path rooted at `apps/web/build/client`.
    - `render.yaml` has an admin static publish path compatible with `/god-mode`.
    - `VITE_ADMIN_BASE_PATH` remains `/god-mode`; it is not flattened to `/`.
    - The verifier documents and enforces the chosen admin publish-path strategy.
  </acceptance_criteria>
  <done>Static-site paths are explicit and verifier-protected.</done>
</task>

</tasks>

<verification>
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && node scripts/verify-render-blueprint.mjs`
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "docker-entrypoint-migrator.sh" render.yaml`
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "bright-byte-beat" render.yaml`
</verification>

<success_criteria>

- `render.yaml` exists and declares the full Phase 4 Render topology.
- Managed Postgres and Key Value are paid and referenced by app services.
- The verifier runs offline and catches missing topology, duplicate beat, free datastore plans, and static path mistakes.
  </success_criteria>

<output>
After completion, create `.planning/phases/04-render-topology-infra/04-01-render-blueprint-topology-SUMMARY.md`
</output>
