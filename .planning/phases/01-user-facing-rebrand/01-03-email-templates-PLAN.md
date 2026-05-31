---
phase: 01-user-facing-rebrand
plan: 03
type: execute
wave: 2
depends_on: [01-01]
files_modified:
  - apps/api/templates/base.html
  - apps/api/templates/emails/test_email.html
  - apps/api/templates/admin/base_site.html
  - apps/api/templates/emails/auth/forgot_password.html
  - apps/api/templates/emails/auth/magic_signin.html
  - apps/api/templates/emails/user/user_deactivation.html
  - apps/api/templates/emails/user/email_updated.html
  - apps/api/templates/emails/user/user_activation.html
  - apps/api/templates/emails/exports/analytics.html
  - apps/api/templates/emails/notifications/webhook-deactivate.html
  - apps/api/templates/emails/notifications/project_addition.html
  - apps/api/templates/emails/notifications/issue-updates.html
  - apps/api/templates/emails/invitations/workspace_invitation.html
  - apps/api/templates/emails/invitations/project_invitation.html
  - apps/api/plane/license/utils/instance_value.py
  - .env.example
autonomous: false
requirements: [BRAND-10]
must_haves:
  truths:
    - "Invite, magic-link, password-reset, and notification emails read 'Bright-Byte PMP', not 'Plane'"
    - "The email logo image is the Bright-Byte logo, not the remote Plane logo URL"
    - "The default EMAIL_FROM is a Bright-Byte sender, env-overridable"
  artifacts:
    - path: "apps/api/templates/base.html"
      provides: "Shared email layout / title"
      contains: "Bright-Byte"
    - path: "apps/api/plane/license/utils/instance_value.py"
      provides: "EMAIL_FROM default value"
      contains: "EMAIL_FROM"
  key_links:
    - from: "apps/api/templates/emails/**"
      to: "apps/api/templates/base.html"
      via: "Django template extends/include"
      pattern: "extends|include"
---

<objective>
Rebrand every transactional email template (invites, magic-link, password reset, notifications, exports, user lifecycle) and the default `EMAIL_FROM` sender so emails read "Bright-Byte PMP" and carry the Bright-Byte logo instead of "Plane" and the remote `media.docs.plane.so` Plane logo. Emails are external, user-facing, and high-trust — a "Plane" leak here undermines the whole white-label.

Purpose: Invites and auth emails are the first thing a new client sees, often before the app itself. They must not say "Plane" or pull a Plane logo.
Output: Rebranded `apps/api/templates/**` HTML, updated `EMAIL_FROM` default, and a documented `EMAIL_FROM` entry in `.env.example`.

Wave/ordering note: this plan is Wave 2 and depends on Plan 01 ONLY because both append to the shared `.env.example` file (Plan 01 creates/owns it first; this plan appends `EMAIL_FROM`). All email-template content work is otherwise independent of Plan 01 and could run concurrently — the dependency is purely to serialize the single shared file.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/research/FEATURES.md
@.planning/research/PITFALLS.md

<interfaces>
<!-- Brand "plane" hit counts per template (from the repo). All are user-visible HTML, NOT AGPL source headers. -->
base.html:1, test_email.html:2, admin/base_site.html:2, auth/forgot_password.html:8, auth/magic_signin.html:7,
user/user_deactivation.html:15, user/email_updated.html:8, user/user_activation.html:16, exports/analytics.html:8,
notifications/webhook-deactivate.html:6, notifications/project_addition.html:8, notifications/issue-updates.html:14,
invitations/workspace_invitation.html:8, invitations/project_invitation.html:9.

Representative leak shapes (from magic_signin.html / workspace_invitation.html):
- <title>Your Plane login code</title> ; "Your Plane login code {{code}} is valid..."
- Remote logo: src="https://media.docs.plane.so/logo/new-logo-dark.png" alt="Plane"
- HTML comments like <!-- PLANE LOGIN CODE EMAIL --> (cosmetic; rebrand for tidiness)
- Footer text "Plane Software, Inc." (company/legal-ish line — see constraint on this)
- "{{first_name}} invited you to {{workspace_name}} on Plane"

EMAIL_FROM default: apps/api/plane/license/utils/instance_value.py L55-56:
  "key": "EMAIL_FROM", "default": os.environ.get("EMAIL_FROM", "Team Plane <team@mailer.plane.so>")
(Editing this STRING is in scope. Do NOT remove or alter the surrounding license/instance-registration machinery — that app is an anti-feature we leave intact.)
</interfaces>
</context>

<constraints>
- Display name is exactly "Bright-Byte PMP". The AI assistant (if referenced in any email) is "Byte".
- These are Django HTML templates, NOT source files with AGPL headers — they have no `SPDX`/`Copyright (c) ... Plane Software` comment header to protect. Rebrand all visible brand text freely.
- IMPORTANT — the footer line "Plane Software, Inc." is a COMPANY/legal attribution string inside email bodies (not an AGPL source-file header). Replace the user-visible brand name with "Bright-Byte PMP" where it functions as product branding, BUT surface the legal-entity footer ("Plane Software, Inc." / any address / unsubscribe-law text) as a "values to confirm" checkpoint item rather than inventing a Bright-Byte legal entity name/address. Keep `{{ ... }}` Django template variables and `{% ... %}` tags byte-identical (do not corrupt placeholders or links — Pitfall: template-injection/broken-link risk).
- The remote logo URL `https://media.docs.plane.so/logo/new-logo-dark.png` is an EXTERNAL Plane asset — replace it with a Bright-Byte logo reference (see Task 2; do not leave it pointing at Plane infra, and do not introduce a mixed-content http:// reference).
- Preserve every `{{variable}}` and `{% block %}` exactly; only edit literal brand text and the logo `src`.
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Rebrand visible brand text across all email templates</name>
  <read_first>
    - apps/api/templates/base.html (shared layout — read first to find the title/header/footer blocks)
    - apps/api/templates/emails/auth/magic_signin.html and emails/invitations/workspace_invitation.html (representative full templates)
    - The remaining 11 templates listed in files_modified (read each before editing)
  </read_first>
  <files>apps/api/templates/base.html, apps/api/templates/emails/test_email.html, apps/api/templates/admin/base_site.html, apps/api/templates/emails/auth/forgot_password.html, apps/api/templates/emails/auth/magic_signin.html, apps/api/templates/emails/user/user_deactivation.html, apps/api/templates/emails/user/email_updated.html, apps/api/templates/emails/user/user_activation.html, apps/api/templates/emails/exports/analytics.html, apps/api/templates/emails/notifications/webhook-deactivate.html, apps/api/templates/emails/notifications/project_addition.html, apps/api/templates/emails/notifications/issue-updates.html, apps/api/templates/emails/invitations/workspace_invitation.html, apps/api/templates/emails/invitations/project_invitation.html</files>
  <action>
    BRAND-10: In each template, replace every user-visible "Plane" brand string with "Bright-Byte PMP" (e.g. `<title>Your Plane login code</title>` → "Your Bright-Byte PMP login code"; "on Plane" → "on Bright-Byte PMP"; `alt="Plane"` → `alt="Bright-Byte PMP"`). Rebrand cosmetic HTML comments (e.g. `<!-- PLANE LOGIN CODE EMAIL -->`) for tidiness. Do NOT touch any `{{ ... }}` variable or `{% ... %}` tag. Do NOT edit the remote logo `src` in this task (Task 2 owns it). For the footer legal-entity line ("Plane Software, Inc." and any postal address / legal text), leave it as-is for now and record it as a checkpoint item — Task 3 confirms the correct legal/footer string.
    Note: where a string is a wordmark used as a sentence noun ("on Plane"), prefer "Bright-Byte PMP"; keep grammar natural.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && rem=$(grep -ric "plane" apps/api/templates/base.html apps/api/templates/emails/test_email.html apps/api/templates/admin/base_site.html apps/api/templates/emails/auth/forgot_password.html apps/api/templates/emails/auth/magic_signin.html apps/api/templates/emails/user/user_deactivation.html apps/api/templates/emails/user/email_updated.html apps/api/templates/emails/user/user_activation.html apps/api/templates/emails/exports/analytics.html apps/api/templates/emails/notifications/webhook-deactivate.html apps/api/templates/emails/notifications/project_addition.html apps/api/templates/emails/notifications/issue-updates.html apps/api/templates/emails/invitations/workspace_invitation.html apps/api/templates/emails/invitations/project_invitation.html | grep -viE "media\.docs\.plane\.so|Plane Software, Inc" | awk -F: '{s+=$2} END{print s}'); echo "Remaining plane hits (excluding logo URL + legal footer, which are handled in Task 2/Task 3): $rem"; [ "$rem" -eq 0 ] && echo "PASS" || echo "REVIEW: see remaining hits"</automated>
  </verify>
  <acceptance_criteria>
    - After Task 1, the ONLY remaining "plane" hits across the 14 templates are the remote logo URL (`media.docs.plane.so`, handled in Task 2) and the legal footer "Plane Software, Inc." (handled in Task 3).
    - Every `{{variable}}` and `{% tag %}` is preserved — `git diff` shows no change inside `{{...}}` or `{%...%}`.
    - No `http://` reference was introduced (no mixed content).
  </acceptance_criteria>
  <done>All email body brand text reads Bright-Byte PMP; template variables/tags intact; only the logo URL and legal footer remain (deferred to Task 2/3).</done>
</task>

<task type="auto">
  <name>Task 2: Replace the remote Plane logo in emails + rebrand the EMAIL_FROM default</name>
  <read_first>
    - apps/api/templates/base.html and the email templates referencing `media.docs.plane.so` (grep first)
    - apps/api/plane/license/utils/instance_value.py (lines around 55-56 — EMAIL_FROM default)
    - .planning/research/PITFALLS.md (Pitfall 8: EMAIL_FROM = "Team Plane <team@mailer.plane.so>" leak)
  </read_first>
  <files>apps/api/templates/base.html, apps/api/templates/emails/auth/magic_signin.html, apps/api/templates/emails/invitations/workspace_invitation.html, apps/api/templates/emails/invitations/project_invitation.html, apps/api/templates/emails/auth/forgot_password.html, apps/api/templates/emails/user/user_activation.html, apps/api/templates/emails/user/email_updated.html, apps/api/templates/emails/user/user_deactivation.html, apps/api/templates/emails/notifications/project_addition.html, apps/api/templates/emails/notifications/issue-updates.html, apps/api/templates/emails/notifications/webhook-deactivate.html, apps/api/templates/emails/exports/analytics.html, apps/api/plane/license/utils/instance_value.py</files>
  <action>
    Logo: Replace every `src="https://media.docs.plane.so/logo/new-logo-dark.png"` (and any light variant) with a Bright-Byte logo reference. Prefer a self-hosted/static asset served by the app (so emails do not depend on Plane infra and there is no external-host trust dependency); if a Bright-Byte hosted logo URL is confirmed at the Task 3 checkpoint, use that https URL. Never leave the Plane media URL and never use http://. Find all occurrences with: grep -rl "media.docs.plane.so" apps/api/templates/.
    EMAIL_FROM (BRAND-10 + Pitfall 8): in instance_value.py, change ONLY the default string in `os.environ.get("EMAIL_FROM", "Team Plane <team@mailer.plane.so>")` to a Bright-Byte sender confirmed at Task 3 (e.g. "Bright-Byte PMP <noreply@bright-byte.example>"), keeping the env-override structure intact. Do not modify any other line in this file, and do not remove/relocate the license-app machinery around it. Preserve the Python AGPL header.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && logo=$(grep -ric "media.docs.plane.so" apps/api/templates 2>/dev/null | awk -F: '{s+=$2} END{print s+0}'); from=$(grep -c "team@mailer.plane.so\|Team Plane" apps/api/plane/license/utils/instance_value.py); echo "logo URL hits: $logo (want 0); EMAIL_FROM plane hits: $from (want 0)"; [ "$logo" -eq 0 ] && [ "$from" -eq 0 ] && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -ri "media.docs.plane.so" apps/api/templates` returns 0.
    - `EMAIL_FROM` default contains no "Plane"/"mailer.plane.so"; env-override structure (`os.environ.get("EMAIL_FROM", ...)`) preserved.
    - No `http://` logo reference introduced; instance_value.py AGPL header unchanged; no license machinery removed.
  </acceptance_criteria>
  <done>Emails use the Bright-Byte logo and send from a Bright-Byte address by default; no Plane infra dependency.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <decision>Confirm the email sender, hosted email-logo URL, and the legal-entity footer string.</decision>
  <context>
    Three email values cannot be invented: (1) the default `EMAIL_FROM` sender, (2) where the email logo is served from (a self-hosted static asset vs a Bright-Byte CDN URL), and (3) the legal-entity footer currently reading "Plane Software, Inc." Note: AGPL requires preserving SOURCE-FILE copyright headers — these email-body footers are NOT source headers, so they may be changed; but we must use your real legal/footer text, not a guess. The real sender domain is also gated on the SMTP provider decision in Phase 4, so a placeholder default is acceptable for v1 (overridable via the EMAIL_FROM env var).
  </context>
  <options>
    <option id="confirm-values">
      <name>Provide the real values</name>
      <pros>Final email branding ships now.</pros>
      <cons>Requires the sender address, logo hosting choice, and legal footer text to be decided.</cons>
      <detail>Provide: EMAIL_FROM (e.g. "Bright-Byte PMP &lt;noreply@yourdomain&gt;"); email-logo choice (self-hosted asset path OR an https CDN URL); legal footer line (company name + any required address/unsubscribe text).</detail>
    </option>
    <option id="placeholders">
      <name>Approve placeholders (recommended for v1)</name>
      <pros>Unblocks the rebrand; sender is env-overridable in Render later; logo self-hosted (no external dependency).</pros>
      <cons>Footer/sender are placeholders until decided.</cons>
      <detail>EMAIL_FROM default "Bright-Byte PMP &lt;noreply@bright-byte.example&gt;" (override via EMAIL_FROM env); email logo = a self-hosted Bright-Byte static asset; footer = "Bright-Byte PMP" with the legal-entity line removed pending your legal text.</detail>
    </option>
  </options>
  <resume-signal>Reply "placeholders" or paste the EMAIL_FROM, logo choice, and legal footer text.</resume-signal>
</task>

<task type="auto">
  <name>Task 4: Document EMAIL_FROM in .env.example</name>
  <read_first>
    - .env.example (root) — Plan 01 created/owns this file and added the VITE_* brand vars; read it first and APPEND, do not overwrite
    - apps/api/plane/license/utils/instance_value.py (to mirror the exact key name)
  </read_first>
  <files>.env.example</files>
  <action>
    Add a documented `EMAIL_FROM` entry to `.env.example` with the confirmed sender as the example and a one-line comment that it sets the From address for invites/magic-link/notification emails and overrides the in-app default. Plan 01 already created `.env.example` with the VITE_* vars — append the EMAIL_FROM line, keep the existing entries intact, and do not duplicate if already present.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -q "EMAIL_FROM" .env.example && grep -qE "VITE_WEBSITE_URL|VITE_SUPPORT_EMAIL" .env.example && echo "PASS: EMAIL_FROM documented and Plan 01 vars preserved" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `.env.example` documents `EMAIL_FROM` with the confirmed example sender.
    - The `VITE_WEBSITE_URL` / `VITE_SUPPORT_EMAIL` entries added by Plan 01 are still present (this plan appended, did not overwrite).
  </acceptance_criteria>
  <done>Deployers know how to set the production From address without a code change; Plan 01's env entries are intact.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| Django template vars → rendered email HTML | `{{first_name}}`, `{{workspace_name}}`, `{{code}}` are interpolated server-side; corrupting or unescaping them risks template-injection or broken/incorrect emails. |
| email logo src → recipient mail client | The logo URL is fetched by the recipient's mail client; an external/insecure URL is a privacy + availability dependency. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-03-01 | Tampering / Injection | email template `{{ }}` / `{% %}` placeholders | mitigate | Edit only literal brand text and the logo `src`; never alter Django variables/tags or their autoescaping. Acceptance criteria assert no diff inside `{{...}}`/`{%...%}`, preventing template-injection or broken-link regressions. |
| T-03-02 | Information Disclosure | email logo served from Plane infra | mitigate | Replace `media.docs.plane.so` with a self-hosted/confirmed-https Bright-Byte asset, removing the dependency on (and silent beacon to) Plane infrastructure. No http:// (no mixed content / downgrade). |
| T-03-03 | Spoofing | EMAIL_FROM default | mitigate | Default sender is env-overridable; the real authenticated sender is set in Phase 4 with the SMTP provider (SPF/DKIM there). v1 placeholder cannot send as Plane. |
| T-03-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages (template + one string edit). No supply-chain surface. |
</threat_model>

<verification>
- `grep -ri "plane" apps/api/templates` returns 0 brand hits after Task 1-3 (legal footer resolved at checkpoint; logo URL removed in Task 2). Note these HTML templates have no AGPL headers to exclude.
- `EMAIL_FROM` default and `.env.example` carry the Bright-Byte sender.
- Django templates still render: confirm no `{{ }}`/`{% %}` placeholder was altered via `git diff`.
- instance_value.py: Python AGPL header unchanged; only the default string changed.
- `.env.example`: Plan 01's VITE_* entries preserved alongside the new EMAIL_FROM.
</verification>

<success_criteria>
- Every email (invite, magic-link, password-reset, notification) and `EMAIL_FROM` read Bright-Byte, not Plane — ROADMAP Phase 1 success criterion 3 (email portion).
- Email logo no longer points at Plane infrastructure.
- Template variables/tags preserved; no injection or broken-link regression.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-03-SUMMARY.md` when done.
</output>
