---
phase: 01-user-facing-rebrand
plan: 06
subsystem: brand-leak-sweep
tags: [rebrand, verification, audit, agpl, brand-leak]
dependency_graph:
  requires: [01-01, 01-02, 01-03, 01-04, 01-05]
  provides: [BRAND-11-sweep, phase-01-verification]
  affects: [phase-01-closure]
tech_stack:
  added: []
  patterns: [case-insensitive-brand-sweep, keep-fixed-outofphase-triage]
key_files:
  created:
    - .planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md
  modified:
    - apps/web/ce/components/onboarding/tour/root.tsx
    - apps/web/ce/components/onboarding/tour/sidebar.tsx
    - apps/admin/app/(all)/(home)/sign-in-form.tsx
    - apps/admin/app/(all)/(home)/page.tsx
    - apps/admin/app/(all)/(dashboard)/sidebar-help-section.tsx
    - apps/admin/app/(all)/(dashboard)/email/page.tsx
    - apps/web/ce/components/instance/maintenance-message.tsx
    - apps/web/core/components/integration/single-integration-card.tsx
    - apps/web/core/components/common/activity/user.tsx
    - apps/web/core/components/common/activity/helper.tsx
    - apps/web/core/components/profile/activity/activity-list.tsx
    - apps/web/core/components/issues/issue-detail/issue-activity/activity/actions/archived-at.tsx
    - apps/web/ce/components/issues/issue-details/issue-creator.tsx
    - apps/web/core/components/inbox/sidebar/inbox-list-item.tsx
    - apps/web/core/components/issues/peek-overview/properties.tsx
    - apps/space/components/common/powered-by.tsx
    - apps/space/components/account/terms-and-conditions.tsx
    - apps/web/core/components/account/terms-and-conditions.tsx
decisions:
  - "[01-06]: 71 'plane' hits triaged — 25 KEEP, 24 FIXED, 22 OUT-OF-PHASE; zero unresolved user-facing brand leaks"
  - "[01-06]: 24 brand leaks Plans 01-01..05 missed were fixed here (onboarding tour, admin UI, activity-feed system-actor name, integration cards, space powered-by, T&C legal URLs, maintenance message)"
  - "[01-06]: OUT-OF-PHASE classified and deferred — Phase 5 (16 support/docs/forum/changelog URLs + 3 telemetry + 2 API dev docs), Phase 3 (1 plane.so/contact upsell). These are NOT user-visible brand wordmarks."
  - "[01-06]: AGPL integrity verified — LICENSE.txt/COPYRIGHT.txt and all source-file copyright headers untouched across the entire phase (0 header diff lines)"
  - "[01-06]: issue-updates.html retains 12 functional utility-icon URLs on plane-marketing.s3 — classified non-brand functional icons (infra-dependency cleanup is out of Phase-1 scope)"
  - "[01-06]: Human-verify gate APPROVED by user 2026-06-03 with documented v1 stubs (deferred binary brand assets + env-overridable placeholders) accepted"
metrics:
  duration_minutes: 28
  completed_date: "2026-06-03"
  tasks_completed: 4
  files_modified: 18
---

# Phase 01 Plan 06: Brand-Leak Sweep + Verification Summary

Final BRAND-11 gate for Phase 1: a whole-tree case-insensitive `plane` sweep,
KEEP/FIXED/OUT-OF-PHASE triage, closure of any user-facing leak Plans 01-01..05
missed, and AGPL-integrity verification. Ends the phase at the human-verify gate.

## Tasks Completed

| Task | Name                                      | Commit     | Result                                                                                     |
| ---- | ----------------------------------------- | ---------- | ------------------------------------------------------------------------------------------ |
| 1    | Case-insensitive sweep + triage every hit | c6f200b096 | 01-06-BRAND-SWEEP.md — 71 hits classified (25 KEEP / 22 OUT-OF-PHASE / 24 to-fix)          |
| 2    | Close genuine user-facing brand leaks     | 45815cb97d | 24 leaks fixed across 18 files; pre-existing `prefer-tag-over-role` warning fixed properly |
| 3    | Confirm AGPL integrity across the phase   | 7f41a1761d | AGPL audit appended — PASS                                                                 |
| 4    | Human-verify checkpoint                   | (gate)     | APPROVED by user 2026-06-03                                                                |

## Changes Made

### 24 brand leaks fixed (Task 2)

- Onboarding tour (web): "Welcome to Plane", "glad you tried out Plane", "building block of the Plane", "Get more out of Plane" → Bright-Byte PMP
- Admin: sign-in heading + meta, help-section tooltip/button, email page description → Bright-Byte PMP
- Maintenance message (web): copy + `support@plane.so` → `support@bright-byte.example`
- Integration cards: "your Plane workspace" (GitHub + Slack)
- Activity feed + intake system-actor display name "Plane" → "Bright-Byte PMP" (user.tsx, helper.tsx, activity-list.tsx, archived-at.tsx, issue-creator.tsx, inbox-list-item.tsx, peek-overview/properties.tsx)
- Space "powered by Plane Publish" → Bright-Byte PMP
- Terms & Conditions legal URLs (web + space): `plane.so/legals/...` → `bright-byte.example/legals/...`

## Verification Results

- AGPL: `LICENSE.txt`/`COPYRIGHT.txt` unchanged; 0 source-header diff lines across the whole phase. PASS.
- User-visible brand grep clean (excluding KEEP/OUT-OF-PHASE): 0 unresolved leaks. PASS.
- i18n rendered values: 0 brand "Plane" tokens across all 19 locales.

## Deviations from Plan

- Fixed a pre-existing `prefer-tag-over-role` oxlint warning in code (did not disable the rule).
- Final SUMMARY + ROADMAP/STATE tracking were written by the orchestrator after the user approved the human-verify gate (executor stopped at the gate by design).

## Out-of-Phase (deferred, classified KEEP-for-now)

- Phase 5: 16 support/docs/forum/changelog URLs, 3 telemetry endpoint/consent items, 2 API developer-docs links.
- Phase 3: 1 `plane.so/contact` upsell link in admin/ai/form.tsx.
- 12 functional utility-icon URLs on `plane-marketing.s3` in issue-updates.html (non-brand functional icons).

## Known Stubs (accepted for v1 at the approved gate)

- Binary brand assets deferred (favicons, app/PWA icons, OG image, spinner GIFs, logo PNGs, email logo image) — placeholder SVG marks + code wiring shipped; real art is a drop-in.
- Env-overridable placeholders: `bright-byte.example`, `support@bright-byte.example`, `@brightbyte`, `noreply@bright-byte.example` — finalized in Phase 4/Render.
- Real legal-entity footer text is a value to confirm.

## Self-Check: PASSED
