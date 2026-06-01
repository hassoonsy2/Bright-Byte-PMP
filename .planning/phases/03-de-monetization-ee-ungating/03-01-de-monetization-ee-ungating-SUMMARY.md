---
phase: 03-de-monetization-ee-ungating
plan: 01
subsystem: ui
tags: [billing, license, upsell, react-router, i18n]

requires:
  - phase: 02-atomic-package-scope-rename
    provides: Bright-Byte package scope and baseline branding used by Phase 3 source updates
provides:
  - Billing/Plans settings route, nav entries, and members-page billing actions removed
  - Paid-plan modal, license UI, plan/pricing constants, and billing exports removed
  - Absent EE upsell stubs removed for workspace active cycles, bulk operations, and issue embeds
  - Paid-plan locale copy neutralized across locale bundles
affects: [phase-4, phase-5, billing, workspace-settings, i18n]

tech-stack:
  added: []
  patterns: [delete-absent-ee-stubs, neutralize-edition-badge, source-grep-validation]

key-files:
  created:
    - .planning/phases/03-de-monetization-ee-ungating/03-01-de-monetization-ee-ungating-SUMMARY.md
  modified:
    - apps/web/app/routes/core.ts
    - apps/web/ce/components/workspace/edition-badge.tsx
    - apps/web/core/components/workspace/sidebar/workspace-menu.tsx
    - apps/web/core/components/workspace/sidebar/help-section/root.tsx
    - apps/web/core/services/issue/issue.service.ts
    - packages/constants/src/endpoints.ts
    - packages/constants/src/event-tracker/core.ts
    - packages/i18n/src/locales/*/*.json

key-decisions:
  - "Absent-code EE stubs were removed rather than enabled because complete local backend/UI support was not proven."
  - "Workspace edition badge is passive version-only UI with no paid-plan modal trigger."
  - "Bulk operation API calls now fail locally as unavailable instead of calling a removed cloud/EE endpoint."
  - "Sales/help monetization copy was neutralized across locale bundles, not just English."

patterns-established:
  - "Use targeted source greps as the acceptance gate for monetization removal."
  - "Preserve CE-present project-management features while deleting route-level absent stubs."

requirements-completed: [BILL-01, BILL-02, BILL-03, BILL-04, BILL-05, BILL-06]

duration: 1h53m
completed: 2026-06-01
---

# Phase 3: De-Monetization EE Ungating Summary

**Billing, license, paid-plan, and absent EE upsell surfaces were removed while preserving CE project-management paths.**

## Performance

- **Duration:** 1h53m
- **Started:** 2026-06-01T08:43:05Z
- **Completed:** 2026-06-01T10:36:27Z
- **Tasks:** 9
- **Files modified:** 222

## Accomplishments

- Removed the workspace Billing/Plans settings route, settings tab, sidebar icon mapping, and members-page billing action.
- Replaced the clickable edition badge and paid-plan modal with a passive version-only badge.
- Deleted license modal/card UI, billing comparison UI, plan/pricing constants, payment/subscription types, and related package exports.
- Removed absent EE upsell entry points for workspace active cycles, bulk operations, issue embeds, upgrade badges, and Pro icons.
- Neutralized paid-plan locale copy across all locale bundles and replaced the live sidebar sales link with configured support email.
- Kept project-level active cycle functionality, notification subscriptions, reserved workspace slugs, AGPL/license files, and edition aliases intact.

## Task Commits

1. **Remove billing settings entry points** - `0ac19f83ca`
2. **Remove paid-plan modal and billing data** - `adda0e600e`
3. **Remove workspace active cycles upsell** - `e25e20fcd3`
4. **Remove remaining upgrade stubs** - `04f896ad27`
5. **Neutralize paid-plan locale copy** - `2dc4bc08d9`
6. **Replace sales help link with support** - `19316fc008`

## Verification

- `pnpm build` passed.
- `pnpm check:types` passed.
- `pnpm check:lint` passed with existing warning budgets and no errors.
- Residual source greps are clean for billing route/nav, license modal, paid-plan constants/types, pricing links, Plane upgrade URLs, `UpgradeBadge`, sales help copy, and removed EE stubs.
- `LICENSE.txt` and `COPYRIGHT.txt` have no diff.

## Deviations from Plan

### Auto-fixed Issues

**1. Billing tree deletion was pulled into Task 2**

- **Found during:** Billing route/nav removal
- **Issue:** Residual gates still found CE billing root/action files after route consumers were removed.
- **Fix:** Deleted the now-unreachable CE billing root/action/index files with the route cleanup.
- **Verification:** Billing route/nav residual grep returned no matches; typecheck passed.
- **Committed in:** `0ac19f83ca`

**2. Billing data, event tracker, and package exports were coupled**

- **Found during:** Paid-plan modal and billing data removal
- **Issue:** Deleting payment/subscription types required removing the remaining tracker enum references and package exports in the same slice.
- **Fix:** Removed billing tracker constants, plan data, payment/subscription files, and export barrels together.
- **Verification:** Payment/type residual grep returned no matches; typecheck passed.
- **Committed in:** `adda0e600e`

**3. Commit hooks surfaced lint in touched files**

- **Found during:** Workspace active-cycles and upgrade-stub commits
- **Issue:** Existing lint rules rejected no-shadow and redundant ternary patterns in touched files.
- **Fix:** Renamed local variables in the sidebar item and simplified the list-view boolean expression.
- **Verification:** Commit hooks and full lint pass completed.
- **Committed in:** `e25e20fcd3`, `04f896ad27`

**4. Bulk operation service now fails locally**

- **Found during:** Bulk operation stub removal
- **Issue:** UI consumers could still call `/bulk-operation-issues/` after removing the upgrade banner/root.
- **Fix:** Kept selection disabled and changed `IssueService.bulkOperations` to throw `Bulk operations are not available in this edition.`
- **Verification:** `bulk-operation-issues` residual grep returned no matches; typecheck passed.
- **Committed in:** `04f896ad27`

**5. Locale and help-menu paid-plan copy expanded the cleanup scope**

- **Found during:** Final residual greps and Plane-domain scan
- **Issue:** Dormant locale bundles and a live help menu still contained sales/paid-plan copy.
- **Fix:** Neutralized paid-plan strings across locale bundles, removed the unused `contact_sales` key, updated Storybook example copy, and replaced `sales@plane.so` with configured `SUPPORT_EMAIL`.
- **Verification:** Sales/paid-plan residual greps returned no matches; i18n generated 3836 keys; build/typecheck/lint passed.
- **Committed in:** `2dc4bc08d9`, `19316fc008`

---

**Total deviations:** 5 auto-fixed
**Impact on plan:** All changes stayed inside Phase 3 billing, license, and upsell removal. No unrelated schema, license, or issue-notification surfaces were changed.

## Issues Encountered

- `pnpm build` and `pnpm check:types` initially failed inside the sandbox because `tsx` could not open its IPC pipe under `/tmp`. Both passed when rerun with approved escalation.
- The repo reports an existing Node engine warning because this shell uses Node `v22.15.0` while the repo asks for `>=22.18.0`.
- Browser smoke was not run; validation relied on source residual gates, production build, typecheck, and lint as planned for this frontend source slice.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 4 can proceed with the app free of reachable billing, license, paid-plan, and sales-upgrade surfaces. Remaining Plane-domain links in the broad scan are docs, support/status, legal, metadata, forum, changelog, or deployment defaults and should be handled only by later brand/deploy cleanup phases.

---

_Phase: 03-de-monetization-ee-ungating_
_Completed: 2026-06-01_
