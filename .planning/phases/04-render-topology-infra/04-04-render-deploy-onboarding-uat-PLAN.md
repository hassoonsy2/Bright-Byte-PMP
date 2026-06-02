---
phase: 04-render-topology-infra
plan: 04
type: execute
wave: 3
depends_on: ["04-01", "04-02", "04-03"]
files_modified:
  - .planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md
  - docs/render-deployment.md
autonomous: false
requirements: [DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05, DEPLOY-06, DEPLOY-07]
user_setup:
  - service: render
    why: "Blueprint sync, paid resource creation, service domains, and deploy logs require Render account/dashboard access."
    env_vars:
      - name: DATABASE_URL
        source: "Render managed Postgres internal connection string"
      - name: REDIS_URL
        source: "Render Key Value internal Redis URL"
      - name: CELERY_BROKER_URL
        source: "Render Key Value internal Redis URL"
    dashboard_config:
      - task: "Create or sync blueprint from render.yaml"
        location: "Render dashboard > Blueprints"
        details: "Confirm API, worker, beat, live, space, web, admin, Postgres, and Key Value are created from the repo blueprint."
      - task: "Confirm Key Value eviction policy"
        location: "Render dashboard > Key Value > Settings"
        details: "Use a paid plan and noeviction policy before worker verification."
  - service: live-client-test
    why: "End-to-end onboarding requires a real browser session, real email recipient, and deployed object storage."
    dashboard_config:
      - task: "Prepare a test recipient inbox"
        location: "Email inbox controlled by the operator"
        details: "Use this inbox for invite or magic-link delivery verification."
must_haves:
  truths:
    - "Render deploy evidence proves all services are green and exactly one beat process is running."
    - "A live client can sign in, create a workspace/project, upload and download an attachment through R2, and receive an email."
    - "Workers process at least one real job and live collaboration connects through the deployed live service."
  artifacts:
    - path: ".planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md"
      provides: "Recorded live deployment/UAT evidence for DEPLOY-01 through DEPLOY-07"
      contains: "Client onboarding"
    - path: "docs/render-deployment.md"
      provides: "Operator runbook updated with any live deployment decisions"
      contains: "Verification"
  key_links:
    - from: "render.yaml"
      to: ".planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md"
      via: "blueprint service evidence"
      pattern: "bright-byte-api"
    - from: "Cloudflare R2"
      to: ".planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md"
      via: "attachment upload/download evidence"
      pattern: "presigned PUT/GET"
    - from: "SMTP provider"
      to: ".planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md"
      via: "email delivery evidence"
      pattern: "SMTP"
---

<objective>
Deploy the Render topology and record live onboarding verification for a shared Bright-Byte PMP instance.

Purpose: Phase 4 is only complete when the blueprint and external services work together in production-like conditions, not merely when config files exist.
Output: A deployment checklist with concrete evidence for Render services, R2, SMTP, Celery worker/beat, origin/cookie behavior, live collaboration, and client onboarding.
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
@.planning/phases/04-render-topology-infra/04-PATTERNS.md
@render.yaml
@scripts/verify-render-blueprint.mjs
@docs/render-deployment.md
@apps/api/db/management/commands/test_email.py
@apps/api/plane/settings/storage.py
@apps/live/src/env.ts
</context>

<constraints>
- Do not mark Phase 4 complete from local checks alone. Live Render, R2, SMTP, worker/beat, and browser checks are required.
- Do not store real secrets in the checklist or docs. Record service names, URLs, timestamps, masked identifiers, and outcomes only.
- Exactly one beat scheduler may run. Additional beat instances are a Phase 4 failure.
- Do not onboard real client data until Phase 5 security and AGPL gates are complete. Use a test client/workspace for Phase 4 UAT.
- If Phase 4 discovers a Phase 5 hardening issue, record it as a blocker or deferred Phase 5 item instead of expanding this plan's scope.
</constraints>

<threat_model>
<threat id="T-04-10" severity="high" requirement="DEPLOY-01,DEPLOY-02">
<risk>Render shows green deploys but one required service is missing, failed, or wired to the wrong resource.</risk>
<mitigation>Checklist records each service, resource, region, plan, deploy status, health URL, and the managed connection source used by API/worker/beat/live.</mitigation>
</threat>
<threat id="T-04-11" severity="high" requirement="DEPLOY-03,DEPLOY-04">
<risk>R2 or SMTP only works from backend shell but fails for real browser uploads or real email recipients.</risk>
<mitigation>UAT requires browser attachment upload/download and inbox-confirmed email delivery, not only config inspection.</mitigation>
</threat>
<threat id="T-04-12" severity="high" requirement="DEPLOY-06,DEPLOY-07">
<risk>Authentication works on one origin but cookies, CORS, OAuth redirects, or live WebSocket auth fail across the multi-service topology.</risk>
<mitigation>Run browser sign-in plus API calls, admin route, Space route, live editor connection, and client onboarding flow from the deployed origins.</mitigation>
</threat>
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Create deployment evidence checklist</name>
  <read_first>
    - .planning/phases/04-render-topology-infra/04-VALIDATION.md
    - docs/render-deployment.md
    - render.yaml
  </read_first>
  <files>.planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md</files>
  <action>
    Create `.planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md` with sections for blueprint sync, managed resources, env matrix, R2 presigned PUT/GET, SMTP delivery, Celery worker/beat, origin/cookie/OAuth, live WebSocket, and client onboarding. Include fields for timestamp, service URL, status, evidence link or log excerpt summary, and operator initials. Include explicit pass/fail checkboxes for every DEPLOY-01 through DEPLOY-07 success criterion.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "DEPLOY-01\|DEPLOY-02\|DEPLOY-03\|DEPLOY-04\|DEPLOY-05\|DEPLOY-06\|DEPLOY-07\|Client onboarding" .planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md</automated>
  </verify>
  <acceptance_criteria>
    - Checklist exists in the Phase 4 directory.
    - Checklist has one evidence section for every Phase 4 requirement.
    - Checklist tells operators not to paste real secrets.
  </acceptance_criteria>
  <done>Live deployment evidence has a structured place to be recorded.</done>
</task>

<task type="auto">
  <name>Task 2: Run local pre-deploy gates</name>
  <read_first>
    - scripts/verify-render-blueprint.mjs
    - render.yaml
    - apps/api/plane/tests/unit/settings/test_celery_broker.py
    - docs/render-deployment.md
  </read_first>
  <files>.planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md, docs/render-deployment.md</files>
  <action>
    Run the offline blueprint verifier and targeted Celery broker unit test. Record the command names and outcomes in the checklist. If either fails, fix the underlying source from earlier plans before continuing. Update `docs/render-deployment.md` only if the local gates reveal a missing operator instruction.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && node scripts/verify-render-blueprint.mjs</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP/apps/api && pytest plane/tests/unit/settings/test_celery_broker.py -m unit</automated>
  </verify>
  <acceptance_criteria>
    - Offline blueprint verifier exits 0.
    - Targeted Celery broker settings test exits 0.
    - Checklist records local pre-deploy gate outcomes.
  </acceptance_criteria>
  <done>Local source gates are green before any Render dashboard deploy.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <name>Task 3: Sync Render blueprint and external dashboards</name>
  <files>none</files>
  <action>Pause execution while the operator syncs Render and configures required external dashboards with real secrets and domains.</action>
  <what-required>Sync `render.yaml` in Render, provision paid Postgres and paid Key Value, set all required env vars, configure R2, configure SMTP, and attach final custom domains or approve Render-generated service URLs for first deploy.</what-required>
  <why-required>This requires authenticated access to Render, Cloudflare, DNS, SMTP, and optionally OAuth provider dashboards. The agent must not invent or store secrets.</why-required>
  <verify>Human response provides deployed service URLs, resource names, and non-secret configuration notes or identifies the failed dashboard step.</verify>
  <done>Render and external services are configured enough for live browser verification to begin, or a blocking dashboard failure is documented.</done>
  <resume-signal>Return the deployed service URLs, resource names, and any non-secret configuration notes, or say which dashboard step failed.</resume-signal>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Task 4: Verify deployed onboarding flow in browser</name>
  <files>none</files>
  <action>Pause execution for browser-based live UAT across sign-in, project creation, R2 attachment flow, SMTP delivery, admin, Space, live WebSocket, worker, and beat.</action>
  <what-built>Live Bright-Byte PMP shared instance deployed from `render.yaml` with R2, SMTP, Redis broker, and multi-origin frontend settings.</what-built>
  <how-to-verify>In a browser, sign in to the deployed web app, create a test workspace or client, create a project, upload and download an attachment, confirm an email reaches the test inbox, open admin under `/god-mode`, open Space under `/spaces`, and open a page/editor that connects to the live service under `/live`. Confirm Render shows one beat service and worker logs show at least one processed job.</how-to-verify>
  <verify>Human response approves the flow with URLs/timestamps and masked evidence, or lists the failing live step.</verify>
  <done>Live UAT is approved or the failing deployed behavior is documented for remediation.</done>
  <resume-signal>Type "approved" with URLs/timestamps and masked evidence, or describe the failing step.</resume-signal>
</task>

<task type="auto">
  <name>Task 5: Record final deployment findings</name>
  <read_first>
    - .planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md
    - docs/render-deployment.md
    - .planning/phases/04-render-topology-infra/04-VALIDATION.md
  </read_first>
  <files>.planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md, docs/render-deployment.md</files>
  <action>
    After human verification, update the checklist with non-secret evidence: dates, deployed origins, service/resource names, pass/fail status, and any blockers. If the deploy exposed a reusable instruction, update `docs/render-deployment.md`. Do not paste secret values, bearer tokens, cookie values, or private inbox contents.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -n "approved\|blocked\|pass\|fail\|Client onboarding" .planning/phases/04-render-topology-infra/04-DEPLOYMENT-CHECKLIST.md</automated>
  </verify>
  <acceptance_criteria>
    - Checklist records pass/fail evidence for every Phase 4 requirement.
    - Any blocked item has an owner and next action.
    - No real secrets are present in the checklist or docs.
  </acceptance_criteria>
  <done>Phase 4 deploy/UAT evidence is recorded without leaking credentials.</done>
</task>

</tasks>

<verification>
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP && node scripts/verify-render-blueprint.mjs`
- [ ] `cd /Users/Hussi/Desktop/Bright-Byte-PMP/apps/api && pytest plane/tests/unit/settings/test_celery_broker.py -m unit`
- [ ] Render dashboard shows all services/resources green.
- [ ] Browser UAT proves sign-in, project creation, attachment upload/download, email delivery, and live connection.
</verification>

<success_criteria>

- Render blueprint deploy is live and evidence-backed.
- Paid Postgres and paid Key Value are wired.
- R2 presigned PUT/GET and SMTP delivery are verified.
- Celery worker processes jobs and exactly one beat scheduler runs.
- A test client can complete end-to-end onboarding on the shared instance.
  </success_criteria>

<output>
After completion, create `.planning/phases/04-render-topology-infra/04-04-render-deploy-onboarding-uat-SUMMARY.md`
</output>
