---
phase: 03-de-monetization-ee-ungating
plan: 01
type: execute
wave: 1
depends_on:
  - 02-01-atomic-package-scope-rename
files_modified:
  - apps/web/app/routes/core.ts
  - apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/**
  - apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx
  - apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/**
  - apps/web/ce/components/active-cycles/**
  - apps/web/ce/components/license/**
  - apps/web/core/components/license/**
  - apps/web/ce/components/workspace/billing/**
  - apps/web/core/components/workspace/billing/**
  - apps/web/ce/components/workspace/edition-badge.tsx
  - apps/web/ce/components/workspace/upgrade-badge.tsx
  - apps/web/ce/components/workspace/sidebar/extended-sidebar-item.tsx
  - apps/web/core/components/workspace/sidebar/workspace-menu.tsx
  - apps/web/core/components/workspace/sidebar/workspace-menu-item.tsx
  - apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx
  - apps/web/core/components/common/pro-icon.tsx
  - apps/web/ce/components/issues/bulk-operations/root.tsx
  - apps/web/ce/hooks/use-bulk-operation-status.ts
  - apps/web/ce/components/pages/editor/embed/**
  - apps/web/ce/hooks/use-issue-embed.tsx
  - apps/web/core/components/estimates/create/stage-one.tsx
  - apps/web/core/components/project/settings/features-list.tsx
  - apps/web/core/services/cycle.service.ts
  - packages/services/src/cycle/cycle.service.ts
  - packages/types/src/workspace.ts
  - apps/web/core/constants/plans.tsx
  - packages/constants/src/payment.ts
  - packages/constants/src/subscription.ts
  - packages/constants/src/endpoints.ts
  - packages/constants/src/index.ts
  - packages/types/src/payment.ts
  - packages/types/src/index.ts
  - packages/utils/src/subscription.ts
  - packages/utils/src/index.ts
  - packages/constants/src/settings/workspace.ts
  - packages/types/src/settings.ts
  - apps/web/core/components/settings/workspace/sidebar/item-icon.tsx
  - packages/constants/src/event-tracker/core.ts
autonomous: false
requirements: [BILL-01, BILL-02, BILL-03, BILL-04, BILL-05, BILL-06]
must_haves:
  truths:
    - "There is no workspace Billing/Plans settings route, page, settings sidebar entry, Power-K target, or members-page billing action."
    - "The workspace edition badge is version-only and cannot open a paid-plan modal or external upgrade URL."
    - "The license modal cluster, billing comparison UI, plan cards, checkout button, Stripe redirect, talk-to-sales card, and plan/pricing data are deleted or have no source consumers."
    - "Every discovered upsell stub is classified before removal: workspace active cycles, bulk operations, and issue embeds are treated as absent-code stubs unless real backend/UI support is proven in this phase."
    - "Project-level active cycle functionality, issue notification subscriptions, reserved workspace slugs, AGPL headers, and the `@/plane-web/*` edition alias remain intact."
    - "`pnpm build`, `pnpm check:types`, and `pnpm check:lint` pass after source residual gates are clean or explicitly documented as out-of-scope brand/deploy leftovers."
  artifacts:
    - path: ".planning/phases/03-de-monetization-ee-ungating/03-RESEARCH.md"
      provides: "Inventory/classification record required by BILL-06"
      contains: "Source Inventory"
    - path: ".planning/phases/03-de-monetization-ee-ungating/03-VALIDATION.md"
      provides: "Nyquist validation contract and residual grep gates"
      contains: "Phase 03 - Validation Strategy"
  key_links:
    - from: "apps/web/app/routes/core.ts"
      to: "apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/**"
      via: "workspace billing route registration"
      pattern: ":workspaceSlug/settings/billing"
    - from: "apps/web/ce/components/workspace/edition-badge.tsx"
      to: "apps/web/ce/components/license/modal/upgrade-modal.tsx"
      via: "PaidPlanUpgradeModal import"
      pattern: "PaidPlanUpgradeModal"
    - from: "apps/web/ce/components/active-cycles/root.tsx"
      to: "packages/constants/src/endpoints.ts"
      via: "MARKETING_PRICING_PAGE_LINK"
      pattern: "WorkspaceActiveCyclesUpgrade"
---

<objective>
Remove billing, paid-plan, license, and upsell surfaces from the Bright-Byte web app while preserving working Community Edition project-management functionality. The plan is inventory-first: delete pure billing surfaces, neutralize the edition badge, remove absent-code EE upsell entry points, and verify no billing route, upgrade trigger, pricing data, or Plane cloud upgrade URL remains reachable from Phase 3 UI paths.

Purpose: Bright-Byte PMP must operate as a fully branded, fully unlocked client PM tool with no payment or licensing friction. Removing an upsell banner is not enough if it leaves a blank route, dead button, or cloud-only endpoint call.
Output: A de-monetized app surface with billing/license code pruned, CE-present functionality preserved, absent EE stubs removed from navigation, and all BILL-01 through BILL-06 validation gates green.
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
@.planning/research/ARCHITECTURE.md
@.planning/research/FEATURES.md
@.planning/research/PITFALLS.md
@.planning/research/SUMMARY.md
@.planning/phases/03-de-monetization-ee-ungating/03-RESEARCH.md
@.planning/phases/03-de-monetization-ee-ungating/03-VALIDATION.md

<interfaces>
Billing route and settings surfaces:
- `apps/web/app/routes/core.ts` currently registers `:workspaceSlug/settings/billing`.
- `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/page.tsx` imports `BillingRoot`.
- `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/header.tsx` reads `WORKSPACE_SETTINGS["billing-and-plans"]`.
- `packages/constants/src/settings/workspace.ts` owns `WORKSPACE_SETTINGS["billing-and-plans"]`, `WORKSPACE_SETTINGS_ACCESS`, and `GROUPED_WORKSPACE_SETTINGS`.
- `packages/types/src/settings.ts` includes `"billing-and-plans"` in `TWorkspaceSettingsTabs`.
- `apps/web/core/components/settings/workspace/sidebar/item-icon.tsx` maps `"billing-and-plans"` to `CreditCard`.
- `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx` renders `BillingActionsButton`.

License and billing component clusters:

- `apps/web/ce/components/license/**`
- `apps/web/core/components/license/**`
- `apps/web/ce/components/workspace/billing/**`
- `apps/web/core/components/workspace/billing/comparison/**`
- `apps/web/core/constants/plans.tsx`
- `packages/constants/src/payment.ts`
- `packages/constants/src/subscription.ts`
- `packages/types/src/payment.ts`
- `packages/utils/src/subscription.ts`

Known upsell stubs from research:

- Workspace active cycles: route files under `apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/**`, CE components under `apps/web/ce/components/active-cycles/**`, and workspace sidebar entry in `apps/web/core/components/workspace/sidebar/workspace-menu.tsx`.
- Bulk operations: `apps/web/ce/components/issues/bulk-operations/root.tsx`, `apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx`, `apps/web/ce/hooks/use-bulk-operation-status.ts`.
- Issue embeds: `apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx`, `apps/web/ce/hooks/use-issue-embed.tsx`.
- Upgrade badge: `apps/web/ce/components/workspace/upgrade-badge.tsx` and imports in active cycles header/sidebar, workspace menu item, estimates create stage, and project feature settings.

Preserve exactly:

- Project-level active cycle components and services: `apps/web/ce/components/cycles/active-cycle/**`, `apps/web/core/components/cycles/active-cycle/**`, `fetchActiveCycle`, `workspaceActiveCyclesProgress`, and `workspaceActiveCyclesAnalytics`.
- Issue/work-item notification subscriptions: files under issue detail subscription stores/types/components.
- `packages/constants/src/workspace.ts` reserved slugs including `billing`, `upgrade`, and `license`.
- `apps/api/plane/license/**` instance-registration code.
- `@/plane-web/*` and `@/plane-live/*` aliases.
- AGPL copyright headers, `LICENSE.txt`, and `COPYRIGHT.txt`.
  </interfaces>
  </context>

<constraints>
- The invocation used `--skip-ui`; no `UI-SPEC.md` exists. Do not invent a new visual redesign. Use the existing sidebar/settings/button patterns and keep UI changes minimal.
- Delete pure billing code after consumers are removed. Do not leave dead no-op billing exports just to avoid import cleanup.
- Do not enable a feature unless both UI and backend support are proven in this repo. Workspace active cycles, bulk operations, and issue embeds are absent-code stubs unless execution discovers complete local support.
- Do not remove issue notification subscriptions. Match billing by `payment`, `plan`, `pricing`, `checkout`, `license`, `upgrade`, `MARKETING_*`, and `SUBSCRIPTION_*`, not by the bare word `subscription`.
- Do not broaden Phase 3 into all Plane-domain cleanup. Product metadata, Docker defaults, support links, telemetry, and deployment defaults are Phase 1/4/5 unless directly tied to billing or upsell UI.
- No schema push is required; Phase 3 does not modify database schema files.
- Existing frontend source has no general unit-test harness for `apps/web`; validation relies on source residual gates, typecheck, build, lint, and manual smoke checks.
</constraints>

<threat_model>
<threat id="T-03-01" severity="high" requirement="BILL-01">
<risk>Billing route, settings nav, command palette, or members-page action remains reachable after component deletion, causing dead navigation or visible monetization.</risk>
<mitigation>Remove route/page/nav consumers before deleting billing component trees. Verify with targeted source greps for `billing-and-plans`, `settings/billing`, `BillingRoot`, and `BillingActionsButton`.</mitigation>
</threat>
<threat id="T-03-02" severity="high" requirement="BILL-02,BILL-03">
<risk>The edition badge keeps a modal trigger or a license modal import survives through a barrel export.</risk>
<mitigation>Rewrite `WorkspaceEditionBadge` first as non-clickable version-only UI, then delete the license modal/card cluster and run modal residual greps.</mitigation>
</threat>
<threat id="T-03-03" severity="high" requirement="BILL-04,BILL-06">
<risk>An absent EE stub is treated as unlockable, leaving a blank page, dead selection mode, or unavailable backend endpoint.</risk>
<mitigation>Use the research inventory to remove absent-code entry points for workspace active cycles, bulk operations, and issue embeds unless execution proves complete local support.</mitigation>
</threat>
<threat id="T-03-04" severity="medium" requirement="BILL-05">
<risk>Deleting payment/plan types before all consumers are removed breaks package exports and transitive builds.</risk>
<mitigation>Delete plan/pricing constants after route, modal, and billing components are gone. Update package index exports and run `pnpm check:types` immediately after this cleanup.</mitigation>
</threat>
<threat id="T-03-05" severity="medium" requirement="BILL-04,BILL-06">
<risk>Residual `plane.so` or `app.plane.so` links remain in Phase 3 UI paths and continue to send users to Plane cloud billing/marketing.</risk>
<mitigation>Run source-scoped cloud-host greps. Classify remaining hits as either Phase 3 failures or later brand/deploy surfaces before final verification.</mitigation>
</threat>
<threat id="T-03-06" severity="medium" requirement="BILL-06">
<risk>Broad search deletion removes core issue notification subscriptions or AGPL/license machinery.</risk>
<mitigation>Keep issue subscription files and `apps/api/plane/license/**` untouched. Use final diff review and targeted greps to confirm only billing/upsell subscription constants were removed.</mitigation>
</threat>
</threat_model>

<tasks>

<task type="auto">
  <name>Task 1: Preflight Phase 3 inventory and worktree boundary</name>
  <read_first>
    - .planning/phases/03-de-monetization-ee-ungating/03-RESEARCH.md
    - .planning/phases/03-de-monetization-ee-ungating/03-VALIDATION.md
    - .planning/REQUIREMENTS.md
    - git status and git diff for any pre-existing user changes
  </read_first>
  <files>none</files>
  <action>
    Confirm the worktree state before editing. Re-run a source inventory for billing and upsell surfaces using `git grep` because `rg` is not available in this environment. Record any newly discovered source hit that is not already classified in `03-RESEARCH.md`; classify it as billing UI, upgrade trigger, absent EE stub, CE-present feature, core notification subscription, or out-of-scope brand/deploy link before changing it. Do not edit files in this task.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && git status --short</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && git grep -n "PaidPlanUpgradeModal\\|BillingRoot\\|BillingActionsButton\\|MARKETING_PRICING_PAGE_LINK\\|MARKETING_PLANE_ONE_PAGE_LINK\\|SUBSCRIPTION_REDIRECTION_URLS\\|SUBSCRIPTION_WEBPAGE_URLS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build' || true</automated>
  </verify>
  <acceptance_criteria>
    - Pre-existing dirty files are known before edits begin.
    - Every billing/upsell source hit is either already in `03-RESEARCH.md` or added to the executor's working notes with a classification before edits.
    - No code file has been modified yet.
  </acceptance_criteria>
  <done>The implementation starts from a known worktree and an up-to-date source inventory.</done>
</task>

<task type="auto">
  <name>Task 2: Remove Billing/Plans route, settings nav, and member action</name>
  <read_first>
    - apps/web/app/routes/core.ts
    - apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/page.tsx
    - apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/header.tsx
    - apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx
    - packages/constants/src/settings/workspace.ts
    - packages/types/src/settings.ts
    - apps/web/core/components/settings/workspace/sidebar/item-icon.tsx
    - apps/web/core/components/power-k/ui/pages/open-entity/workspace-settings-menu.tsx
  </read_first>
  <files>
    apps/web/app/routes/core.ts,
    apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/**,
    apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/members/page.tsx,
    packages/constants/src/settings/workspace.ts,
    packages/types/src/settings.ts,
    apps/web/core/components/settings/workspace/sidebar/item-icon.tsx
  </files>
  <action>
    Delete the route registration for `:workspaceSlug/settings/billing` from `apps/web/app/routes/core.ts`. Delete the billing route page and header files. Remove the `BillingActionsButton` import and JSX render from the workspace members settings page. Remove `"billing-and-plans"` from `TWorkspaceSettingsTabs`, `WORKSPACE_SETTINGS`, `GROUPED_WORKSPACE_SETTINGS`, and `WORKSPACE_SETTINGS_ICONS`. Ensure `WORKSPACE_SETTINGS_ACCESS` continues deriving from the reduced `WORKSPACE_SETTINGS` object and Power-K workspace settings menu still maps over valid settings only.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "billing-and-plans\\|settings/billing\\|BillingRoot\\|BillingActionsButton" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
  </verify>
  <acceptance_criteria>
    - `apps/web/app/routes/core.ts` does not contain `settings/billing`.
    - No source file under `apps/web` or `packages` contains `billing-and-plans`, `BillingRoot`, or `BillingActionsButton`.
    - Workspace settings type union no longer includes `"billing-and-plans"`.
    - `pnpm check:types` exits 0 after route/nav removal.
  </acceptance_criteria>
  <done>Billing/Plans is no longer reachable from routing, settings navigation, Power-K settings, or workspace members actions.</done>
</task>

<task type="auto">
  <name>Task 3: Neutralize the edition badge and remove the license modal cluster</name>
  <read_first>
    - apps/web/ce/components/workspace/edition-badge.tsx
    - apps/web/ce/components/license/index.ts
    - apps/web/ce/components/license/modal/upgrade-modal.tsx
    - apps/web/core/components/license/index.ts
    - apps/web/core/components/license/modal/card/checkout-button.tsx
    - apps/web/core/components/license/modal/card/plan-upgrade.tsx
    - apps/web/core/components/license/modal/card/talk-to-sales.tsx
  </read_first>
  <files>
    apps/web/ce/components/workspace/edition-badge.tsx,
    apps/web/ce/components/license/**,
    apps/web/core/components/license/**
  </files>
  <action>
    Rewrite `WorkspaceEditionBadge` so it renders a non-clickable version-only badge using existing local UI primitives. Keep the tooltip content `Version: v${packageJson.version}` or an equivalent version-only string. Remove `useState`, `PaidPlanUpgradeModal`, modal open/close handlers, `aria-haspopup="dialog"`, and any `onClick` that opens upgrade UI. Delete `apps/web/ce/components/license/**` and `apps/web/core/components/license/**` after no source imports remain.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "PaidPlanUpgradeModal\\|components/license\\|license/modal\\|TALK_TO_SALES_URL\\|SUBSCRIPTION_REDIRECTION_URLS\\|SUBSCRIPTION_WEBPAGE_URLS\\|Redirecting to Stripe" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "aria-haspopup=\\\"dialog\\\"\\|isPaidPlanPurchaseModalOpen\\|setIsPaidPlanPurchaseModalOpen" -- apps/web/ce/components/workspace/edition-badge.tsx</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
  </verify>
  <acceptance_criteria>
    - `WorkspaceEditionBadge` imports `package.json` for version display but does not import `PaidPlanUpgradeModal`.
    - `WorkspaceEditionBadge` has no upgrade modal state and no click handler that opens a dialog or external URL.
    - No source file contains `PaidPlanUpgradeModal`, `license/modal`, `Redirecting to Stripe`, `TALK_TO_SALES_URL`, `SUBSCRIPTION_REDIRECTION_URLS`, or `SUBSCRIPTION_WEBPAGE_URLS`.
    - `pnpm check:types` exits 0 after license cluster deletion.
  </acceptance_criteria>
  <done>The Community badge is version-only and the paid-plan modal/checkout cluster is gone.</done>
</task>

<task type="auto">
  <name>Task 4: Delete billing component trees and plan/pricing data</name>
  <read_first>
    - apps/web/ce/components/workspace/billing/root.tsx
    - apps/web/ce/components/workspace/billing/comparison/root.tsx
    - apps/web/core/components/workspace/billing/comparison/base.tsx
    - apps/web/core/constants/plans.tsx
    - packages/constants/src/payment.ts
    - packages/constants/src/subscription.ts
    - packages/constants/src/index.ts
    - packages/types/src/payment.ts
    - packages/types/src/index.ts
    - packages/utils/src/subscription.ts
    - packages/utils/src/index.ts
  </read_first>
  <files>
    apps/web/ce/components/workspace/billing/**,
    apps/web/core/components/workspace/billing/**,
    apps/web/core/constants/plans.tsx,
    packages/constants/src/payment.ts,
    packages/constants/src/subscription.ts,
    packages/constants/src/index.ts,
    packages/types/src/payment.ts,
    packages/types/src/index.ts,
    packages/utils/src/subscription.ts,
    packages/utils/src/index.ts
  </files>
  <action>
    Delete the CE and core workspace billing component trees after Task 2 has removed route consumers. Delete `apps/web/core/constants/plans.tsx`, `packages/constants/src/payment.ts`, and `packages/constants/src/subscription.ts`. Remove `export * from "./payment";` and `export * from "./subscription";` from `packages/constants/src/index.ts` only after no non-billing consumers remain. Delete `packages/types/src/payment.ts` and remove its export from `packages/types/src/index.ts` if `EProductSubscriptionEnum`, `TBillingFrequency`, `IPaymentProduct`, `TProductBillingFrequency`, and `TSubscriptionPrice` have no source consumers. Delete `packages/utils/src/subscription.ts` and remove its export from `packages/utils/src/index.ts` if `getSubscriptionName`, `getBaseSubscriptionName`, `calculateYearlyDiscount`, and `getSubscriptionPriceDetails` have no source consumers.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "EProductSubscriptionEnum\\|IPaymentProduct\\|TBillingFrequency\\|TProductBillingFrequency\\|TSubscriptionPrice\\|PLANE_COMMUNITY_PRODUCTS\\|DEFAULT_PRODUCT_BILLING_FREQUENCY\\|SUBSCRIPTION_WITH_BILLING_FREQUENCY\\|PLANS_COMPARISON_LIST\\|PLANE_PLANS\\|FREE_PLAN_UPGRADE_FEATURES\\|PRO_PLAN_FEATURES\\|BUSINESS_PLAN_FEATURES\\|ENTERPRISE_PLAN_FEATURES" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && test ! -d apps/web/ce/components/workspace/billing && test ! -d apps/web/core/components/workspace/billing</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
  </verify>
  <acceptance_criteria>
    - No workspace billing component files remain under `apps/web/ce/components/workspace/billing` or `apps/web/core/components/workspace/billing`.
    - No source file imports or references payment plan types, billing frequencies, plan comparison constants, plan feature arrays, or `PLANE_COMMUNITY_PRODUCTS`.
    - Package index files do not export deleted billing modules.
    - `pnpm check:types` exits 0 after billing data deletion.
  </acceptance_criteria>
  <done>Plan/pricing data and billing UI modules are removed without dangling package exports.</done>
</task>

<task type="auto">
  <name>Task 5: Remove absent-code workspace active cycles upsell path</name>
  <read_first>
    - apps/web/app/routes/core.ts
    - apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/layout.tsx
    - apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/page.tsx
    - apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/header.tsx
    - apps/web/ce/components/active-cycles/root.tsx
    - apps/web/ce/components/active-cycles/workspace-active-cycles-upgrade.tsx
    - apps/web/core/components/workspace/sidebar/workspace-menu.tsx
    - apps/web/core/components/workspace/sidebar/workspace-menu-item.tsx
    - apps/web/ce/components/workspace/sidebar/extended-sidebar-item.tsx
    - apps/web/core/services/cycle.service.ts
    - packages/services/src/cycle/cycle.service.ts
    - packages/types/src/workspace.ts
    - apps/web/ce/components/cycles/active-cycle/root.tsx
  </read_first>
  <files>
    apps/web/app/routes/core.ts,
    apps/web/app/(all)/[workspaceSlug]/(projects)/active-cycles/**,
    apps/web/ce/components/active-cycles/**,
    apps/web/core/components/workspace/sidebar/workspace-menu.tsx,
    apps/web/core/components/workspace/sidebar/workspace-menu-item.tsx,
    apps/web/ce/components/workspace/sidebar/extended-sidebar-item.tsx,
    apps/web/core/services/cycle.service.ts,
    packages/services/src/cycle/cycle.service.ts,
    packages/types/src/workspace.ts
  </files>
  <action>
    Remove the workspace-level active cycles route registration `:workspaceSlug/active-cycles` and delete the corresponding route directory. Remove the `active-cycles` item from `SIDEBAR_WORKSPACE_MENU_ITEMS`. Remove active-cycle upgrade badge rendering from extended sidebar pinned navigation. Remove the unconditional `UpgradeBadge` render from `SidebarWorkspaceMenuItem`; if it exists only to decorate the removed active-cycles item, remove its import. Delete `apps/web/ce/components/active-cycles/**`. Remove `workspaceActiveCycles()` methods and `IWorkspaceActiveCyclesResponse` only if no source consumers remain. Preserve project-level active cycle components and methods such as `fetchActiveCycle`, `workspaceActiveCyclesProgress`, and `workspaceActiveCyclesAnalytics`.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "active-cycles\\|WorkspaceActiveCyclesRoot\\|WorkspaceActiveCyclesUpgrade\\|workspaceActiveCycles(" -- apps/web packages/services packages/types -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && git grep -n "fetchActiveCycle\\|workspaceActiveCyclesProgress\\|workspaceActiveCyclesAnalytics" -- apps/web/core apps/web/ce packages/services -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
  </verify>
  <acceptance_criteria>
    - No workspace route or sidebar menu links to `/:workspaceSlug/active-cycles`.
    - No source file contains `WorkspaceActiveCyclesUpgrade` or imports `MARKETING_PRICING_PAGE_LINK` for active cycles.
    - Project-level active cycle components and progress/analytics service methods still exist.
    - `pnpm check:types` exits 0 after workspace active cycles cleanup.
  </acceptance_criteria>
  <done>The absent-code workspace active cycles upsell surface is removed without damaging project-level cycles.</done>
</task>

<task type="auto">
  <name>Task 6: Remove remaining upgrade stubs without enabling unsupported features</name>
  <read_first>
    - apps/web/ce/hooks/use-bulk-operation-status.ts
    - apps/web/ce/components/issues/bulk-operations/root.tsx
    - apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx
    - apps/web/core/components/issues/issue-layouts/list/default.tsx
    - apps/web/core/components/issues/issue-layouts/spreadsheet/spreadsheet-view.tsx
    - apps/web/core/components/gantt-chart/chart/main-content.tsx
    - apps/web/core/services/issue/issue.service.ts
    - apps/api/plane/app/urls/issue.py
    - apps/web/ce/hooks/use-issue-embed.tsx
    - apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx
    - apps/web/ce/hooks/pages/use-extended-editor-extensions.ts
    - apps/web/ce/components/workspace/upgrade-badge.tsx
    - apps/web/core/components/common/pro-icon.tsx
    - apps/web/core/components/estimates/create/stage-one.tsx
    - apps/web/core/components/project/settings/features-list.tsx
  </read_first>
  <files>
    apps/web/ce/hooks/use-bulk-operation-status.ts,
    apps/web/ce/components/issues/bulk-operations/root.tsx,
    apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx,
    apps/web/ce/hooks/use-issue-embed.tsx,
    apps/web/ce/components/pages/editor/embed/**,
    apps/web/ce/components/workspace/upgrade-badge.tsx,
    apps/web/core/components/common/pro-icon.tsx,
    apps/web/core/components/estimates/create/stage-one.tsx,
    apps/web/core/components/project/settings/features-list.tsx
  </files>
  <action>
    Delete the bulk operations upgrade banner and ensure `IssueBulkOperationsRoot` never renders an upsell. Keep `useBulkOperationStatus()` returning `false` unless execution also adds a complete backend route for `/bulk-operation-issues/` and a real bulk operation toolbar; this plan does not require adding that feature. Remove issue embed upgrade card and hook exports if no source callers remain; otherwise make the hook return no `widgetCallback` rather than an upgrade card. Delete `UpgradeBadge` after removing imports. Delete `ProIcon` after active cycles and issue embed stubs are gone if no non-upsell consumers remain. In `EstimateCreateStageOne`, remove the unreachable `UpgradeBadge` branch and keep unsupported estimate systems filtered by `isEstimateSystemEnabled()`. In `ProjectFeaturesList`, remove `UpgradeBadge` import and any `isPro` rendering branch if all features remain `isPro: false`.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "BulkOperationsUpgradeBanner\\|MARKETING_PLANE_ONE_PAGE_LINK\\|IssueEmbedUpgradeCard\\|https://plane.so/pro\\|UpgradeBadge\\|ProIcon" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "bulk-operation-issues" -- apps/api apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
  </verify>
  <acceptance_criteria>
    - No source file contains `BulkOperationsUpgradeBanner`, `IssueEmbedUpgradeCard`, `UpgradeBadge`, `MARKETING_PLANE_ONE_PAGE_LINK`, or `https://plane.so/pro`.
    - Bulk operation selection is not enabled unless a matching backend route and real non-upsell UI have been implemented in the same task.
    - Issue embed editor extension does not render an upgrade card.
    - `pnpm check:types` exits 0 after stub cleanup.
  </acceptance_criteria>
  <done>Remaining upgrade-only stubs are removed or made inert without pretending absent EE implementations exist.</done>
</task>

<task type="auto">
  <name>Task 7: Remove upgrade trigger constants and billing tracker elements</name>
  <read_first>
    - packages/constants/src/endpoints.ts
    - packages/constants/src/event-tracker/core.ts
    - apps/web/core/components/workspace/sidebar/help-section/root.tsx
    - apps/web/core/components/global/product-updates/footer.tsx
    - apps/web/core/components/common/latest-feature-block.tsx
  </read_first>
  <files>
    packages/constants/src/endpoints.ts,
    packages/constants/src/event-tracker/core.ts
  </files>
  <action>
    Remove upgrade-only marketing constants `MARKETING_PRICING_PAGE_LINK`, `MARKETING_PLANE_ONE_PAGE_LINK`, and `MARKETING_CONTACT_US_PAGE_LINK` from `packages/constants/src/endpoints.ts` after all imports are gone. Keep `WEBSITE_URL` and `SUPPORT_EMAIL` in this phase because they support brand/deploy surfaces outside billing. Remove billing-only tracker event `upgrade_plan_redirected` and tracker elements `BILLING_UPGRADE_BUTTON` and `BILLING_TALK_TO_SALES_BUTTON` from `packages/constants/src/event-tracker/core.ts` after no source consumers remain. Do not remove docs, support, changelog, or metadata links unless the link is part of a billing/upgrade path.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "MARKETING_PRICING_PAGE_LINK\\|MARKETING_PLANE_ONE_PAGE_LINK\\|MARKETING_CONTACT_US_PAGE_LINK\\|upgrade_plan_redirected\\|BILLING_UPGRADE_BUTTON\\|BILLING_TALK_TO_SALES_BUTTON" -- apps packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
  </verify>
  <acceptance_criteria>
    - Upgrade-only marketing constants are absent from `packages/constants/src/endpoints.ts`.
    - Billing tracker events/elements are absent from `packages/constants/src/event-tracker/core.ts`.
    - `WEBSITE_URL` and `SUPPORT_EMAIL` remain available.
    - `pnpm check:types` exits 0 after constants cleanup.
  </acceptance_criteria>
  <done>Shared constants no longer expose billing or upgrade triggers.</done>
</task>

<task type="auto">
  <name>Task 8: Run final residual gates and full verification</name>
  <read_first>
    - .planning/phases/03-de-monetization-ee-ungating/03-VALIDATION.md
    - .planning/phases/03-de-monetization-ee-ungating/03-RESEARCH.md
    - package.json
    - apps/web/package.json
  </read_first>
  <files>none</files>
  <action>
    Run every residual search gate from `03-VALIDATION.md`. For each remaining hit, classify it as a Phase 3 failure or an explicitly out-of-scope Phase 1/4/5 brand/deploy link. Fix all Phase 3 failures. Then run `pnpm build`, `pnpm check:types`, and `pnpm check:lint`. Review `git diff` to confirm issue notification subscriptions, `apps/api/plane/license/**`, reserved workspace slugs, AGPL headers, `LICENSE.txt`, `COPYRIGHT.txt`, and `@/plane-web/*` aliases were not damaged.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "billing-and-plans\\|settings/billing\\|BillingRoot\\|BillingActionsButton" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "PaidPlanUpgradeModal\\|components/license\\|license/modal\\|TALK_TO_SALES_URL\\|SUBSCRIPTION_REDIRECTION_URLS\\|SUBSCRIPTION_WEBPAGE_URLS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "MARKETING_PRICING_PAGE_LINK\\|MARKETING_PLANE_ONE_PAGE_LINK\\|Upgrade to\\|upgrade to Plane\\|Plane Pro\\|Plane One\\|UpgradeBadge" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "EProductSubscriptionEnum\\|IPaymentProduct\\|TBillingFrequency\\|PLANE_COMMUNITY_PRODUCTS\\|PLANS_COMPARISON_LIST\\|PLANE_PLANS" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && ! git grep -n "plane.so/pro\\|plane.so/pricing\\|plane.so/one\\|talk-to-sales\\|app.plane.so/upgrade" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build' ':!packages/i18n/src/locales'</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && git grep -n "plane\\.so\\|app\\.plane\\.so" -- apps/web packages -- ':!apps/web/.react-router' ':!apps/web/build' ':!packages/i18n/src/locales' || true</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && git diff -- LICENSE.txt COPYRIGHT.txt</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm build</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:types</automated>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm check:lint</automated>
  </verify>
  <acceptance_criteria>
    - All Phase 3 residual greps return no Phase 3 source failures.
    - Any remaining `plane.so` or `app.plane.so` hit is documented as out-of-scope brand/deploy/support cleanup, not billing or upsell UI.
    - `git diff -- LICENSE.txt COPYRIGHT.txt` is empty.
    - No diff changes AGPL header text.
    - `pnpm build`, `pnpm check:types`, and `pnpm check:lint` exit 0.
  </acceptance_criteria>
  <done>Automated Phase 3 verification is complete and green.</done>
</task>

<task type="manual">
  <name>Task 9: Smoke test user-facing de-monetization paths</name>
  <read_first>
    - apps/web/package.json
    - .planning/phases/03-de-monetization-ee-ungating/03-VALIDATION.md
  </read_first>
  <files>none</files>
  <action>
    Start the web app using the repo's normal development command if a server is not already running. In a workspace, inspect the sidebar, workspace settings, command palette workspace settings entries, project list/cycle views, issue list/spreadsheet/gantt selection behavior, and page editor. Confirm removed entry points do not leave blank pages or dead buttons. Confirm issue notification subscription behavior still exists where it existed before execution. Do not run backend Docker tests unless execution touched backend code; this plan is frontend/package source cleanup.
  </action>
  <verify>
    <manual>Workspace settings sidebar has General, Members, Export, and Webhooks where permitted, but no Billing/Plans item.</manual>
    <manual>Opening the workspace sidebar badge shows no paid-plan modal and no external upgrade link.</manual>
    <manual>Workspace sidebar has no Active Cycles upsell route entry.</manual>
    <manual>Issue list/spreadsheet/gantt views show no Upgrade to One/Pro banner when selecting issues.</manual>
    <manual>Page editor shows no issue embed upgrade card.</manual>
    <manual>Issue detail notification subscription behavior is still available if it was available before Phase 3.</manual>
  </verify>
  <acceptance_criteria>
    - No visible billing, pricing, upgrade, talk-to-sales, Plane One, Plane Pro, Business, or Enterprise CTA appears in the checked web app paths.
    - Removed entry points are absent rather than blank.
    - Core CE PM surfaces checked in this task still render.
  </acceptance_criteria>
  <done>Manual smoke confirms the de-monetized UI has no obvious broken or dangling surfaces.</done>
</task>

</tasks>

<verification>
Primary automated gates:
- `pnpm build`
- `pnpm check:types`
- `pnpm check:lint`
- Source residual greps listed in Task 8 and `03-VALIDATION.md`

Manual gates:

- Sidebar/settings/member/action paths contain no billing or upgrade entry point.
- Edition badge is version-only.
- Removed absent-code stubs leave no blank pages.
- Issue notification subscriptions are preserved.
  </verification>
