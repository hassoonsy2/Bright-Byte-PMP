---
phase: 01-user-facing-rebrand
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - apps/web/manifest.json
  - apps/web/public/manifest.json
  - apps/web/public/site.webmanifest.json
  - apps/admin/public/site.webmanifest.json
  - apps/space/public/site.webmanifest.json
  - packages/propel/src/icons/brand/plane-logo.tsx
  - apps/web/app/assets/favicon/favicon-16x16.png
  - apps/web/app/assets/favicon/favicon-32x32.png
  - apps/web/app/assets/favicon/favicon.ico
  - apps/web/app/assets/favicon/apple-touch-icon.png
  - apps/web/app/assets/icons/icon-180x180.png
  - apps/web/app/assets/icons/icon-512x512.png
  - apps/web/public/icons/icon-192x192.png
  - apps/web/public/icons/icon-348x348.png
  - apps/web/public/icons/icon-512x512.png
  - apps/web/public/favicon/android-chrome-192x192.png
  - apps/web/public/favicon/android-chrome-512x512.png
  - apps/web/app/assets/og-image.png
  - apps/web/app/assets/plane-logos/black-horizontal-with-blue-logo.png
  - apps/web/app/assets/plane-logos/white-horizontal-with-blue-logo.png
  - apps/web/app/assets/plane-logos/white-horizontal.svg
  - apps/web/app/assets/plane-logos/blue-without-text.png
  - apps/web/public/plane-logos/plane-mobile-pwa.png
  - apps/web/app/assets/auth/gradient-logo.webp
  - apps/web/app/assets/auth/gradient-bg-logo.webp
  - apps/web/app/assets/images/logo-spinner-light.gif
  - apps/web/app/assets/images/logo-spinner-dark.gif
autonomous: false
requirements: [BRAND-03, BRAND-04, BRAND-05]
must_haves:
  truths:
    - "The PWA install prompt and installed home-screen app name read 'Bright-Byte PMP' (no 'Plane' name)"
    - "The browser-tab favicon and Apple touch icon show the Bright-Byte mark"
    - "The sidebar/auth/spinner logo components render the Bright-Byte logo"
    - "The OG/social preview image shows the Bright-Byte brand"
  artifacts:
    - path: "apps/web/manifest.json"
      provides: "Primary PWA manifest name/short_name/description"
      contains: "Bright-Byte PMP"
    - path: "packages/propel/src/icons/brand/plane-logo.tsx"
      provides: "Shared brand logo SVG component (PlaneLogo) used across apps"
      contains: "export function PlaneLogo"
  key_links:
    - from: "apps/web/app/root.tsx"
      to: "apps/web/manifest.json"
      via: "manifest link / icon references"
      pattern: "manifest"
    - from: "apps/web/core/components/common/logo-spinner.tsx"
      to: "apps/web/app/assets/images/logo-spinner-*.gif"
      via: "import of spinner gif"
      pattern: "logo-spinner"
---

<objective>
Rebrand the installed-app identity: PWA manifests (web/admin/space), the favicon/app-icon/PWA-icon set, the OG image, the shared logo SVG component, and the logo/spinner image assets. All code-side wiring (manifest JSON strings, the SVG `PlaneLogo` component body, asset references) is done autonomously; the actual binary asset drop-in is blocked on client-supplied files and handled at a checkpoint.

Purpose: After metadata (Plan 01), the visible logo, favicon, and PWA icon are the next "this is Plane" tells — in the tab, the auth screen, spinners, and the home-screen install.
Output: Rebranded manifest JSON, an updated `plane-logo.tsx` SVG (Bright-Byte mark), and the client-provided binary assets dropped into their exact paths.
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
<!-- Manifest brand strings to replace (current values from the repo): -->
apps/web/manifest.json: L2 theme_color "#3579f6" (KEEP — v1 no color change); L7 name "Plane | Accelerate software development with peace."; L8 short_name "Plane"; L9 description "Plane accelerated the software development...".
apps/web/public/manifest.json: 2 "plane" hits (name/short_name/description block).
apps/web/public/site.webmanifest.json: 5 "plane" hits.
apps/admin/public/site.webmanifest.json: 3 "plane" hits.
apps/space/public/site.webmanifest.json: 3 "plane" hits.
(apps/web/public/favicon/site.webmanifest and apps/space/app/assets/favicon/site.webmanifest have 0 "plane" hits — verify and skip if clean.)

packages/propel/src/icons/brand/plane-logo.tsx: `export function PlaneLogo({ width = "85", height = "52", className, color = "currentColor" }: ISvgIcons)` returning an inline <svg> with the Plane mark paths. KEEP the export name `PlaneLogo` and the props signature (renaming the identifier is AI-03/Phase-2). Swap only the SVG path geometry to the Bright-Byte mark.

Asset paths (binary, client-supplied) — exact locations and sizes:
- Favicons: apps/web/app/assets/favicon/{favicon-16x16.png, favicon-32x32.png, favicon.ico, apple-touch-icon.png}
- App icons: apps/web/app/assets/icons/{icon-180x180.png, icon-512x512.png}
- PWA icons (public): apps/web/public/icons/{icon-192x192.png, icon-348x348.png, icon-512x512.png}; apps/web/public/favicon/{android-chrome-192x192.png, android-chrome-512x512.png}
- OG image: apps/web/app/assets/og-image.png (1200x630)
- Logos: apps/web/app/assets/plane-logos/{black-horizontal-with-blue-logo.png, white-horizontal-with-blue-logo.png, white-horizontal.svg, blue-without-text.png}; apps/web/public/plane-logos/plane-mobile-pwa.png
- Auth logos: apps/web/app/assets/auth/{gradient-logo.webp, gradient-bg-logo.webp}
- Spinners: apps/web/app/assets/images/{logo-spinner-light.gif, logo-spinner-dark.gif} (consumed by apps/web/core/components/common/logo-spinner.tsx)
</interfaces>
</context>

<constraints>
- Display name is exactly "Bright-Byte PMP".
- v1 keeps the existing brand color — do NOT change `theme_color`/`background_color`/any hex in any manifest.
- Keep the existing asset FILE PATHS and FILENAMES (e.g. the directory is named `plane-logos/` and the file `plane-mobile-pwa.png`). Renaming asset paths would require chasing every import reference and risks broken links/CSP/manifest mismatches — out of scope for this phase. Replace file CONTENTS in place; keep names.
- Keep the `PlaneLogo` export name and props signature (identifier rename is Phase 2 / AI-03).
- NEVER edit AGPL headers in plane-logo.tsx or logo-spinner.tsx.
- Icon dimensions in each manifest's `icons[].sizes` must continue to match the actual asset dimensions — do not change sizes.
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Rebrand all PWA manifest JSON strings</name>
  <read_first>
    - apps/web/manifest.json
    - apps/web/public/manifest.json
    - apps/web/public/site.webmanifest.json
    - apps/admin/public/site.webmanifest.json
    - apps/space/public/site.webmanifest.json
    - apps/web/public/favicon/site.webmanifest (confirm 0 brand hits)
    - apps/space/app/assets/favicon/site.webmanifest (confirm 0 brand hits)
  </read_first>
  <files>apps/web/manifest.json, apps/web/public/manifest.json, apps/web/public/site.webmanifest.json, apps/admin/public/site.webmanifest.json, apps/space/public/site.webmanifest.json</files>
  <action>
    BRAND-05: In each manifest, set `name` to a Bright-Byte value and `short_name` to "Bright-Byte PMP" (or "Bright-Byte" if a short_name length guideline applies — keep ≤12 chars where the file already used a short value). Rewrite any `description` so it contains no "Plane"/"plane". Replace every remaining case-insensitive "plane" brand string (names, descriptions, any `start_url`/`scope` that embeds a plane domain — but leave relative `start_url`/`scope` paths like "/" unchanged). Do NOT change `theme_color`, `background_color`, any hex color, or any `icons[].sizes`/`src` path. Keep valid JSON (no trailing commas — these are .json, not .jsonc). If `apps/web/public/favicon/site.webmanifest` or `apps/space/app/assets/favicon/site.webmanifest` contain any brand string after re-reading, rebrand them too and add them to files_modified in the SUMMARY.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && hits=$(grep -ric "plane" apps/web/manifest.json apps/web/public/manifest.json apps/web/public/site.webmanifest.json apps/admin/public/site.webmanifest.json apps/space/public/site.webmanifest.json | awk -F: '{s+=$2} END{print s}'); [ "$hits" -eq 0 ] && echo "PASS: 0 plane hits across manifests" || echo "FAIL: $hits plane hits remain"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -ric "plane" <each manifest>` returns 0 across all five manifests.
    - Each manifest contains "Bright-Byte" in `name`/`short_name`.
    - Every manifest still parses as valid JSON (`node -e "JSON.parse(require('fs').readFileSync('<file>'))"` succeeds for each).
    - No hex color value or `icons[].sizes`/`src` changed (diff shows only string-value edits).
  </acceptance_criteria>
  <done>All PWA manifests read Bright-Byte; valid JSON; colors and icon size/src wiring unchanged.</done>
</task>

<task type="auto">
  <name>Task 2: Swap the shared brand logo SVG to the Bright-Byte mark</name>
  <read_first>
    - packages/propel/src/icons/brand/plane-logo.tsx (full file — note export name PlaneLogo, props, viewBox, inline path geometry)
    - .planning/codebase/CONVENTIONS.md (React component + file-header rules)
  </read_first>
  <files>packages/propel/src/icons/brand/plane-logo.tsx</files>
  <action>
    BRAND-04: Replace the inner SVG path/geometry of the `PlaneLogo` component with the Bright-Byte logo mark. Keep the `export function PlaneLogo(...)` name and the `ISvgIcons` props signature unchanged (identifier rename is Phase 2). Update `viewBox`, `width`/`height` defaults, and `<path>`/`<svg>` children to render the new mark; keep `color = "currentColor"` theming so it inherits app colors (no hard-coded brand hex unless the mark requires it). If the client has supplied the logo as an SVG, transcribe its paths here; if not yet supplied, this task is blocked — coordinate with Task 3's checkpoint and use a faithful placeholder mark only if explicitly approved there. Do not edit the AGPL header.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -q "export function PlaneLogo" packages/propel/src/icons/brand/plane-logo.tsx && grep -q "ISvgIcons" packages/propel/src/icons/brand/plane-logo.tsx && echo "PASS: export name + props preserved" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `export function PlaneLogo` and the `ISvgIcons` props signature are unchanged.
    - The SVG renders the Bright-Byte mark (paths differ from the original Plane geometry).
    - `color` theming via the `color` prop still works (component does not hard-code a single fill that ignores the prop, unless the mark is intentionally multi-color).
    - AGPL header unchanged.
  </acceptance_criteria>
  <done>PlaneLogo component renders the Bright-Byte mark; component name/props/header preserved for Phase 2 compatibility.</done>
</task>

<task type="checkpoint:human-action" gate="blocking">
  <what-built>
    The manifest JSON and the `PlaneLogo` SVG are rebranded in code. The remaining work is replacing the BINARY brand assets, which only you can supply (client-provided logo/favicon/icon files).
  </what-built>
  <how-to-verify>
    Provide the Bright-Byte asset files and drop them in at these EXACT paths/filenames (keep the names; replace contents), at these sizes:
    1. Favicons: `apps/web/app/assets/favicon/favicon-16x16.png` (16x16), `favicon-32x32.png` (32x32), `favicon.ico` (multi-res .ico), `apple-touch-icon.png` (180x180).
    2. App icons: `apps/web/app/assets/icons/icon-180x180.png` (180x180), `icon-512x512.png` (512x512).
    3. PWA icons: `apps/web/public/icons/icon-192x192.png` (192), `icon-348x348.png` (348), `icon-512x512.png` (512); `apps/web/public/favicon/android-chrome-192x192.png` (192), `android-chrome-512x512.png` (512).
    4. OG image: `apps/web/app/assets/og-image.png` (1200x630).
    5. Logos: `apps/web/app/assets/plane-logos/{black-horizontal-with-blue-logo.png, white-horizontal-with-blue-logo.png, white-horizontal.svg, blue-without-text.png}`; `apps/web/public/plane-logos/plane-mobile-pwa.png`.
    6. Auth logos: `apps/web/app/assets/auth/{gradient-logo.webp, gradient-bg-logo.webp}`.
    7. Spinners: `apps/web/app/assets/images/{logo-spinner-light.gif, logo-spinner-dark.gif}` (light + dark variants).
    If you have the official Bright-Byte SVG, also share it so Task 2's `PlaneLogo` paths can be the real mark (otherwise an approved placeholder ships until you provide it).
    After drop-in: run `pnpm --filter web build` (or `pnpm build`) and load the web app — the tab favicon, auth-screen logo, and loading spinner should show the Bright-Byte mark; install the PWA and confirm the home-screen name/icon read Bright-Byte.
  </how-to-verify>
  <resume-signal>Type "assets dropped in" once the files are in place (or "use placeholder logo" to ship a placeholder PlaneLogo SVG for now and defer binary assets).</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| manifest/icon refs → browser PWA installer | The browser fetches `icons[].src`; a broken/renamed path yields a missing-icon install or a manifest parse error. |
| asset files → CSP/mixed-content | Replacing remote-referenced brand images with local assets must keep references same-origin (no http:// in https context). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-02-01 | Denial of Service | PWA manifest JSON | mitigate | Validate each manifest parses as JSON (Task 1 acceptance) and that `icons[].src` paths and `sizes` are unchanged, so the installer never hits a 404 or parse failure that breaks install. |
| T-02-02 | Information Disclosure | asset file references | mitigate | Keep all icon/logo references same-origin relative paths (no new external URLs); replacing contents in place means no mixed-content or CSP change is introduced. |
| T-02-03 | Tampering | client-supplied binary assets | accept | Assets are dropped in by the developer at a human checkpoint; image files carry no executable surface in this stack. Sizes verified against manifest declarations. |
| T-02-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages. No supply-chain surface. |
</threat_model>

<verification>
- All five manifests: `grep -ric "plane"` = 0 and each parses as JSON.
- `pnpm --filter @plane/propel run check:types` passes (PlaneLogo edit did not break types).
- After asset drop-in: `pnpm build` (or `pnpm --filter web build`) succeeds with all icon/logo asset paths resolving (no missing-asset errors).
- AGPL headers in plane-logo.tsx unchanged.
</verification>

<success_criteria>
- The Bright-Byte logo, favicon, and app/PWA icons appear in the sidebar, auth screen, spinners, and home-screen install (no Plane mark) — ROADMAP Phase 1 success criterion 2.
- PWA install prompt reads "Bright-Byte PMP".
- Brand color unchanged; asset paths/filenames preserved; PlaneLogo identifier preserved for Phase 2.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-02-SUMMARY.md` when done.
</output>
