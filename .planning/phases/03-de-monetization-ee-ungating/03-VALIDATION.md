---
phase: 03
slug: de-monetization-ee-ungating
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-01
---

# Phase 03 - Validation Strategy

Per-phase validation contract for de-monetization and EE-stub cleanup.

## Test Infrastructure

| Property           | Value                                                      |
| ------------------ | ---------------------------------------------------------- |
| Framework          | Turborepo build/type/lint for source verification          |
| Config file        | `turbo.json`, `.oxlintrc.json`, TypeScript package configs |
| Quick run command  | `pnpm check:types`                                         |
| Full suite command | `pnpm build && pnpm check:types && pnpm check:lint`        |
| Estimated runtime  | Repository-dependent; expect several minutes               |

## Sampling Rate

- After route/nav and badge changes: run source residual grep gates for billing route, license modal, and upgrade triggers.
- After deleting billing/license/plan constants: run `pnpm check:types`.
- After each absent-stub cleanup group: run targeted source greps for that stub and confirm no sidebar/route/button remains.
- Before final commit: run the full suite command and all residual grep gates.
- Max feedback latency: one task; no code task may proceed after a failed residual gate without either fixing it or documenting why the hit is out of Phase 3 scope.

## Per-Task Verification Map

| Task ID  | Plan | Wave | Requirement      | Threat Ref | Secure Behavior                                                                 | Test Type     | Automated Command                                             | File Exists                                                                                                            | Status              |
| -------- | ---- | ---- | ---------------- | ---------- | ------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------------------------------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------- | --- | ------ |
| 03-01-01 | 01   | 1    | BILL-01          | T-03-01    | Billing route/nav/command entry points are absent                               | source/search | `git grep -n "billing-and-plans\\                             | settings/billing\\                                                                                                     | BillingRoot\\       | BillingActionsButton" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'` | yes                             | passed                                                                                            |
| 03-01-02 | 01   | 1    | BILL-02, BILL-03 | T-03-02    | Edition badge cannot open a paid-plan modal and modal cluster has no consumers  | source/search | `git grep -n "PaidPlanUpgradeModal\\                          | components/license\\                                                                                                   | license/modal\\     | TALK_TO_SALES_URL\\                                                                          | SUBSCRIPTION_REDIRECTION_URLS\\ | SUBSCRIPTION_WEBPAGE_URLS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'` | yes | passed |
| 03-01-03 | 01   | 1    | BILL-04, BILL-06 | T-03-03    | Upsell stubs are classified and either removed or left as real CE functionality | source/search | `git grep -n "MARKETING_PRICING_PAGE_LINK\\                   | MARKETING_PLANE_ONE_PAGE_LINK\\                                                                                        | Upgrade to\\        | Plane Pro\\                                                                                  | Plane One\\                     | UpgradeBadge" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'`              | yes | passed |
| 03-01-04 | 01   | 1    | BILL-05          | T-03-04    | Plan/pricing and payment subscription data are removed with no dangling imports | source/search | `git grep -n "EProductSubscriptionEnum\\                      | IPaymentProduct\\                                                                                                      | TBillingFrequency\\ | PLANE_COMMUNITY_PRODUCTS\\                                                                   | PLANS_COMPARISON_LIST\\         | PLANE_PLANS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'`               | yes | passed |
| 03-01-05 | 01   | 1    | BILL-04, BILL-06 | T-03-05    | Phase 3 UI paths do not call Plane cloud hosts                                  | source/search | `git grep -n "plane\\.so\\                                    | app\\.plane\\.so" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build' ':!packages/i18n/src/locales'` | yes                 | passed                                                                                       |
| 03-01-06 | 01   | 1    | BILL-01..BILL-06 | T-03-06    | Monorepo still builds, type-checks, and lints after de-monetization             | integration   | `pnpm build && pnpm check:types && pnpm check:lint`           | yes                                                                                                                    | passed              |
| 03-01-07 | 01   | 1    | BILL-06          | T-03-07    | AGPL headers and upstream license files remain untouched                        | compliance    | `git diff -- LICENSE.txt COPYRIGHT.txt` plus header diff grep | yes                                                                                                                    | passed              |

## Wave 0 Requirements

Existing infrastructure covers all phase requirements:

- Source residual searches validate route, modal, billing constant, and cloud-host removal.
- TypeScript catches deleted barrel exports and dangling imports.
- The full build catches route/module breakage across apps and packages.

## Manual-Only Verifications

| Behavior                                         | Requirement | Why Manual                                                         | Test Instructions                                                                                                                       |
| ------------------------------------------------ | ----------- | ------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Version-only edition badge                       | BILL-03     | The exact visual affordance is user-facing and should be inspected | In the web app sidebar, confirm the badge displays version/community context only and cannot open a dialog or external link.            |
| Removed EE-only entry points do not leave blanks | BILL-06     | Source greps prove removal, but navigation needs a quick UI smoke  | In a workspace, confirm settings, sidebar, and pinned navigation do not expose billing, active-cycles upsell, or upgrade-only surfaces. |
| Issue subscriptions retained                     | BILL-06     | Naming collision can be over-deleted by search                     | Open an issue detail and confirm notify/subscribe behavior still exists if it was present before execution.                             |

## Validation Sign-Off

- [x] Billing route/nav/member action residual grep returns no Phase 3 source hits.
- [x] License modal, checkout, talk-to-sales, and subscription redirection residual grep returns no Phase 3 source hits.
- [x] Upgrade/marketing residual grep returns no in-app upsell hits.
- [x] Plan/pricing residual grep returns no live source consumers.
- [x] Plane cloud-host residuals are either gone from Phase 3 UI paths or explicitly classified as later brand/deploy scope.
- [x] `pnpm build && pnpm check:types && pnpm check:lint` is green.
- [x] AGPL headers, `LICENSE.txt`, and `COPYRIGHT.txt` are unchanged.
- [x] `nyquist_compliant: true` set in frontmatter.

**Approval:** passed 2026-06-01
