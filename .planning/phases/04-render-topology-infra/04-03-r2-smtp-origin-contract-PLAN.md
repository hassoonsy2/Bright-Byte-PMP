---
phase: 04-render-topology-infra
plan: 03
type: execute
wave: 2
depends_on: ["04-01", "04-02"]
files_modified:
  - docs/render-deployment.md
  - render.yaml
  - .env.example
  - apps/api/.env.example
  - apps/web/.env.example
  - apps/admin/.env.example
  - apps/space/.env.example
  - apps/live/.env.example
autonomous: false
requirements: [DEPLOY-03, DEPLOY-04, DEPLOY-06]
user_setup:
  - service: cloudflare-r2
    why: "Cloudflare R2 bucket, CORS, and API tokens require account/dashboard access."
    env_vars:
      - name: AWS_ACCESS_KEY_ID
        source: "Cloudflare dashboard > R2 > Manage API tokens > Access key ID"
      - name: AWS_SECRET_ACCESS_KEY
        source: "Cloudflare dashboard > R2 > Manage API tokens > Secret access key"
      - name: AWS_S3_ENDPOINT_URL
        source: "Cloudflare dashboard > R2 > Account ID endpoint URL"
      - name: AWS_S3_BUCKET_NAME
        source: "Cloudflare dashboard > R2 > Bucket name"
    dashboard_config:
      - task: "Create R2 bucket and set CORS for deployed web/admin/space origins"
        location: "Cloudflare dashboard > R2 > Bucket > Settings > CORS"
        details: "Allow HTTPS origins that match the final Render/custom domains; allow PUT, GET, HEAD, and required Content-Type headers."
  - service: smtp-provider
    why: "SMTP host, username, password, and authenticated sender require provider dashboard access."
    env_vars:
      - name: EMAIL_HOST
        source: "SMTP provider dashboard"
      - name: EMAIL_HOST_USER
        source: "SMTP provider dashboard"
      - name: EMAIL_HOST_PASSWORD
        source: "SMTP provider dashboard"
      - name: EMAIL_PORT
        source: "SMTP provider dashboard"
      - name: EMAIL_USE_TLS
        source: "SMTP provider dashboard"
      - name: EMAIL_USE_SSL
        source: "SMTP provider dashboard"
  - service: custom-domains-and-oauth
    why: "Final HTTPS origins and OAuth redirect URIs must be configured in Render/DNS/OAuth provider dashboards."
    env_vars:
      - name: WEB_URL
        source: "Final API origin"
      - name: APP_BASE_URL
        source: "Final web app origin"
      - name: ADMIN_BASE_URL
        source: "Final admin origin"
      - name: SPACE_BASE_URL
        source: "Final Space origin"
      - name: LIVE_BASE_URL
        source: "Final live WebSocket origin"
      - name: COOKIE_DOMAIN
        source: "Shared parent domain if subdomains are used"
    dashboard_config:
      - task: "Register OAuth redirect URIs if OAuth providers are enabled"
        location: "OAuth provider dashboard"
        details: "Use the deployed API/auth redirect routes from the final origin topology."
must_haves:
  truths:
    - "R2, SMTP, and browser-origin env contracts are documented with exact variable names used by the codebase."
    - "All frontend `.env.example` files expose the same Vite base-url and base-path topology used by Render builds."
    - "Backend docs explain HTTPS-only origins, CORS, cookie domain, and OAuth redirect URI updates without adding a Phase 4 UI surface."
  artifacts:
    - path: "docs/render-deployment.md"
      provides: "Operator runbook for R2, SMTP, origin, and Render env wiring"
      contains: "Cloudflare R2"
    - path: "apps/live/.env.example"
      provides: "Live service origin and Redis contract"
      contains: "CORS_ALLOWED_ORIGINS"
  key_links:
    - from: "docs/render-deployment.md"
      to: "apps/api/plane/settings/storage.py"
      via: "R2 S3-compatible env"
      pattern: "AWS_S3_ENDPOINT_URL"
    - from: "docs/render-deployment.md"
      to: "apps/api/plane/settings/common.py"
      via: "origin and cookie env"
      pattern: "COOKIE_DOMAIN"
    - from: "render.yaml"
      to: "apps/web/.env.example"
      via: "VITE build-time env"
      pattern: "VITE_API_BASE_URL"
---

<objective>
Create the deployment contract for R2 object storage, SMTP delivery, and multi-origin browser behavior.

Purpose: The Render blueprint is only deployable when the external services and baked frontend URLs match the runtime settings that Django, live, and Vite already consume.
Output: A Render deployment runbook plus env example updates that make R2, SMTP, CORS, cookies, OAuth redirects, and Vite base paths explicit.
</objective>

<execution_context>
@$HOME/.codex/get-shit-done/workflows/execute-plan.md
@$HOME/.codex/get-shit-done/templates/summary.md
@$HOME/.codex/get-shit-done/references/checkpoints.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/REQUIREMENTS.md
@.planning/STATE.md
@.planning/phases/04-render-topology-infra/04-RESEARCH.md
@.planning/phases/04-render-topology-infra/04-VALIDATION.md
@.planning/phases/04-render-topology-infra/04-UI-SPEC.md
@.planning/phases/04-render-topology-infra/04-PATTERNS.md
@render.yaml
@.env.example
@apps/api/.env.example
@apps/web/.env.example
@apps/admin/.env.example
@apps/space/.env.example
@apps/live/.env.example
@apps/api/plane/settings/common.py
@apps/api/plane/settings/storage.py
@apps/api/plane/license/utils/instance_value.py
@apps/live/src/env.ts
@apps/web/vite.config.ts
@apps/admin/vite.config.ts
@apps/space/vite.config.ts
</context>

<constraints>
- Do not put real R2, SMTP, OAuth, or domain secrets in repo files.
- Do not create a new deployment UI. This is docs, env examples, and Render config only.
- Keep `USE_MINIO=0` for R2; do not reintroduce MinIO or Caddy proxy assumptions.
- Keep `VITE_*` values clearly marked as build-time values for static sites.
- Keep Phase 5 security hardening scoped out, but document the production values Phase 4 needs for cookies and CORS to work.
</constraints>

<threat_model>
<threat id="T-04-07" severity="high" requirement="DEPLOY-03">
<risk>R2 presigned PUT/GET fails in the browser because endpoint, bucket, region, or CORS values are inconsistent.</risk>
<mitigation>Document the exact S3-compatible env names already consumed by `S3Storage`; include R2 CORS instructions and a manual upload/download verification path.</mitigation>
</threat>
<threat id="T-04-08" severity="high" requirement="DEPLOY-04">
<risk>SMTP appears configured but transactional email jobs fail because TLS/SSL mode, sender, or provider credentials are wrong.</risk>
<mitigation>Document the EMAIL-prefixed variables, TLS/SSL exclusivity, provider dashboard setup, and the `test_email` command used by the codebase.</mitigation>
</threat>
<threat id="T-04-09" severity="high" requirement="DEPLOY-06">
<risk>Baked frontend base URLs differ from backend cookie/CORS/OAuth origins, causing login loops, blocked API calls, or broken live collaboration.</risk>
<mitigation>Update env examples and docs as one origin matrix; require `CORS_ALLOWED_ORIGINS`, `COOKIE_DOMAIN`, backend base URLs, live CORS, and frontend VITE-prefixed values to match the same HTTPS topology.</mitigation>
</threat>
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Write Render deployment runbook</name>
  <read_first>
    - .planning/phases/04-render-topology-infra/04-RESEARCH.md
    - .planning/phases/04-render-topology-infra/04-VALIDATION.md
    - docs/linting.md
    - apps/api/plane/settings/storage.py
    - apps/api/plane/license/utils/instance_value.py
    - apps/api/db/management/commands/test_email.py
  </read_first>
  <files>docs/render-deployment.md</files>
  <action>
    Create `docs/render-deployment.md` with concise operator sections for topology, Render resources, Cloudflare R2, SMTP, origin/cookie/OAuth configuration, deploy order, and verification. Include exact env variable names from the codebase. For R2, specify `AWS_REGION=auto`, `USE_MINIO=0`, `AWS_S3_ENDPOINT_URL`, `AWS_S3_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `SIGNED_URL_EXPIRATION`. For SMTP, specify `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, and `EMAIL_FROM`, plus a test path using `python manage.py test_email <recipient>` from the API container or Render shell.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "Cloudflare R2\|AWS_S3_ENDPOINT_URL\|EMAIL_HOST\|test_email\|COOKIE_DOMAIN\|VITE_API_BASE_URL" docs/render-deployment.md</automated>
  </verify>
  <acceptance_criteria>
    - `docs/render-deployment.md` contains sections for Render, R2, SMTP, origin/cookie/OAuth, and verification.
    - The document includes every R2 and SMTP env variable listed in the action.
    - The document instructs manual verification for presigned PUT/GET and email delivery.
  </acceptance_criteria>
  <done>The deployment runbook contains enough exact env and verification detail to operate Phase 4.</done>
</task>

<task type="auto">
  <name>Task 2: Align env examples with Render origin contract</name>
  <read_first>
    - render.yaml
    - .env.example
    - apps/api/.env.example
    - apps/web/.env.example
    - apps/admin/.env.example
    - apps/space/.env.example
    - apps/live/.env.example
    - apps/api/plane/settings/common.py
    - apps/live/src/env.ts
  </read_first>
  <files>render.yaml, .env.example, apps/api/.env.example, apps/web/.env.example, apps/admin/.env.example, apps/space/.env.example, apps/live/.env.example</files>
  <action>
    Update `render.yaml` and env examples so Render production values are discoverable without changing local defaults. In `render.yaml`, add placeholder or dashboard-entered env entries for R2, SMTP, backend origins, cookie domain, live CORS, and static-site `VITE_*` build values; do not add real secrets. Add commented Render examples for API origin, web origin, admin origin plus `/god-mode`, Space origin plus `/spaces`, live origin plus `/live`, `CORS_ALLOWED_ORIGINS`, and `COOKIE_DOMAIN`. Add R2 and SMTP variables to the API/root examples. Add `CORS_ALLOWED_ORIGINS` to `apps/live/.env.example`. Ensure web/admin/space examples all list the same `VITE_API_BASE_URL`, `VITE_WEB_BASE_URL`, `VITE_ADMIN_BASE_URL`, `VITE_ADMIN_BASE_PATH`, `VITE_SPACE_BASE_URL`, `VITE_SPACE_BASE_PATH`, `VITE_LIVE_BASE_URL`, and `VITE_LIVE_BASE_PATH`.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "AWS_S3_ENDPOINT_URL\|EMAIL_HOST\|CORS_ALLOWED_ORIGINS\|VITE_API_BASE_URL" render.yaml</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "VITE_API_BASE_URL\|VITE_ADMIN_BASE_PATH\|VITE_SPACE_BASE_PATH\|VITE_LIVE_BASE_PATH" apps/web/.env.example apps/admin/.env.example apps/space/.env.example</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "AWS_S3_ENDPOINT_URL\|EMAIL_HOST\|COOKIE_DOMAIN\|CORS_ALLOWED_ORIGINS" .env.example apps/api/.env.example apps/live/.env.example</automated>
  </verify>
  <acceptance_criteria>
    - `render.yaml` includes placeholder or dashboard-entered env vars for R2, SMTP, origin, cookie, live CORS, and Vite build values.
    - Frontend env examples list a consistent Vite origin/base-path matrix.
    - Backend/root env examples include R2, SMTP, CORS, and cookie-domain variables.
    - Live env example includes `CORS_ALLOWED_ORIGINS`.
    - Localhost defaults remain usable for local development.
  </acceptance_criteria>
  <done>Env examples reflect the Render origin and external-service contract.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: Confirm final deployed origins</name>
  <files>none</files>
  <action>Pause execution and request the final HTTPS origins or approval to use Render-generated service URLs for the first deploy.</action>
  <what-required>Choose or confirm the final HTTPS origins before live deploy: web app, admin, Space, live WebSocket, API, and optional shared cookie parent domain.</what-required>
  <why-required>The static `VITE_*` values are baked at build time, OAuth redirect URIs are dashboard-controlled, and cookies/CORS must match deployed origins. The agent cannot infer final production domains safely.</why-required>
  <verify>Human response provides final origins or explicitly approves Render-generated service URLs for first deploy.</verify>
  <done>Origin choice is captured before live deployment verification.</done>
  <resume-signal>Provide the final origins, or say "use Render service URLs for first deploy" to continue with Render-generated domains.</resume-signal>
</task>

</tasks>

<verification>
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "AWS_S3_ENDPOINT_URL" docs/render-deployment.md apps/api/.env.example .env.example`
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "EMAIL_HOST" docs/render-deployment.md apps/api/.env.example .env.example`
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "CORS_ALLOWED_ORIGINS" docs/render-deployment.md apps/api/.env.example apps/live/.env.example`
</verification>

<success_criteria>

- R2, SMTP, and origin/cookie/OAuth contracts are documented.
- Env examples expose the exact variables needed by the existing code.
- Final origin choice is captured before deploy verification starts.
  </success_criteria>

<output>
After completion, create `.planning/phases/04-render-topology-infra/04-03-r2-smtp-origin-contract-SUMMARY.md`
</output>
