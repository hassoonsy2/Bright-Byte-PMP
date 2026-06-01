# Phase 03 Research: De-monetization + EE Ungating

**Phase:** 03 - De-monetization + EE Ungating
**Researched:** 2026-06-01
**Status:** Complete
**Inputs:** `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/research/{ARCHITECTURE,FEATURES,PITFALLS,SUMMARY}.md`, live repo inspection after Phase 2

## RESEARCH COMPLETE

Phase 03 is not a generic "turn on every paid feature" change. The repo still has the Plane CE edition seam (`@/plane-web/*` resolving into `apps/web/ce/*`), and several upsell surfaces are stubs for code that is not present in this checkout. The safe plan shape is inventory-first: remove billing and marketing surfaces, expose only CE-present functionality, and remove entry points for absent EE-only stubs so no route, button, or sidebar item opens a blank page or a Plane cloud URL.

## Phase Boundary

This phase delivers:

- No Billing/Plans settings route, page, sidebar entry, or Power-K workspace settings target.
- No license or paid-plan modal cluster, including upgrade, checkout, Stripe redirect, talk-to-sales, and plan card components.
- A version-only edition badge with no modal trigger and no upgrade affordance.
- No in-app upsell banners or CTAs for Plane One, Pro, Business, Enterprise, pricing, checkout, or talk-to-sales.
- Removal of plan/pricing data and billing subscription constants that exist only to support the removed UI.
- A retained inventory/classification record for every discovered upsell stub.
- Verification that source UI paths do not call `plane.so` or `app.plane.so` from billing, upsell, or removed stub surfaces.

This phase does not deliver:

- Porting closed/absent EE implementations into CE.
- Removing core work-item or notification "subscriptions"; those are notify-me features, not billing.
- Removing `apps/api/plane/license/**`; project research classifies this as instance registration/God-mode machinery, not paid-plan billing.
- Renaming `@/plane-web/*`; Phase 2 intentionally preserved edition seam aliases.
- Editing AGPL headers, `LICENSE.txt`, or `COPYRIGHT.txt`.
- Broad Phase 1/4/5 Plane-domain cleanup such as metadata, Docker defaults, support links, telemetry, or deployment config unless a Phase 3 UI path imports it.

## Source Inventory

| Surface | Files | Classification | Planning implication |
| --- | --- | --- | --- |
| Billing settings route | `apps/web/app/routes/core.ts`, `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/{page,header}.tsx` | Billing UI | Remove route registration and route modules first so deleted components are no longer imported. |
| Workspace settings nav | `packages/constants/src/settings/workspace.ts`, `packages/types/src/settings.ts`, `apps/web/core/components/settings/workspace/sidebar/item-icon.tsx`, Power-K workspace settings menu consumers | Billing UI | Remove `billing-and-plans` from settings constants, grouped settings, tab type, and icon map. Verify settings sidebar and command palette no longer expose billing. |
| Members page billing action | `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx`, `apps/web/ce/components/workspace/billing/billing-actions-button.tsx` | Billing UI, currently no-op | Remove import/render and then delete no-op component with the billing tree. |
| CE billing page body | `apps/web/ce/components/workspace/billing/**`, `apps/web/core/components/workspace/billing/comparison/**` | Billing UI and plan comparison | Delete after route/page consumers are gone. These files import payment/subscription constants and plan comparison helpers. |
| License upgrade modal cluster | `apps/web/ce/components/license/**`, `apps/web/core/components/license/**` | Billing/upsell UI | Neutralize edition badge first, then delete modal/card/checkout/talk-to-sales components and barrels. |
| Edition badge | `apps/web/ce/components/workspace/edition-badge.tsx` | CE-present surface with upgrade trigger | Replace with a non-clickable version-only badge. Remove `PaidPlanUpgradeModal`, state, `aria-haspopup`, and modal open handler. |
| Plan/pricing constants | `apps/web/core/constants/plans.tsx`, `packages/constants/src/payment.ts`, `packages/constants/src/subscription.ts`, related exports from `packages/constants/src/index.ts` | Billing data | Delete after all consumers are removed. `packages/types/src/payment.ts` and `packages/utils/src/subscription.ts` are also billing-only if no imports remain. |
| Marketing upgrade constants | `packages/constants/src/endpoints.ts` (`MARKETING_PRICING_PAGE_LINK`, `MARKETING_PLANE_ONE_PAGE_LINK`, `MARKETING_CONTACT_US_PAGE_LINK`) | Upgrade trigger constants | Remove pricing/one/contact constants if no remaining imports need them. Do not touch `WEBSITE_URL`/`SUPPORT_EMAIL` here; those belong to brand/deploy phases unless a billing UI path uses them. |
| Active cycles workspace page | `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/**`, `apps/web/ce/components/active-cycles/**`, `apps/web/core/components/workspace/sidebar/workspace-menu.tsx`, `apps/web/ce/components/workspace/sidebar/extended-sidebar-item.tsx` | EE-only/absent implementation stub | The CE root renders only `WorkspaceActiveCyclesUpgrade` and links to pricing. `CycleService.workspaceActiveCycles()` points to `/active-cycles/`, but no matching API route exists in `apps/api`. Remove the route/sidebar/pinned-entry upsell path rather than attempting to unlock it. Project-level active cycle components remain CE functionality and must stay. |
| Active cycles service method | `apps/web/core/services/cycle.service.ts`, `packages/services/src/cycle/cycle.service.ts`, `packages/types/src/workspace.ts` | Dead workspace-level EE endpoint | Remove only if no consumers remain after route removal. Keep project-level active-cycle service/store methods. |
| Bulk operations upsell banner | `apps/web/ce/components/issues/bulk-operations/root.tsx`, `apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx`, `apps/web/ce/hooks/use-bulk-operation-status.ts` | Absent implementation path, not currently visible | The hook returns `false`, which disables selection and prevents the banner from rendering. The frontend service has a `bulk-operation-issues` call, but no matching Django route exists. Delete the upgrade banner and keep selection disabled, or remove the unused root path if imports can be pruned cleanly. Do not enable this as CE-present without adding a real backend/UI implementation. |
| Issue embed upgrade card | `apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx`, `apps/web/ce/hooks/use-issue-embed.tsx` | EE-only/unused stub | The hook returns only an upgrade card and is not referenced by source callers. Remove the upgrade card/hook exports if no consumers remain. Do not add a broken embed widget. |
| Upgrade badge component | `apps/web/ce/components/workspace/upgrade-badge.tsx` plus imports in active cycles header/sidebar, workspace menu item, estimates, project settings features | Upsell badge | Remove component after all actual render sites are removed or proven unreachable. Estimate/project-settings references are currently unreachable because `isEstimateSystemEnabled()` filters out EE-only time estimates and all `PROJECT_FEATURES_LIST` items have `isPro: false`; still remove imports/dead branches where practical. |
| Time estimate EE flag | `packages/constants/src/estimates.ts`, `apps/web/ce/components/estimates/helper.tsx`, `apps/web/core/components/estimates/create/stage-one.tsx` | Potential feature gate | `time` estimates are marked `is_ee: true`, and CE helper returns false for `TIME`. This is a real gate but not a billing upsell in current UI because disabled options are filtered before rendering. Treat as follow-up only if Phase 3 scope explicitly includes time estimates; do not silently expose without backend/data verification. |
| Product update/help/support links | `latest-feature-block`, product updates modal/footer, help-section, docs/forum/support links | Brand/support surfaces, not billing by default | Not a Phase 3 removal unless the link is part of an upsell or billing path. Phase 1/5 should handle broad Plane/support domain cleanup. |
| Issue subscriptions | `apps/web/core/components/issues/issue-detail/subscription.tsx`, `apps/web/core/store/issue/issue-details/subscription.store.ts`, `packages/types/src/issues/issue_subscription.ts` | Core PM notification feature | Leave intact. Do not match bare `subscription` as billing without checking context. |
| Reserved slugs | `packages/constants/src/workspace.ts` includes `billing`, `upgrade`, `license` in `RESTRICTED_URLS` | Workspace URL safety | Keep reserved slugs unless a later product decision says otherwise; removing UI does not require allowing those slugs. |

Generated output under `apps/web/.react-router/**` and `apps/web/build/**` appeared during file searches and should be ignored for source edits and residual grep gates.

## Critical Dependencies and Ordering

1. Remove route/nav entry points before deleting billing components.
2. Convert `WorkspaceEditionBadge` to a version-only component before deleting `PaidPlanUpgradeModal`.
3. Delete/neutralize direct upsell stubs before deleting the constants they import.
4. Remove plan/pricing data only after `EProductSubscriptionEnum`, `TBillingFrequency`, `IPaymentProduct`, `getSubscriptionName`, and pricing helpers have no source consumers.
5. Classify each `*-upgrade*`, `UpgradeBadge`, `MARKETING_*`, and `SUBSCRIPTION_*` hit before changing behavior.
6. Run residual searches before final verification, scoped to source and excluding generated output/planning docs.

## Validation Architecture

### Primary Commands

| Purpose | Command |
| --- | --- |
| Full build | `pnpm build` |
| Typecheck | `pnpm check:types` |
| Lint | `pnpm check:lint` |
| Source billing route residual | `git grep -n "billing-and-plans\\|settings/billing\\|BillingRoot\\|BillingActionsButton" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'` |
| License/modal residual | `git grep -n "PaidPlanUpgradeModal\\|components/license\\|license/modal\\|TALK_TO_SALES_URL\\|SUBSCRIPTION_REDIRECTION_URLS\\|SUBSCRIPTION_WEBPAGE_URLS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'` |
| Upgrade/marketing residual | `git grep -n "MARKETING_PRICING_PAGE_LINK\\|MARKETING_PLANE_ONE_PAGE_LINK\\|Upgrade to\\|upgrade to Plane\\|Plane Pro\\|Plane One" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'` |
| Cloud host residual in web UI | `git grep -n "plane\\.so\\|app\\.plane\\.so" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build' ':!packages/i18n/src/locales'` |
| Plan/pricing residual | `git grep -n "EProductSubscriptionEnum\\|IPaymentProduct\\|TBillingFrequency\\|PLANE_COMMUNITY_PRODUCTS\\|PLANS_COMPARISON_LIST\\|PLANE_PLANS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'` |
| Header/license preservation | `git diff -- LICENSE.txt COPYRIGHT.txt` and header diff grep for changed AGPL header lines |

### Acceptance Gate

The phase is not complete unless:

- `pnpm build`, `pnpm check:types`, and `pnpm check:lint` pass.
- Billing settings page, route, nav, command palette target, and member billing action are absent.
- Edition badge has no modal import, stateful open handler, `aria-haspopup`, pricing link, or upgrade copy.
- License, billing, plan comparison, checkout, talk-to-sales, and plan/pricing constants have no source consumers.
- Every upsell stub found in this research is either deleted, no longer reachable, or explicitly retained as a non-billing PM feature.
- No source UI path opened by Phase 3 calls `plane.so` or `app.plane.so`.
- Issue subscription/notification code and AGPL headers remain untouched except for unrelated pre-existing changes.

## Planning Guidance

Use one implementation plan with a first-class inventory task and a cleanup task at the end. Do not split "delete billing" and "ungate stubs" into disconnected plans because the constants/components become dead only after the route and badge changes are done.

Prefer deletion over no-op replacement for pure billing code once imports are gone. Prefer clean entry-point removal over half-built UI for absent EE stubs such as workspace active cycles, bulk operations, and issue embeds.
