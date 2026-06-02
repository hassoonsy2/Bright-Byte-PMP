---
phase: 01-user-facing-rebrand
plan: 03
subsystem: email-templates
tags: [rebrand, email, transactional, brand]
dependency_graph:
  requires: [01-01]
  provides: [BRAND-10-email]
  affects: [email-delivery, client-onboarding]
tech_stack:
  added: []
  patterns: [django-template-rebrand]
key_files:
  created: []
  modified:
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
decisions:
  - "[01-03]: Email logo uses https://bright-byte.example/static/emails/bright-byte-logo.png placeholder; binary image drop-in deferred to Plan 01-02"
  - "[01-03]: Legal-entity footer replaced with 'Bright-Byte PMP' placeholder; real legal entity name/address is a value to confirm"
  - "[01-03]: Plane community blurbs ('Despite our popularity') replaced with neutral Bright-Byte PMP contact text"
  - "[01-03]: Plane social link hrefs (planepowers, makeplane, plane.so) replaced with bright-byte.example placeholder"
  - "[01-03]: EMAIL_FROM default is 'Bright-Byte PMP <noreply@bright-byte.example>' (env-overridable); real authenticated sender configured in Phase 4 with SMTP provider"
metrics:
  duration_minutes: 45
  completed_date: "2026-06-02"
  tasks_completed: 3
  files_modified: 16
---

# Phase 01 Plan 03: Email Templates Rebrand Summary

Rebranded all 14 transactional email templates to read "Bright-Byte PMP" instead of "Plane", replaced the remote Plane logo with a self-hosted placeholder URL, updated the EMAIL_FROM default sender, and documented it in .env.example.

## Tasks Completed

| Task                  | Description                                                      | Commit     |
| --------------------- | ---------------------------------------------------------------- | ---------- |
| Task 1                | Rebrand visible brand text across all email templates            | e7e347f9ea |
| Task 2                | Replace remote Plane logo + rebrand EMAIL_FROM default           | e7e347f9ea |
| Task 3 (pre-approved) | Checkpoint: confirm sender/logo/footer — approved "placeholders" | n/a        |
| Task 4                | Document EMAIL_FROM in .env.example                              | 1af8551b54 |

## Changes Made

### Brand Text Changes (Task 1)

- `<title>` elements rebranded: "Plane login code" → "Bright-Byte PMP login code", "Reset your Plane password" → "Reset your Bright-Byte PMP password", etc.
- HTML comments rebranded (e.g. `<!-- PLANE LOGIN CODE EMAIL -->` → `<!-- BRIGHT-BYTE PMP LOGIN CODE EMAIL -->`)
- Headings and body copy updated: "on Plane" → "on Bright-Byte PMP", "Join {{workspace_name}} on Plane" → "on Bright-Byte PMP"
- "Plane Software, Inc." footer replaced with "Bright-Byte PMP" (email body footers only — AGPL source-file headers untouched)
- "Despite our popularity" Plane community blurb removed from user_deactivation, user_activation, webhook-deactivate — replaced with "If you have any questions or need help, please reach out to the Bright-Byte PMP team."
- Plane social link hrefs (x.com/planepowers, linkedin/planepowers, github.com/makeplane, plane.so) replaced with https://bright-byte.example placeholder in all 5 affected templates
- "Note: Plane is still in its early days..." blurb in project_invitation.html replaced with neutral contact text

### Logo Replacement (Task 2)

- All occurrences of `https://media.docs.plane.so/logo/new-logo-dark.png` (5 files) replaced with `https://bright-byte.example/static/emails/bright-byte-logo.png`
- All occurrences of `https://media.docs.plane.so/logo/new-logo-white.png` (6 files) replaced with the same placeholder URL
- No `http://` (no mixed content) introduced; no Plane infra dependency remains for the primary logo

### EMAIL_FROM (Task 2)

- `apps/api/plane/license/utils/instance_value.py` L56: changed default from `"Team Plane <team@mailer.plane.so>"` to `"Bright-Byte PMP <noreply@bright-byte.example>"`
- `os.environ.get("EMAIL_FROM", ...)` structure preserved; Python AGPL file header untouched

### .env.example (Task 4)

- Appended `EMAIL_FROM="Bright-Byte PMP <noreply@bright-byte.example>"` with one-line comment
- Plan 01 entries `VITE_WEBSITE_URL` and `VITE_SUPPORT_EMAIL` preserved

## Verification Results

| Check                                               | Result                                                |
| --------------------------------------------------- | ----------------------------------------------------- |
| `grep -ri "media.docs.plane.so" apps/api/templates` | 0 hits — PASS                                         |
| `EMAIL_FROM` contains no "plane"/"mailer.plane.so"  | PASS                                                  |
| Django `{{ }}` / `{% %}` variables unaltered        | PASS (git diff shows no changes inside template tags) |
| `http://` introduced                                | PASS (none)                                           |
| AGPL source-file headers untouched                  | PASS                                                  |
| `.env.example` Plan 01 vars preserved               | PASS                                                  |
| `.env.example` EMAIL_FROM documented                | PASS                                                  |

## Deviations from Plan

### Auto-fixed Issues

None — plan executed as written, with the Task 3 checkpoint pre-approved as "placeholders".

### Discovered Out-of-Scope Item (deferred)

**[Deferred] `issue-updates.html`: 12 `plane-marketing.s3.ap-south-1.amazonaws.com/plane-assets/` utility icon URLs**

- **What:** The issue notification email uses 12 small utility icons (state, priority, assignee, etc.) hosted at `plane-marketing.s3.ap-south-1.amazonaws.com/plane-assets/emails/*.png`
- **Classification:** These are functional UI icons (not brand images/wordmarks). They contain "plane" in the URL but display no "Plane" text to users.
- **Decision:** Deferred — replacing these requires binary image uploads to self-hosted storage, which is outside the scope of a template text rebrand. The `grep -ric "plane"` count for `issue-updates.html` shows 13 total hits, 12 from these icon URLs, 1 from the replaced logo.
- **Impact:** `issue-updates.html` retains 12 `plane-marketing.s3` URL hits. These are an external infrastructure dependency on Plane's S3 bucket (not brand exposure to end users as text).
- **Logged to:** `deferred-items.md` for future phase

**[Non-brand] `project_invitation.html`: "Planet Earth 🌍"**

- Line 194 contains "Planet Earth" which matches case-insensitive "plane" grep but is not a Plane brand reference. Left unchanged.

## Values to Confirm

| Value                       | Current Placeholder                                              | Notes                                                                                                                                                                                   |
| --------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Email logo binary           | `https://bright-byte.example/static/emails/bright-byte-logo.png` | Wired and ready; actual PNG binary is the binary-asset drop-in from Plan 01-02. The URL path and static serving setup needs to be confirmed when the binary is deployed.                |
| Legal entity footer         | "Bright-Byte PMP"                                                | Replaced Plane Software Inc. in email bodies. The actual legal entity name and any required address/unsubscribe-law text for the jurisdiction must be confirmed before serving clients. |
| Authenticated sender domain | `noreply@bright-byte.example`                                    | Placeholder until Phase 4 SMTP provider setup (SPF/DKIM authentication for real sender domain).                                                                                         |

## Known Stubs

| File                | Stub                                                                        | Reason                                                                                                                                                                                             |
| ------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| All email templates | Logo `src="https://bright-byte.example/static/emails/bright-byte-logo.png"` | Placeholder URL — actual binary image `.png` is the deferred asset from Plan 01-02. Emails will show a broken image icon until the binary is deployed and the URL updated to the real hosted path. |

## Self-Check: PASSED

- `apps/api/plane/license/utils/instance_value.py` exists: FOUND
- `.env.example` exists with EMAIL_FROM: FOUND
- All 14 template files exist and modified: FOUND
- Commits e7e347f9ea and 1af8551b54 exist: FOUND
