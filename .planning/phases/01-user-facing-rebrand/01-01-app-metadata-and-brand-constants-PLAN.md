---
phase: 01-user-facing-rebrand
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - packages/constants/src/metadata.ts
  - packages/constants/src/endpoints.ts
  - apps/web/app/root.tsx
  - apps/admin/app/root.tsx
  - apps/space/app/root.tsx
  - .env.example
  - apps/web/core/components/account/auth-forms/auth-header.tsx
  - apps/web/core/components/core/page-title.tsx
  - apps/web/core/components/auth-screens/header.tsx
  - apps/web/core/components/auth-screens/footer.tsx
  - apps/web/core/components/instance/not-ready-view.tsx
  - apps/web/core/components/onboarding/steps/role/root.tsx
  - apps/web/core/components/onboarding/steps/profile/root.tsx
  - apps/web/core/components/onboarding/steps/profile/consent.tsx
  - apps/web/core/components/onboarding/steps/usecase/root.tsx
  - apps/web/core/components/onboarding/steps/team/root.tsx
  - apps/web/core/components/onboarding/invite-members.tsx
  - apps/web/core/layouts/auth-layout/workspace-wrapper.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/page.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/github/form.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/github/page.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/gitlab/form.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/gitlab/page.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/google/form.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/google/page.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/gitea/form.tsx
  - apps/admin/app/(all)/(dashboard)/authentication/gitea/page.tsx
  - apps/admin/app/(all)/(dashboard)/ai/form.tsx
  - apps/admin/app/(all)/(dashboard)/ai/page.tsx
  - apps/space/components/account/auth-forms/auth-header.tsx
  - apps/space/lib/instance-provider.tsx
  - apps/space/components/instance/instance-failure-view.tsx
autonomous: false
requirements: [BRAND-01, BRAND-02, BRAND-06, BRAND-07]
must_haves:
  truths:
    - "The browser tab, OG/twitter preview, and meta tags on the web app read 'Bright-Byte PMP', not 'Plane'"
    - "The admin app browser tab and meta read 'Bright-Byte PMP', not 'Plane'"
    - "The public space (Sites) app browser tab and meta read 'Bright-Byte PMP', not 'Plane Publish'"
    - "Brand constants in @plane/constants resolve to Bright-Byte values consumed by all three apps"
    - "WEBSITE_URL and SUPPORT_EMAIL are env-driven (VITE_*) and documented in .env.example"
    - "Hardcoded user-visible 'Plane' string literals in web auth/onboarding/instance .tsx, admin authentication/ai pages, and space auth/instance components read 'Bright-Byte PMP'/'Byte' (these are i18n-independent and would otherwise leak on the browser tab and auth screen)"
  artifacts:
    - path: "packages/constants/src/metadata.ts"
      provides: "Central SITE_NAME/SITE_TITLE/SITE_DESCRIPTION/SITE_URL + SPACE_SITE_* + TWITTER_USER_NAME brand strings"
      contains: "Bright-Byte PMP"
    - path: "packages/constants/src/endpoints.ts"
      provides: "Env-driven WEBSITE_URL and SUPPORT_EMAIL"
      contains: "VITE_WEBSITE_URL"
    - path: "apps/web/app/root.tsx"
      provides: "Web APP_TITLE + application-name + OG/twitter meta"
      contains: "Bright-Byte PMP"
    - path: "apps/admin/app/root.tsx"
      provides: "Admin APP_TITLE + meta"
      contains: "Bright-Byte PMP"
    - path: "apps/space/app/root.tsx"
      provides: "Space APP_TITLE + APP_DESCRIPTION + meta"
      contains: "Bright-Byte PMP"
    - path: "apps/web/core/components/core/page-title.tsx"
      provides: "document.title fallback (was 'Plane | ...') — now Bright-Byte"
      contains: "Bright-Byte PMP"
    - path: "apps/web/core/components/account/auth-forms/auth-header.tsx"
      provides: "Auth-screen subheaders (Welcome back / Create your account)"
      contains: "Bright-Byte PMP"
  key_links:
    - from: "apps/web/app/root.tsx"
      to: "packages/constants/src/metadata.ts"
      via: "import { SITE_DESCRIPTION, SITE_NAME } from @plane/constants"
      pattern: "from \"@plane/constants\""
---

<objective>
Rebrand all user-visible application metadata and the central brand-constants package so the browser tab, social/OG preview, PWA name source, and meta tags on the web, admin, and space apps read "Bright-Byte PMP" instead of "Plane"/"Plane Publish". Make the website URL and support email env-driven (they are undecided) and document them in `.env.example`. ALSO rebrand the hardcoded, i18n-independent "Plane" string literals baked directly into web auth/onboarding/instance components, the admin authentication/ai config pages, and the space auth/instance components — these do NOT live in the i18n JSON (so Plans 01-04/01-05 cannot reach them) and would otherwise leak "Plane" on the browser tab and auth screen.

Purpose: The page `<title>`, OG preview, and `application-name` are the most immediate "this is Plane" tells. They are the first thing a human sees in a tab or a shared link. The hardcoded component literals (e.g. "Welcome back to Plane.", document.title fallback, "Welcome to Plane", "set up Plane", admin "Authentication Settings - Plane Web", "Plane AI features") are equally user-visible but live in `.tsx`/`.ts` source, not in any locale file.
Output: Updated `metadata.ts`, `endpoints.ts`, three `root.tsx` files, `.env.example`, and the enumerated web/admin/space component files with their hardcoded brand literals rebranded.
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
@.planning/codebase/CONVENTIONS.md

<interfaces>
<!-- Exact current values extracted from the codebase. Executor uses these directly. -->

packages/constants/src/metadata.ts (current literals to replace):
- L7  SITE_NAME = "Plane | Simple, extensible, open-source project management tool."
- L8  SITE_TITLE = "Plane | Simple, extensible, open-source project management tool."
- L9  SITE_DESCRIPTION = (Plane marketing description)
- L13 SITE_URL = "https://app.plane.so/"
- L14 TWITTER_USER_NAME = "Plane | Simple, extensible, open-source project management tool."
- L17 SPACE_SITE_NAME = "Plane Publish | Make your Plane boards and roadmaps pubic with just one-click. "
- L18 SPACE_SITE_TITLE = "Plane Publish | Make your Plane boards public with one-click"
- L19 SPACE_SITE_DESCRIPTION = "Plane Publish is a customer feedback management tool built on top of plane.so"
- L20 SPACE_SITE_KEYWORDS = (keywords)
- L22 SPACE_SITE_URL = "https://app.plane.so/"
- L23 SPACE_TWITTER_USER_NAME = "planepowers"

packages/constants/src/endpoints.ts (current):
- L27 WEBSITE_URL = process.env.VITE_WEBSITE_URL || "https://plane.so"
- L29 SUPPORT_EMAIL = process.env.VITE_SUPPORT_EMAIL || "support@plane.so"
- L31-33 MARKETING_* links (https://plane.so/...) — leave for Phase 3 (billing/upsell removal); do NOT touch here.

apps/web/app/root.tsx (current): L36 APP_TITLE; L67 application-name "Plane"; L98 title; L100 og:title; L105 og:url "https://app.plane.so/"; L109 og:image:alt "Plane - Modern project management"; L115 twitter:site "@planepowers"; L120 twitter:image:alt. L13 imports SITE_NAME/SITE_DESCRIPTION from @plane/constants.

apps/admin/app/root.tsx (current): L24 APP_TITLE; L62 title; L64 og:title; L66 og:url "https://plane.so/"; L72 twitter:site "@planepowers".

apps/space/app/root.tsx (current): L27 APP_TITLE "Plane Publish | ..."; L28 APP_DESCRIPTION; L77 og:url "https://sites.plane.so/"; L83 twitter:site "@planepowers".

<!-- Hardcoded user-visible "Plane" string literals (i18n-independent; verified in the live codebase). These are .tsx/.ts source values, NOT locale JSON, so Plans 01-04/01-05 do NOT touch them. KEEP all import lines, code identifiers, i18n KEY strings (e.g. "auth.common.new_to_plane"), @plane/* paths, and component names — only string VALUE literals/JSX text/alt-text change. -->
WEB (apps/web):
- core/components/account/auth-forms/auth-header.tsx: subHeader "Welcome back to Plane." (×3) and "Create your Plane account." (×3) → "...to Bright-Byte PMP." / "Create your Bright-Byte PMP account."
- core/components/core/page-title.tsx: L19 document.title fallback `?? "Plane | Simple, extensible, open-source project management tool."` → "Bright-Byte PMP | ..." (a Bright-Byte fallback title with no "Plane").
- core/components/auth-screens/header.tsx: L73 `<PageHead title={pageTitle + " - Plane"} />` → " - Bright-Byte PMP". (DO NOT touch L20 `text: "auth.common.new_to_plane"` — that is an i18n KEY name, KEEP; its VALUE is rebranded in Plan 01-04's auth.json.)
- core/components/auth-screens/footer.tsx: L35 "Join 10,000+ teams building with Plane" → "...building with Bright-Byte PMP".
- core/components/instance/not-ready-view.tsx: L40 `alt="Plane Logo"` → `alt="Bright-Byte PMP Logo"`; L42 `<h1>Welcome to Plane</h1>` → "Welcome to Bright-Byte PMP". (The PlaneLockup/GradientLogo wordmark image is swapped in Plan 01-02 — here only the text + alt.)
- core/components/onboarding/steps/role/root.tsx: L95 "Let's set up Plane for how you work." → "...set up Bright-Byte PMP...".
- core/components/onboarding/steps/profile/root.tsx: L150 "This is how you will appear in Plane." → "...appear in Bright-Byte PMP."
- core/components/onboarding/steps/profile/consent.tsx: L26 "I agree to Plane marketing communications" → "...Bright-Byte PMP marketing communications".
- core/components/onboarding/steps/usecase/root.tsx: L89 "What brings you to Plane?" → "What brings you to Bright-Byte PMP?".
- core/components/onboarding/steps/team/root.tsx: L346 description "Work in plane happens best with your team. Invite them now to use Plane to its potential." → "Work in Bright-Byte PMP happens best ... use Bright-Byte PMP to its potential."
- core/components/onboarding/invite-members.tsx: L343 same sentence as team/root → rebrand both "plane"/"Plane" brand occurrences to "Bright-Byte PMP".
- core/layouts/auth-layout/workspace-wrapper.tsx: L174 `alt="Plane logo"` → `alt="Bright-Byte PMP logo"`. (KEEP L158 `<PlaneLogo .../>` — that is a component identifier, swapped in Plan 01-02.)
ADMIN (apps/admin/app/(all)/(dashboard)) — BRAND-06 page literals beyond root.tsx:
- authentication/page.tsx: L172 meta title "Authentication Settings - Plane Web" → "Authentication Settings - Bright-Byte PMP".
- authentication/{github,gitlab,google,gitea}/{form,page}.tsx: user-visible "Plane" brand strings in titles/descriptions (e.g. "...so users can log in to Plane with their <provider> account") → "Bright-Byte PMP". Grep each before editing; rebrand only brand text VALUES, never provider field keys/identifiers/callback-URL paths.
- ai/{form,page}.tsx: ai/page.tsx L29 "...so Plane AI features are turned on..." → "...so Byte features are turned on..." (the AI assistant is "Byte"); other "Plane" brand text in ai/form.tsx → "Bright-Byte PMP". (KEEP any provider identifier / config-key strings.)
SPACE (apps/space):
- components/account/auth-forms/auth-header.tsx: L30 "...to work with Plane work items and Pages." and L44 "Use plane to add your valuable inputs to features." → "Bright-Byte PMP".
- lib/instance-provider.tsx: L61 `alt="Plane background pattern"` → `alt="Bright-Byte PMP background pattern"`. (KEEP L29 `PlaneBackgroundPattern`/`PlaneBackgroundPatternDark` import identifiers.)
- components/instance/instance-failure-view.tsx: L26 `alt="Plane instance failure image"` → `alt="Bright-Byte PMP instance failure image"`.

<!-- OUT OF SCOPE for this task (do NOT edit here): -->
<!-- - apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx ("upgrade to Plane Pro", plane.so/pro) → Phase 3 billing/upsell removal. -->
<!-- - apps/admin/app/(all)/(dashboard)/general/form.tsx telemetry-consent text + developers.plane.so link → Phase 5 telemetry (SEC-03). -->
<!-- - Any string that is an i18n KEY (auth.common.new_to_plane), a code identifier (PlaneLogo, PlaneLockup, PlaneBackgroundPattern), @plane/* import path, or AGPL header → KEEP. -->
</interfaces>
</context>

<constraints>
- The display name is exactly "Bright-Byte PMP". The AI assistant is exactly "Byte".
- v1 keeps the existing brand color (#3579f6 / theme-color) — do NOT change any color value.
- NEVER edit the AGPL copyright header comment block at the top of any file (`Copyright (c) 2023-present Plane Software, Inc.` / `SPDX-License-Identifier`). It stays verbatim. You are editing string literals further down, never the header.
- Do NOT rename the `@plane/*` package scope or any import path — that is Phase 2. You import from `@plane/constants` exactly as today.
- Do NOT touch the MARKETING_* link constants in endpoints.ts (Phase 3).
- For the hardcoded component literals (Task 5): change only user-visible string VALUES / JSX text / `alt` attributes. NEVER change an i18n KEY (e.g. `"auth.common.new_to_plane"`), a code identifier (`PlaneLogo`, `PlaneLockup`, `PlaneBackgroundPattern`), an import path, a route/callback path, or a provider config key. Verify each hit is a brand reference before editing.
- The exact support email, website URL, and social handle are NOT decided yet — keep them env-driven and use safe neutral placeholders for the hard-coded `og:url`/`twitter:site` literals (see Task 3 checkpoint).
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Rebrand the central brand-constants package</name>
  <read_first>
    - packages/constants/src/metadata.ts (read the whole file: 8 SITE_* + SPACE_SITE_* + TWITTER constants)
    - packages/constants/src/endpoints.ts (lines around 27-33)
    - .planning/codebase/CONVENTIONS.md (CONSTANT_CASE, file-header rule)
  </read_first>
  <files>packages/constants/src/metadata.ts, packages/constants/src/endpoints.ts</files>
  <action>
    In metadata.ts, replace the Plane brand strings with Bright-Byte values (BRAND-02), preserving the `export const` names and types:
    - SITE_NAME and SITE_TITLE → "Bright-Byte PMP" (drop the Plane tagline; a short brand name is correct for these).
    - SITE_DESCRIPTION → a Bright-Byte project-management description (rewrite, removing the word "Plane").
    - TWITTER_USER_NAME → "Bright-Byte PMP".
    - SPACE_SITE_NAME → "Bright-Byte PMP" ; SPACE_SITE_TITLE → "Bright-Byte PMP" ; SPACE_SITE_DESCRIPTION → a Bright-Byte description with no "Plane"/"plane.so".
    - SPACE_SITE_KEYWORDS → remove any "plane" tokens.
    - SITE_URL, SPACE_SITE_URL, SPACE_TWITTER_USER_NAME → these are URL/handle values that are NOT yet decided; replace with the neutral placeholders agreed in Task 3 (do not invent a real domain). For SITE_URL/SPACE_SITE_URL use the value of WEBSITE_URL's env fallback so all three stay consistent.
    In endpoints.ts, change ONLY the hard-coded fallback literals (BRAND-02): keep `process.env.VITE_WEBSITE_URL || ...` and `process.env.VITE_SUPPORT_EMAIL || ...` structure, but replace the `https://plane.so` and `support@plane.so` fallbacks with the neutral placeholders from Task 3. Do NOT touch the MARKETING_* lines.
    Do not edit the AGPL header. Keep oxfmt formatting (printWidth 120, 2-space indent).
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -nv '^\s*\*' packages/constants/src/metadata.ts packages/constants/src/endpoints.ts | grep -iE "plane\.so|\"Plane|Plane Publish|planepowers|support@plane" && echo "FAIL: brand leak remains" || echo "PASS: no brand/plane.so leaks outside header"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -in "Bright-Byte PMP" packages/constants/src/metadata.ts` returns ≥4 hits (SITE_NAME, SITE_TITLE, SPACE_SITE_NAME, SPACE_SITE_TITLE).
    - No `plane.so`, `@planepowers`, `Plane Publish`, or standalone brand `Plane` string remains in either file outside the AGPL comment header.
    - The `export const` names, count, and `process.env.VITE_*` fallback structure in endpoints.ts are unchanged (only literal values changed); MARKETING_* lines are byte-identical to before.
  </acceptance_criteria>
  <done>metadata.ts and endpoints.ts carry Bright-Byte brand values; no Plane brand leaks outside AGPL headers; MARKETING_* untouched.</done>
</task>

<task type="auto">
  <name>Task 2: Rebrand web, admin, and space root.tsx metadata</name>
  <read_first>
    - apps/web/app/root.tsx (APP_TITLE L36, application-name L67, meta array L98-120)
    - apps/admin/app/root.tsx (APP_TITLE L24, meta L62-72)
    - apps/space/app/root.tsx (APP_TITLE L27, APP_DESCRIPTION L28, meta L73-83)
  </read_first>
  <files>apps/web/app/root.tsx, apps/admin/app/root.tsx, apps/space/app/root.tsx</files>
  <action>
    BRAND-01 (web): set APP_TITLE to "Bright-Byte PMP" (a clean brand title; drop the Plane tagline). Set the `application-name` meta content to "Bright-Byte PMP". In the meta array, replace `og:url` content (currently https://app.plane.so/), `og:image:alt` and `twitter:image:alt` (currently "Plane - Modern project management"), and `twitter:site` (currently "@planepowers") with Bright-Byte values — use the neutral placeholders from Task 3 for URL/handle. Leave the `theme-color`/color meta exactly as-is.
    BRAND-06 (admin): set APP_TITLE to "Bright-Byte PMP"; update og:url, twitter:site likewise.
    BRAND-07 (space): set APP_TITLE to "Bright-Byte PMP" (replace "Plane Publish | ..."); rewrite APP_DESCRIPTION to a Bright-Byte description containing no "Plane"/"plane.so"; update og:url (https://sites.plane.so/) and twitter:site.
    Do not change the `import { SITE_DESCRIPTION, SITE_NAME } from "@plane/constants"` line or any other import. Do not edit AGPL headers. Keep `apple-mobile-web-app-title` bound to `SITE_NAME` (it inherits the rebrand from Task 1).
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -nv '^\s*\*' apps/web/app/root.tsx apps/admin/app/root.tsx apps/space/app/root.tsx | grep -iE "plane\.so|planepowers|Plane Publish|content=\"Plane\"|\"Plane \| |Plane - Modern" && echo "FAIL: brand leak remains" || echo "PASS"</automated>
  </verify>
  <acceptance_criteria>
    - Each of the three root.tsx files contains "Bright-Byte PMP" in its APP_TITLE.
    - No `plane.so`, `@planepowers`, `Plane Publish`, `application-name content="Plane"`, or `Plane - Modern project management` string remains outside the AGPL header.
    - The `theme-color`/color meta value is unchanged in all three files.
    - The `@plane/constants` import statement in web/root.tsx is byte-identical to before.
  </acceptance_criteria>
  <done>All three apps render "Bright-Byte PMP" in tab title and meta; no Plane string leaks; color unchanged; imports untouched.</done>
</task>

<task type="checkpoint:decision" gate="blocking">
  <decision>Confirm the undecided brand URL, support email, and social handle (or approve neutral placeholders).</decision>
  <context>
    The exact website URL, support email, and social handle are not yet decided. The codebase reads `VITE_WEBSITE_URL` and `VITE_SUPPORT_EMAIL` from env (good — these can change without a code edit and will be set in Render later). But several values are hard-coded literals that need a concrete string now: `SITE_URL`, `SPACE_SITE_URL`, `og:url` in all three root.tsx, `twitter:site`, and the env fallbacks for `WEBSITE_URL`/`SUPPORT_EMAIL`. Tasks 1 and 2 used the neutral placeholders below pending your confirmation. We will NOT invent a real domain/email.
  </context>
  <options>
    <option id="placeholders">
      <name>Approve neutral placeholders (recommended for v1)</name>
      <pros>Unblocks the rebrand now; no fake domain shipped; real values land later via Render env (VITE_*) and a one-line constants edit.</pros>
      <cons>Placeholders are visible until the real domain/email/handle is decided.</cons>
      <detail>Proposed placeholders: website URL "https://bright-byte.example" (env-overridable via VITE_WEBSITE_URL); support email "support@bright-byte.example" (env-overridable via VITE_SUPPORT_EMAIL); social handle "@brightbyte". og:url/SITE_URL use the website URL value.</detail>
    </option>
    <option id="real-values">
      <name>Provide the real values now</name>
      <pros>Final values shipped immediately; no placeholder churn.</pros>
      <cons>Requires you to have decided the domain, support email, and handle.</cons>
      <detail>Provide: website URL, support email, social handle. Executor substitutes them into metadata.ts, endpoints.ts fallbacks, and the three root.tsx files, and records them in .env.example.</detail>
    </option>
  </options>
  <resume-signal>Reply "placeholders" to accept the neutral values, or paste the real website URL / support email / social handle.</resume-signal>
</task>

<task type="auto">
  <name>Task 4: Document brand env vars in .env.example</name>
  <read_first>
    - .env.example (root) — locate the existing VITE_* block; if no root .env.example exists, check apps/web/.env.example / setup.sh for where VITE_WEBSITE_URL / VITE_SUPPORT_EMAIL belong
    - packages/constants/src/endpoints.ts (to mirror the exact var names)
  </read_first>
  <files>.env.example</files>
  <action>
    Add (or update) documented entries for `VITE_WEBSITE_URL` and `VITE_SUPPORT_EMAIL` in `.env.example`, with the confirmed value from Task 3 as the example and a one-line comment that these drive the Bright-Byte brand website/support links and are baked at build time (VITE_* are build-time, per research). If a root `.env.example` does not exist, create it containing just these two documented vars plus a header comment pointing to where the full env set lives. Do not duplicate vars already present.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -c -E "VITE_WEBSITE_URL|VITE_SUPPORT_EMAIL" .env.example | grep -qE "^[2-9]" && echo "PASS: both vars documented" || echo "FAIL: missing env var docs"</automated>
  </verify>
  <acceptance_criteria>
    - `.env.example` documents both `VITE_WEBSITE_URL` and `VITE_SUPPORT_EMAIL` with the confirmed example value.
    - No real secret is committed (these are public brand URLs/emails, not secrets).
  </acceptance_criteria>
  <done>.env.example documents the two brand env vars so a deployer knows how to set the real website/support values without a code change.</done>
</task>

<task type="auto">
  <name>Task 5: Rebrand hardcoded user-visible "Plane" string literals in web/admin/space components</name>
  <read_first>
    - The <interfaces> "Hardcoded user-visible 'Plane' string literals" block above (the enumerated leak sites + their exact lines).
    - Each file before editing: re-grep it for "Plane" so you see every brand occurrence (the enumerated lines are confirmed, but re-grep to catch any sibling literal — the list is the floor, not the ceiling).
    - .planning/codebase/CONVENTIONS.md (file-header rule; never touch AGPL headers).
  </read_first>
  <files>apps/web/core/components/account/auth-forms/auth-header.tsx, apps/web/core/components/core/page-title.tsx, apps/web/core/components/auth-screens/header.tsx, apps/web/core/components/auth-screens/footer.tsx, apps/web/core/components/instance/not-ready-view.tsx, apps/web/core/components/onboarding/steps/role/root.tsx, apps/web/core/components/onboarding/steps/profile/root.tsx, apps/web/core/components/onboarding/steps/profile/consent.tsx, apps/web/core/components/onboarding/steps/usecase/root.tsx, apps/web/core/components/onboarding/steps/team/root.tsx, apps/web/core/components/onboarding/invite-members.tsx, apps/web/core/layouts/auth-layout/workspace-wrapper.tsx, apps/admin/app/(all)/(dashboard)/authentication/page.tsx, apps/admin/app/(all)/(dashboard)/authentication/github/form.tsx, apps/admin/app/(all)/(dashboard)/authentication/github/page.tsx, apps/admin/app/(all)/(dashboard)/authentication/gitlab/form.tsx, apps/admin/app/(all)/(dashboard)/authentication/gitlab/page.tsx, apps/admin/app/(all)/(dashboard)/authentication/google/form.tsx, apps/admin/app/(all)/(dashboard)/authentication/google/page.tsx, apps/admin/app/(all)/(dashboard)/authentication/gitea/form.tsx, apps/admin/app/(all)/(dashboard)/authentication/gitea/page.tsx, apps/admin/app/(all)/(dashboard)/ai/form.tsx, apps/admin/app/(all)/(dashboard)/ai/page.tsx, apps/space/components/account/auth-forms/auth-header.tsx, apps/space/lib/instance-provider.tsx, apps/space/components/instance/instance-failure-view.tsx</files>
  <action>
    BRAND-01 (web), BRAND-06 (admin), BRAND-07 (space): For each file listed, replace the user-visible "Plane" brand string VALUE / JSX text / `alt` attribute with "Bright-Byte PMP" (use "Byte" for the AI-assistant reference in admin/ai/page.tsx — "Plane AI" → "Byte"), exactly per the enumerated lines in <interfaces>. These literals are hardcoded in `.tsx`/`.ts` source and are i18n-independent, so the i18n plans (01-04/01-05) cannot reach them; this task closes that gap so the browser tab (page-title fallback), auth screen (subheaders, footer, "Welcome to Bright-Byte PMP", " - Bright-Byte PMP" page head), onboarding flow, and the admin authentication/ai pages no longer show "Plane".
    STRICT KEEP (do NOT edit): i18n KEY strings such as `"auth.common.new_to_plane"` (only the VALUE is rebranded in Plan 01-04); code identifiers `PlaneLogo`/`PlaneLockup`/`PlaneBackgroundPattern`; `@plane/*` import paths; provider config keys, callback/route paths, and field names in the admin auth forms; AGPL headers. The PlaneLockup/PlaneLogo/GradientLogo IMAGE swaps are Plan 01-02's job — here you only edit accompanying TEXT and `alt` attributes.
    OUT OF SCOPE (do NOT edit in this phase): the "upgrade to Plane Pro" upsell card (`apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx`) → Phase 3 billing/upsell; the telemetry-consent text + `developers.plane.so` link in `apps/admin/app/(all)/(dashboard)/general/form.tsx` → Phase 5 telemetry (SEC-03). Re-grep each edited file after editing to confirm no remaining user-visible brand "Plane" (excluding KEEP categories).
    Keep oxfmt formatting (printWidth 120, 2-space indent); preserve JSX structure, props, and any `{interpolation}` / i18n `t("...")` calls — change only literal brand text.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && rem=$(grep -rinE "Plane" \
      apps/web/core/components/account/auth-forms/auth-header.tsx \
      apps/web/core/components/core/page-title.tsx \
      apps/web/core/components/auth-screens/header.tsx \
      apps/web/core/components/auth-screens/footer.tsx \
      apps/web/core/components/instance/not-ready-view.tsx \
      apps/web/core/components/onboarding/steps/role/root.tsx \
      apps/web/core/components/onboarding/steps/profile/root.tsx \
      apps/web/core/components/onboarding/steps/profile/consent.tsx \
      apps/web/core/components/onboarding/steps/usecase/root.tsx \
      apps/web/core/components/onboarding/steps/team/root.tsx \
      apps/web/core/components/onboarding/invite-members.tsx \
      apps/web/core/layouts/auth-layout/workspace-wrapper.tsx \
      "apps/admin/app/(all)/(dashboard)/authentication/page.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/github/form.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/github/page.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/gitlab/form.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/gitlab/page.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/google/form.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/google/page.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/gitea/form.tsx" \
      "apps/admin/app/(all)/(dashboard)/authentication/gitea/page.tsx" \
      "apps/admin/app/(all)/(dashboard)/ai/form.tsx" \
      "apps/admin/app/(all)/(dashboard)/ai/page.tsx" \
      apps/space/components/account/auth-forms/auth-header.tsx \
      apps/space/lib/instance-provider.tsx \
      apps/space/components/instance/instance-failure-view.tsx \
      | grep -viE "Copyright \(c\) 2023-present Plane Software|SPDX-License-Identifier|@plane/|@/plane-web|@/plane-live|^[^:]+:[0-9]+:.*import |PlaneLogo|PlaneLockup|PlaneBackgroundPattern|auth\.common\.new_to_plane" \
      | wc -l | tr -d ' '); echo "Residual user-visible 'Plane' literal lines (excluding KEEP categories): $rem (want 0)"; [ "$rem" -eq 0 ] && echo "PASS: no hardcoded component brand leak" || echo "REVIEW: inspect remaining lines — each must be a KEEP identifier/import/i18n-key or a Phase-3/Phase-5 OUT-OF-SCOPE item (upgrade-card / general telemetry are NOT in this file set)"</automated>
  </verify>
  <acceptance_criteria>
    - The grep above returns 0 residual user-visible "Plane" brand literals across the 26 component files (after excluding AGPL headers, `@plane/*` imports, code identifiers, and the `auth.common.new_to_plane` i18n KEY).
    - `apps/web/core/components/core/page-title.tsx` document.title fallback contains "Bright-Byte PMP" and no "Plane".
    - `apps/web/core/components/account/auth-forms/auth-header.tsx` contains no "Welcome back to Plane." / "Create your Plane account." (now Bright-Byte PMP).
    - `apps/admin/.../authentication/page.tsx` meta title reads "Authentication Settings - Bright-Byte PMP"; `ai/page.tsx` references "Byte" (not "Plane AI").
    - No code identifier, import path, route/callback/provider-key, i18n KEY, or AGPL header was changed (verify with `git diff` — no `import`/identifier line modified).
    - The upgrade-card and admin general/telemetry files were NOT touched (they are not in files_modified; confirm `git status` shows no change to them).
  </acceptance_criteria>
  <done>Every hardcoded, i18n-independent user-visible "Plane" literal in the web auth/onboarding/instance components, admin authentication/ai pages, and space auth/instance components reads Bright-Byte/Byte; identifiers, imports, i18n keys, routes, and AGPL headers preserved; Phase-3/Phase-5 items left for their phases.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| build env → baked frontend | `VITE_*` values are baked into the static bundle at build time; a wrong/hostile value ships to every user. |
| meta tags → social/OG scrapers | OG/twitter URLs are rendered into HTML consumed by external link-preview crawlers. |
| component literal → rendered DOM/screen-reader | Hardcoded `.tsx` brand text and `alt` attributes render directly to the page and to assistive tech; a stale "Plane" literal is a visible white-label leak no env/i18n change can fix. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-01-01 | Tampering | og:url / SITE_URL pointing at an attacker-controlled or typo domain | mitigate | Use the human-confirmed value from the Task 3 checkpoint; never invent a domain. og:url is informational only (no token/redirect), so blast radius is brand-trust, not auth. |
| T-01-02 | Information Disclosure | .env.example | accept | File contains only public brand URLs/email examples, no secrets; real secrets go in Render env, never committed. |
| T-01-03 | Spoofing/Brand | hardcoded "Plane" component literals (auth/onboarding/admin/space) | mitigate | Task 5 rebrands every enumerated i18n-independent literal and asserts (grep) zero residual user-visible "Plane" outside KEEP categories, while strictly preserving identifiers/imports/i18n keys/routes/AGPL headers — closing the leak without breaking code. |
| T-01-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages (string-literal edits only). No supply-chain surface. |
</threat_model>

<verification>
- `pnpm --filter @plane/constants run check:types` (or repo-root `pnpm check:types`) passes — the constants edits did not break types consumed by the apps.
- Case-insensitive sweep of the edited metadata files for brand leaks outside AGPL headers returns clean (the grep gates in Tasks 1-2).
- Task 5 grep returns 0 residual user-visible "Plane" literals across the 26 component files (excluding KEEP categories); the web/admin/space apps type-check and build (`pnpm --filter web build` / admin / space) without errors introduced by the literal edits.
- AGPL headers in all edited source files are unchanged: `git diff -- <edited .ts/.tsx files> | grep -E '^[-+].*Copyright \(c\) 2023-present Plane Software'` returns nothing (no header lines added or removed).
</verification>

<success_criteria>
- Loading web, admin, and space apps shows "Bright-Byte PMP" in the browser tab and OG/social preview (no "Plane" title) — ROADMAP Phase 1 success criterion 1.
- The auth screen, onboarding flow, instance views, and admin authentication/ai pages show no hardcoded "Plane" text — success criteria 1 & 2.
- Brand constants are the single Bright-Byte source consumed by all three apps.
- Website URL and support email are env-driven and documented.
- AGPL headers untouched; brand color unchanged; code identifiers/imports/i18n keys/routes preserved for Phase 2.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-01-SUMMARY.md` when done.
</output>
</output>
