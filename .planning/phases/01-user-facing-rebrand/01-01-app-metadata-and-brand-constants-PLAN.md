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
autonomous: false
requirements: [BRAND-01, BRAND-02, BRAND-06, BRAND-07]
must_haves:
  truths:
    - "The browser tab, OG/twitter preview, and meta tags on the web app read 'Bright-Byte PMP', not 'Plane'"
    - "The admin app browser tab and meta read 'Bright-Byte PMP', not 'Plane'"
    - "The public space (Sites) app browser tab and meta read 'Bright-Byte PMP', not 'Plane Publish'"
    - "Brand constants in @plane/constants resolve to Bright-Byte values consumed by all three apps"
    - "WEBSITE_URL and SUPPORT_EMAIL are env-driven (VITE_*) and documented in .env.example"
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
  key_links:
    - from: "apps/web/app/root.tsx"
      to: "packages/constants/src/metadata.ts"
      via: "import { SITE_DESCRIPTION, SITE_NAME } from @plane/constants"
      pattern: "from \"@plane/constants\""
---

<objective>
Rebrand all user-visible application metadata and the central brand-constants package so the browser tab, social/OG preview, PWA name source, and meta tags on the web, admin, and space apps read "Bright-Byte PMP" instead of "Plane"/"Plane Publish". Make the website URL and support email env-driven (they are undecided) and document them in `.env.example`.

Purpose: The page `<title>`, OG preview, and `application-name` are the most immediate "this is Plane" tells. They are the first thing a human sees in a tab or a shared link.
Output: Updated `metadata.ts`, `endpoints.ts`, three `root.tsx` files, and `.env.example`.
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
</interfaces>
</context>

<constraints>
- The display name is exactly "Bright-Byte PMP".
- v1 keeps the existing brand color (#3579f6 / theme-color) — do NOT change any color value.
- NEVER edit the AGPL copyright header comment block at the top of any file (`Copyright (c) 2023-present Plane Software, Inc.` / `SPDX-License-Identifier`). It stays verbatim. You are editing string literals further down, never the header.
- Do NOT rename the `@plane/*` package scope or any import path — that is Phase 2. You import from `@plane/constants` exactly as today.
- Do NOT touch the MARKETING_* link constants in endpoints.ts (Phase 3).
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

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| build env → baked frontend | `VITE_*` values are baked into the static bundle at build time; a wrong/hostile value ships to every user. |
| meta tags → social/OG scrapers | OG/twitter URLs are rendered into HTML consumed by external link-preview crawlers. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-01-01 | Tampering | og:url / SITE_URL pointing at an attacker-controlled or typo domain | mitigate | Use the human-confirmed value from the Task 3 checkpoint; never invent a domain. og:url is informational only (no token/redirect), so blast radius is brand-trust, not auth. |
| T-01-02 | Information Disclosure | .env.example | accept | File contains only public brand URLs/email examples, no secrets; real secrets go in Render env, never committed. |
| T-01-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages (string-literal edits only). No install task, no supply-chain surface. |
</threat_model>

<verification>
- `pnpm --filter @plane/constants run check:types` (or repo-root `pnpm check:types`) passes — the constants edits did not break types consumed by the apps.
- Case-insensitive sweep of the six edited files for brand leaks outside AGPL headers returns clean (the grep gates in Tasks 1-2).
- AGPL headers in all edited files are unchanged: `git diff -- packages/constants/src/metadata.ts packages/constants/src/endpoints.ts apps/web/app/root.tsx apps/admin/app/root.tsx apps/space/app/root.tsx | grep -E '^[-+].*Copyright \(c\) 2023-present Plane Software'` returns nothing (no header lines added or removed).
</verification>

<success_criteria>
- Loading web, admin, and space apps shows "Bright-Byte PMP" in the browser tab and OG/social preview (no "Plane" title) — ROADMAP Phase 1 success criterion 1.
- Brand constants are the single Bright-Byte source consumed by all three apps.
- Website URL and support email are env-driven and documented.
- AGPL headers untouched; brand color unchanged.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-01-SUMMARY.md` when done.
</output>
