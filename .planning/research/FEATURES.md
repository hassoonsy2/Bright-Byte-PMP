# Feature Research

**Domain:** White-label rebrand + de-monetization of the Plane (Community Edition) monorepo into "Bright-Byte PMP"
**Researched:** 2026-06-01
**Confidence:** HIGH (grounded in direct reads of the repo; every surface below cites a real path)

> Scope note: This is a **brownfield rebrand/de-monetization** milestone. Plane's PM features are inherited as-is and are **not** re-researched here. The "features" in this document are the *change surfaces* of the rebrand: BRAND, BILLING/LICENSE removal, EE/Pro ungating, and the AI-assistant rename. Categories map to:
> - **Table Stakes** = must do for a credible white-label (the brand would be "obviously Plane" without it)
> - **Differentiators / nice-to-have** = polish that improves the white-label but isn't strictly required
> - **Anti-Features** = surfaces we deliberately do **not** touch, with reasons

---

## Key Mechanism Finding: How CE Gates Pro/EE Features

This single finding governs the entire "unlock all features" workstream, so it leads.

**There is no runtime license enforcement in CE.** Searches for `useFlag`, `FeatureFlag`, `getFeatureFlag`, `E_FEATURE_FLAGS`, `WithFeatureFlagHOC` returned **zero hits** in `apps/web/core` and `apps/web/ce`. The CE store directory (`apps/web/ce/store/`) has **no** feature-flag or subscription store. Gating is implemented in **three** lighter-weight ways, all UI-only:

1. **CE no-op / empty implementations behind the `@/plane-web/*` alias.** Pro behavior is swapped out by the edition seam (`@/plane-web/*` → `./ce/*` per `apps/web/tsconfig.json`). Examples:
   - `apps/web/ce/components/common/subscription/subscription-pill.tsx` — returns `<></>` (empty).
   - `apps/web/ce/store/workspace/index.ts` — `mutateWorkspaceMembersActivity` is a documented `// No-op in default/CE version`.
   The CE build already *behaves as if unlicensed*; EE swaps these for real implementations. **Most "Pro" PM features that ship in CE are already fully functional** (e.g., cycles, modules, pages, real-time collab via `apps/live`). The "locked" experience is mostly upsell chrome, not disabled functionality.

2. **Hard-coded upsell prompts in core components.** Some CE components render an "Upgrade" call-to-action instead of (or alongside) the feature. Representative:
   - `apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx` — a sticky "Upgrade to One" banner linking to `MARKETING_PLANE_ONE_PAGE_LINK`.
   - `apps/web/core/components/license/modal/card/plan-upgrade.tsx`, `.../checkout-button.tsx`, `.../talk-to-sales.tsx` — the paid-plan cards.

3. **The "Community" edition badge → upgrade modal.** `apps/web/ce/components/workspace/edition-badge.tsx` renders a sidebar button labeled "Community" that opens `PaidPlanUpgradeModal` (`apps/web/ce/components/license/modal/upgrade-modal.tsx`), which renders Pro/Business/Enterprise cards whose checkout buttons `window.open(...)` to `plane.so` upgrade/talk-to-sales URLs.

**Implication for "unlock all features":** The bulk of the work is **deleting upsell UI**, not flipping license flags. Where a feature is genuinely EE-only (lives in an `ee/` directory we don't have), it is simply **absent** from CE — "unlocking" it would require porting EE code we don't possess, which is **out of scope** (PROJECT.md inherits "Plane's feature set as-is"). So "unlock all features" concretely means: **remove the upsell surfaces and let CE's already-working features stand unobstructed.** Confidence: HIGH.

---

## Feature Landscape

### Table Stakes (Must Do for a Credible White-Label)

| Feature (change surface) | Why Expected | Complexity | Notes / Real Paths |
|---|---|---|---|
| **App title + metadata (web)** | First thing in the browser tab / OG preview; "Plane \| ..." is an instant tell | LOW | `apps/web/app/root.tsx` (`APP_TITLE` L36, `og:title`/`og:description`/`og:url`/`og:image:alt` L97-120, `application-name` "Plane" L67, `twitter:site` "@planepowers" L115). Drives `SITE_NAME`/`SITE_DESCRIPTION` from `@plane/constants`. |
| **Brand constants package** | Central source of `SITE_NAME`, `SITE_TITLE`, `SITE_DESCRIPTION`, `SITE_URL`, `TWITTER_USER_NAME`, plus space-site equivalents | LOW | `packages/constants/src/metadata.ts` (8 brand strings, all literally "Plane"). Also `packages/constants/src/endpoints.ts`: `WEBSITE_URL`, `SUPPORT_EMAIL` (`support@plane.so`), `MARKETING_*` links. Env-overridable for some (`VITE_WEBSITE_URL`, `VITE_SUPPORT_EMAIL`). |
| **PWA manifest(s)** | Installed-app name/icon; "Plane" shows on home screen | LOW | `apps/web/manifest.json` (`name`, `short_name`, `description` all "Plane"; theme `#3579f6`); `apps/web/public/manifest.json`; `apps/web/public/site.webmanifest.json`; `apps/admin/public/site.webmanifest.json`; `apps/space/public/site.webmanifest.json`; `apps/space/app/assets/favicon/site.webmanifest`. |
| **Favicons + app icons + PWA icons** | Visual brand in tab, install, Apple touch | MEDIUM | `apps/web/app/assets/favicon/{favicon-16x16,favicon-32x32,favicon.ico}`; `apps/web/app/assets/icons/{icon-180x180,icon-512x512}.png`; `apps/web/public/icons/icon-{192,348,512}.png`; `apps/web/public/favicon/android-chrome-{192,512}.png`; OG image `apps/web/app/assets/og-image.png`. Client supplies assets (PROJECT.md). Complexity is asset prep + every-size coverage, not code. |
| **Logo assets + logo components** | The Plane logo appears in sidebar, auth, spinners, space | MEDIUM | `apps/web/app/assets/plane-logos/*` (horizontal/blue variants); `apps/web/public/plane-logos/plane-mobile-pwa.png`; `apps/web/app/assets/plane-takeoff.png`; auth `apps/web/app/assets/auth/gradient-logo.webp`; spinners `apps/web/app/assets/images/logo-spinner-{light,dark}.gif` (`apps/web/core/components/common/logo-spinner`); brand icon component `packages/propel/src/icons/brand/plane-logo.tsx`. |
| **i18n locale strings (English, canonical)** | "Plane" is baked into translatable UI copy (settings, tour, navigation, AI labels) | MEDIUM | `packages/i18n/src/locales/en/*` — ~130 "Plane" occurrences across `common.json`, `navigation.json`, `workspace-settings.json`, `tour.json`, etc. English is the source of truth. |
| **Admin app brand** | God-mode/admin panel title still says "Plane" | LOW | `apps/admin/app/root.tsx` (`APP_TITLE` L24); `apps/admin/public/site.webmanifest.json`. |
| **Space (Sites) app brand** | Public published boards carry "Plane Publish" branding visible to external viewers | LOW-MEDIUM | `apps/space/app/root.tsx` (`APP_TITLE` L27, `APP_DESCRIPTION` L28); `packages/constants/src/metadata.ts` (`SPACE_SITE_*`, `SPACE_TWITTER_USER_NAME`). External-facing → higher visibility. |
| **Email templates (backend)** | Invites, magic-link, password reset, notifications all branded "Plane" | MEDIUM | `apps/api/templates/base.html` + `apps/api/templates/emails/**` (auth/forgot_password, auth/magic_signin, invitations/workspace_invitation, invitations/project_invitation, notifications/*, user/*, exports/analytics, test_email). ~10+ templates reference "Plane". Server-side, separate from frontend. |
| **Remove license upsell modal cluster** | "Upgrade / Talk to Sales / checkout" is the loudest monetization tell | MEDIUM | Delete/neutralize `apps/web/core/components/license/**` (9 files: `modal/index.ts`, `modal/card/{base-paid-plan-card,plan-upgrade,checkout-button,talk-to-sales,discount-info,free-plan,index}.tsx`, `index.ts`) and CE wrapper `apps/web/ce/components/license/**` (`upgrade-modal.tsx`, `modal/index.ts`, `index.ts`). |
| **Remove the "Community" edition badge → upgrade trigger** | Sidebar button that opens the upgrade modal | LOW | `apps/web/ce/components/workspace/edition-badge.tsx` (`WorkspaceEditionBadge` renders `PaidPlanUpgradeModal` + "Community" button). Replace with a no-op/version-only badge or remove. |
| **Remove workspace billing settings page + route** | A whole "Billing & Plans" settings screen | MEDIUM | `apps/web/ce/components/workspace/billing/**` (`root.tsx` = `BillingRoot`, `billing-actions-button.tsx`, `comparison/{root,plan-detail,frequency-toggle}.tsx`, `index.ts`); core comparison `apps/web/core/components/workspace/billing/comparison/{base,feature-detail,index}.tsx`; route + page `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/(workspace)/billing/{page,header}.tsx`; route registration in `apps/web/app/routes/core.ts`; nav entry in settings sidebar. |
| **Remove plan/pricing data** | The 1,311-line plan comparison matrix | MEDIUM | `apps/web/core/constants/plans.tsx` (`PLANS_LIST`, `PLANS_COMPARISON_LIST`, `PLANE_PLANS` with prices/CTAs). Plus `@plane/constants`: `packages/constants/src/payment.ts` (`PLANE_COMMUNITY_PRODUCTS`, `TALK_TO_SALES_URL`, `SUBSCRIPTION_REDIRECTION_URLS`, `SUBSCRIPTION_WEBPAGE_URLS`) and `packages/constants/src/subscription.ts` (`*_PLAN_FEATURES`). |
| **Remove in-component upsell banners/CTAs** | "Upgrade to One/Pro" prompts scattered in feature UIs | MEDIUM | e.g. `apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx`. Find all via `MARKETING_PLANE_ONE_PAGE_LINK` / `MARKETING_PRICING_PAGE_LINK` / `SUBSCRIPTION_*` references and the upgrade-modal trigger in `apps/web/core/store/issue/issue-details/root.store.ts` and `apps/web/core/components/issues/peek-overview/view.tsx`. |
| **Rename AI assistant labels to "Byte"** | Brand coherence ("Bright-**Byte**"); strings currently say "Pi" / "Plane AI" | MEDIUM | See AI section below. Canonical strings: `apps/web/core/constants/ai.ts` ("Pi is generating response"); locale `pi_chat`: "Plane AI" in `packages/i18n/src/locales/*/{common,navigation,workspace-settings,tour}.json` (all 19 languages); icon `PiChatLogo` (`packages/propel/src/icons/sub-brand/pi-chat.tsx`, used in `apps/web/core/components/workspace/sidebar/user-menu.tsx`); popover `apps/web/core/components/core/modals/gpt-assistant-popover.tsx` (placeholders "Ask AI anything...", "Generate response"). |

### Differentiators / Nice-to-Have

| Feature (change surface) | Value Proposition | Complexity | Notes / Real Paths |
|---|---|---|---|
| **All 19 non-English locales rebranded** | Avoids a "Plane" leak for any client who switches language; consistent polish | MEDIUM | `packages/i18n/src/locales/{cs,de,es,fr,id,it,ja,ko,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/*`. English is table-stakes; the other 18 are nice-to-have (mechanical find/replace of "Plane"/"Plane AI", but high volume). |
| **Component / variable rename ("Pi"→"Byte" in code)** | Maintainability; future devs see "Byte" not "Pi" | MEDIUM | `PiChatLogo` component, `sub-brand.pi-chat` icon registry key (`packages/propel/src/icons/registry.ts`, `constants.tsx`), `pi_chat` i18n key, `GptAssistantPopover` naming. Internal — not user-visible, so optional for the *brand* but cheap to fold into the rename pass. |
| **Theme color / brand color** | Subtle but real Plane tell (`#3579f6` blue) | LOW | `apps/web/manifest.json` (`theme_color`), `apps/web/app/root.tsx` meta `theme-color`. Coordinate with the broader Tailwind theme (`packages/tailwind-config`) if a full color rebrand is wanted. |
| **Replace upgrade modal with neutral "all features included" affordance** | Turns a removed surface into a positive brand signal instead of a hole | LOW | After removing `PaidPlanUpgradeModal`, optionally repurpose `edition-badge.tsx` into a plain version badge. |
| **Marketing/support link redirection via env** | Point `WEBSITE_URL`/`SUPPORT_EMAIL` at Bright-Byte without code edits | LOW | `packages/constants/src/endpoints.ts` already reads `VITE_WEBSITE_URL` / `VITE_SUPPORT_EMAIL`; set in Render env. The hard-coded `MARKETING_*` and `plane.so` URLs are *not* env-driven and need code edits if referenced post-removal. |

### Anti-Features (Deliberately NOT Touched)

| Surface | Why It Looks In-Scope | Why NOT to Touch | What to Do Instead |
|---|---|---|---|
| **Issue / notification "subscriptions"** | Contains the word "subscribe" | It is the **notify-me-on-this-work-item** feature, unrelated to billing (PROJECT.md "Out of Scope" + "Validated"). Files like `apps/web/ce/components/workspace-notifications/*` and any `*subscriber*`/`subscribe` issue code are core PM. | Leave fully intact. Filter billing searches to `payment`/`plan`/`checkout`/`license`/`upgrade`, not the bare word "subscription". Note the naming collision: `packages/constants/src/subscription.ts` IS billing (plan features); issue-subscription code is NOT. |
| **AGPL copyright headers** | They literally say "Plane Software, Inc." | AGPL-3.0 requires attribution; `copyright-check.yml` CI enforces the header via `addlicense` (CONVENTIONS.md). Removing/altering them breaks CI and violates the license. | Keep every `Copyright (c) 2023-present Plane Software, Inc.` / `SPDX-License-Identifier: AGPL-3.0-only` header verbatim. The user-facing brand and the source attribution are distinct. |
| **Internal `@plane/*` package scope** (this milestone) | "Plane" appears in 19 `package.json` + ~1,274 files | The `@plane/*` → `@bright-byte/*` deep rename is a **separate, high-risk workstream** (PROJECT.md) touching build tooling, `pnpm-workspace.yaml`, `turbo.json`, tsconfig path aliases. It is not user-facing brand. | Treat as its own phase. The user-facing rebrand can ship independently of the package-scope rename. |
| **`@/plane-web/*` alias name** | Contains "plane" | It is the CE/EE edition seam (`tsconfig.json` `@/plane-web/*` → `./ce/*`); renaming it is invasive, build-affecting, and invisible to users. | Leave as-is, or fold into the package-rename phase — never into the user-facing brand phase. |
| **Porting real EE-only features into CE** | "Unlock all features" sounds like enabling Enterprise capabilities | EE-only features live in an `ee/` directory the CE checkout does **not** contain; there is nothing to "unlock." PROJECT.md: inherit "Plane's feature set as-is." | "Unlock" = remove upsell chrome so CE's already-working features stand free. Do not attempt to author EE features. |
| **3rd-party AI provider / GPT backend wiring** | The assistant is being renamed to "Byte" | The rename is **label-only**. The backend (`apps/api/plane/app/views/external/base.py`, `createGptTask`, OpenAI config in `apps/api/plane/utils/instance_config_variables/core.py`) is functional and out of scope to re-engineer. | Change display strings/icons only; leave the AI service contract and provider config untouched (still admin-configurable). |
| **License instance app (`apps/api/plane/license/`)** | Named "license" | This is the **instance-registration / God-mode** machinery (the self-hosted instance admin), not paid-plan billing. Removing it risks breaking instance bootstrap/admin. | Leave intact unless a concrete instance-activation upsell screen surfaces; verify before touching. |

---

## Feature Dependencies

```
BRAND constants (packages/constants/src/metadata.ts, endpoints.ts)
    └──feeds──> Web/Admin/Space metadata (root.tsx APP_TITLE, meta tags)
    └──feeds──> Email templates (apps/api/templates/**)

BILLING/LICENSE removal
    ├──requires──> Remove route + page first (settings/.../billing/page.tsx, routes/core.ts)
    │                  └──then──> delete BillingRoot + comparison components safely
    ├──requires──> Remove edition-badge trigger (ce/.../edition-badge.tsx)
    │                  └──before──> deleting PaidPlanUpgradeModal (license/modal/upgrade-modal.tsx)
    └──requires──> Remove in-component upsell banners (bulk-operations/upgrade-banner.tsx, etc.)
                       └──then──> safe to delete plans.tsx + payment.ts/subscription.ts constants

AI rename ("Pi"/"Plane AI" → "Byte")
    └──spans──> ai.ts string + i18n pi_chat key (all 19 locales) + PiChatLogo icon + popover labels
    └──independent of──> BRAND and BILLING workstreams (can run in parallel)

@plane/* package-scope rename  (SEPARATE MILESTONE — not this scope)
    └──conflicts-with──> doing it in the same pass as user-facing brand (different risk profile)
```

### Dependency Notes

- **Billing route removal must precede component deletion.** If you delete `BillingRoot` while `routes/core.ts` still references the billing `page.tsx`, the build breaks. Remove the route registration + page module, *then* the components, *then* the constants. Order: route/page → components (`license/**`, `workspace/billing/**`) → edition badge → in-component banners → `plans.tsx`/`payment.ts`/`subscription.ts`.
- **Edition badge must be neutralized before deleting the modal it imports.** `edition-badge.tsx` imports `PaidPlanUpgradeModal` from `../license`; deleting the modal first breaks the badge.
- **Brand constants are upstream of three apps + emails.** Edit `packages/constants/src/metadata.ts` once; web/admin/space pick it up via `SITE_NAME`/`SITE_DESCRIPTION`. But the hard-coded `APP_TITLE` literals in each `root.tsx` are *separate* and must each be edited.
- **AI rename is parallelizable.** It touches no billing or routing code; it can be its own phase or folded into the brand-strings phase.
- **Anti-feature: keep the package rename out of the user-facing brand phase.** Different blast radius (build tooling vs. strings/assets); mixing them makes the brand phase un-shippable until the risky rename lands.

---

## MVP Definition

### Launch With (v1 — credible white-label, no monetization visible)

- [ ] **Web brand metadata** — `apps/web/app/root.tsx` `APP_TITLE`/OG/twitter/application-name; `packages/constants/src/metadata.ts` + `endpoints.ts` — *the obvious tells*
- [ ] **Favicons + app icons + PWA icons + logos swapped** — `apps/web/app/assets/{favicon,icons,plane-logos}`, `apps/web/public/{icons,favicon,plane-logos}`, OG image, `propel/.../brand/plane-logo.tsx`, spinners — *client-provided assets*
- [ ] **PWA manifests** — `apps/web/manifest.json` + `public/manifest.json` + `site.webmanifest.json` (web/admin/space)
- [ ] **English locale rebrand** — `packages/i18n/src/locales/en/*` (~130 "Plane")
- [ ] **Email templates rebrand** — `apps/api/templates/**` (invites/auth/notifications are user-facing and external)
- [ ] **Admin + Space app brand** — `apps/admin/app/root.tsx`, `apps/space/app/root.tsx`, their manifests
- [ ] **Remove all billing/license upsell** — `license/**`, `ce/.../license/**`, `workspace/billing/**` (core + ce), billing route + page, edition badge trigger, in-component upgrade banners, `plans.tsx` + `payment.ts`/`subscription.ts`
- [ ] **AI assistant → "Byte"** — `ai.ts`, `pi_chat` key (at minimum `en`), popover labels, `PiChatLogo` usage in `user-menu.tsx`

### Add After Validation (v1.x)

- [ ] **Non-English locales rebrand** — remaining 18 locale dirs (`packages/i18n/src/locales/*`) — *trigger: a client uses a non-English language*
- [ ] **Internal "Pi" → "Byte" code rename** — `PiChatLogo` component, `sub-brand.pi-chat` registry key, `pi_chat` i18n key, `GptAssistantPopover` naming — *trigger: developer-facing consistency cleanup*
- [ ] **Theme/brand color** — `theme_color` / `theme-color` meta and Tailwind theme — *trigger: client wants full color identity*

### Future Consideration (v2+ / separate milestone)

- [ ] **`@plane/*` → `@bright-byte/*` deep package rename** — *defer: high-risk, build-tooling-wide, not user-facing (PROJECT.md treats as its own workstream)*

---

## Feature Prioritization Matrix

| Feature (change surface) | User Value | Implementation Cost | Priority |
|---|---|---|---|
| Web brand metadata + constants | HIGH | LOW | P1 |
| Remove license/billing upsell + plans data | HIGH | MEDIUM | P1 |
| Favicons / icons / logos swap | HIGH | MEDIUM | P1 |
| English locale rebrand | HIGH | MEDIUM | P1 |
| Email templates rebrand | HIGH | MEDIUM | P1 |
| AI assistant → "Byte" (user-visible labels) | HIGH | MEDIUM | P1 |
| Admin + Space app brand | MEDIUM | LOW | P1 |
| PWA manifests | MEDIUM | LOW | P1 |
| Non-English locales rebrand | MEDIUM | MEDIUM | P2 |
| Internal "Pi"→"Byte" code rename | LOW | MEDIUM | P2 |
| Theme/brand color | MEDIUM | LOW | P2/P3 |
| `@plane/*` package-scope rename | LOW (user) / HIGH (maintainer) | HIGH | P3 (separate milestone) |

**Priority key:** P1 = must have for launch · P2 = should have, add when possible · P3 = defer.

---

## Competitor Feature Analysis

Not applicable in the conventional sense — this is a **white-label of one upstream product (Plane CE)**, not a net-new product competing in a market. The relevant comparison is **Plane CE (upstream) vs. Bright-Byte PMP (our fork)**:

| Surface | Plane CE (upstream) | Bright-Byte PMP (our approach) |
|---|---|---|
| Brand identity | "Plane", blue `#3579f6`, plane logos | Bright-Byte PMP brand, client-supplied assets |
| Monetization UI | Upgrade modal, billing settings, plan comparison, "Talk to Sales" | All removed; no payment surfaces |
| Pro/EE features | CE features functional; upsell chrome points at paid tiers | Same CE features, upsell chrome removed (no EE porting) |
| AI assistant | "Pi" / "Plane AI" (PiChat) | "Byte" (labels/icons only; same backend) |
| License attribution | AGPL headers, "Plane Software, Inc." | **Unchanged** (AGPL compliance) |

---

## Sources

- Direct reads of the Bright-Byte-PMP repo (HIGH confidence), notably:
  - `apps/web/app/root.tsx`, `apps/web/manifest.json`, `apps/admin/app/root.tsx`, `apps/space/app/root.tsx`
  - `packages/constants/src/{metadata.ts,endpoints.ts,payment.ts,subscription.ts}`
  - `apps/web/core/constants/plans.tsx`, `apps/web/core/constants/ai.ts`
  - `apps/web/core/components/license/**`, `apps/web/ce/components/license/**`
  - `apps/web/core/components/workspace/billing/**`, `apps/web/ce/components/workspace/billing/**`
  - `apps/web/ce/components/workspace/edition-badge.tsx`, `apps/web/ce/components/common/subscription/subscription-pill.tsx`, `apps/web/ce/store/workspace/index.ts`
  - `apps/web/core/components/core/modals/gpt-assistant-popover.tsx`, `apps/web/core/components/issues/bulk-operations/upgrade-banner.tsx`
  - `packages/i18n/src/locales/**`, `packages/propel/src/icons/sub-brand/pi-chat.tsx`, `apps/api/templates/**`
  - Negative searches (HIGH-confidence absence): `useFlag`/`FeatureFlag`/`getFeatureFlag`/`E_FEATURE_FLAGS`/`WithFeatureFlagHOC` returned **zero** hits in `apps/web/core` and `apps/web/ce`.
- Project context: `.planning/PROJECT.md`, `.planning/codebase/{STRUCTURE,ARCHITECTURE,CONVENTIONS}.md`

---
*Feature research for: white-label rebrand + de-monetization of Plane CE → Bright-Byte PMP*
*Researched: 2026-06-01*
