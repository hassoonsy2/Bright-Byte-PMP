---
phase: 01-user-facing-rebrand
plan: 02
subsystem: brand-assets
tags: [pwa-manifest, svg-logo, brand, placeholder]
dependency_graph:
  requires: []
  provides: [BRAND-03, BRAND-04, BRAND-05]
  affects: [apps/web, apps/admin, apps/space, packages/propel]
tech_stack:
  added: []
  patterns: [inline-svg-component, pwa-manifest]
key_files:
  created: []
  modified:
    - apps/web/manifest.json
    - apps/web/public/manifest.json
    - apps/web/public/site.webmanifest.json
    - apps/admin/public/site.webmanifest.json
    - apps/space/public/site.webmanifest.json
    - packages/propel/src/icons/brand/plane-logo.tsx
    - packages/propel/src/icons/brand/plane-lockup.tsx
decisions:
  - "Placeholder 'BB' lettermark SVGs ship now; binary raster assets (favicons, icons, spinners, OG image, auth webp) deferred per user pre-approval at Task 3 checkpoint"
  - "Icon src paths (/plane-logos/plane-mobile-pwa.png) preserved verbatim in manifests per plan constraint — these are asset paths, not brand strings"
  - "Admin manifest short_name set to 'BB PMP Admin' (≤12 chars) to respect PWA length guidance"
metrics:
  duration: 2m
  completed: "2026-06-02"
  tasks_completed: 2
  tasks_total: 3
  files_changed: 7
---

# Phase 01 Plan 02: Manifests, Logos, and Icons Summary

Rebranded PWA manifest JSON strings across all five manifests to "Bright-Byte PMP", and replaced both shared brand SVG components (`PlaneLogo` compact mark + `PlaneLockup` auth-screen horizontal wordmark) with placeholder Bright-Byte vector marks (BB lettermark + "Bright-Byte PMP" geometric wordmark). Binary raster assets deferred pending client-supplied files per pre-approved user decision.

## Tasks

| #   | Task                                     | Status                  | Commit     |
| --- | ---------------------------------------- | ----------------------- | ---------- |
| 1   | Rebrand all PWA manifest JSON strings    | Complete                | 7fbcca33d0 |
| 2   | Swap BOTH shared brand logo SVGs         | Complete                | e99ad9e8a2 |
| 3   | Drop in binary brand assets (checkpoint) | Deferred (pre-approved) | —          |

## Verification Results

### Task 1 — PWA Manifest Strings

- `apps/web/manifest.json`: name, short_name → "Bright-Byte PMP"; description rewritten with no "plane" brand text
- `apps/web/public/manifest.json`: name, short_name → "Bright-Byte PMP"
- `apps/web/public/site.webmanifest.json`: name, short_name, description → "Bright-Byte PMP"
- `apps/admin/public/site.webmanifest.json`: name → "Bright-Byte PMP Admin", short_name → "BB PMP Admin", description rewritten
- `apps/space/public/site.webmanifest.json`: name, short_name, description → "Bright-Byte PMP"
- `apps/web/public/favicon/site.webmanifest`: confirmed 0 brand hits (name/short_name already empty) — no change needed
- `apps/space/app/assets/favicon/site.webmanifest`: confirmed 0 brand hits (name/short_name already empty) — no change needed
- All five manifests parse as valid JSON (node JSON.parse check passed)
- theme_color, background_color, icons[].sizes, and icons[].src paths unchanged
- 2 remaining `grep -ric plane` hits are in icon src paths (`/plane-logos/plane-mobile-pwa.png`) — preserved per plan constraint (asset filenames must not change)

### Task 2 — Brand SVG Components

- `export function PlaneLogo` and `export function PlaneLockup` export names preserved
- `ISvgIcons` props signatures (`width`, `height`, `className`, `color = "currentColor"`) preserved in both
- `viewBox="0 0 85 52"` preserved in PlaneLogo; `viewBox="0 0 253 53"` preserved in PlaneLockup
- SVG path geometry replaced with Bright-Byte placeholder: BB lettermark (compact) + "Bright-Byte PMP" geometric wordmark (horizontal)
- `color = "currentColor"` theming retained — all shapes use `fill={color}` or `stroke={color}`
- Git-diff color guard: 0 brand-color hex lines added/removed (PASS)
- `pnpm --filter propel run check:types` — passed (no type errors)
- AGPL headers ("Copyright (c) 2023-present Plane Software, Inc. and contributors") unchanged in both files
- oxlint --fix --deny-warnings passed via pre-commit hook

## Deviations from Plan

### Checkpoint Pre-Approved (User Decision)

**Task 3: Binary Brand Assets — Deferred**

- **Found during:** Plan load / checkpoint pre-resolution
- **Decision:** User pre-approved "use placeholder logo" path — ship placeholder SVG marks now, defer binary raster assets
- **Impact:** Binary assets remain as original Plane files (unchanged); placeholder SVGs ship for Task 2
- **Commit:** No commit — binary files untouched

## Known Stubs

The following binary brand assets are NOT yet replaced with Bright-Byte assets. These are deferred pending client-supplied files:

| Asset                       | Path                                                                  | Reason                             |
| --------------------------- | --------------------------------------------------------------------- | ---------------------------------- |
| Favicon 16x16               | `apps/web/app/assets/favicon/favicon-16x16.png`                       | Binary — awaiting client files     |
| Favicon 32x32               | `apps/web/app/assets/favicon/favicon-32x32.png`                       | Binary — awaiting client files     |
| Favicon ICO                 | `apps/web/app/assets/favicon/favicon.ico`                             | Binary — awaiting client files     |
| Apple Touch Icon            | `apps/web/app/assets/favicon/apple-touch-icon.png`                    | Binary — awaiting client files     |
| App Icon 180x180            | `apps/web/app/assets/icons/icon-180x180.png`                          | Binary — awaiting client files     |
| App Icon 512x512            | `apps/web/app/assets/icons/icon-512x512.png`                          | Binary — awaiting client files     |
| PWA Icon 192x192            | `apps/web/public/icons/icon-192x192.png`                              | Binary — awaiting client files     |
| PWA Icon 348x348            | `apps/web/public/icons/icon-348x348.png`                              | Binary — awaiting client files     |
| PWA Icon 512x512            | `apps/web/public/icons/icon-512x512.png`                              | Binary — awaiting client files     |
| Android Chrome 192x192      | `apps/web/public/favicon/android-chrome-192x192.png`                  | Binary — awaiting client files     |
| Android Chrome 512x512      | `apps/web/public/favicon/android-chrome-512x512.png`                  | Binary — awaiting client files     |
| OG Image 1200x630           | `apps/web/app/assets/og-image.png`                                    | Binary — awaiting client files     |
| Logo (black horizontal)     | `apps/web/app/assets/plane-logos/black-horizontal-with-blue-logo.png` | Binary — awaiting client files     |
| Logo (white horizontal)     | `apps/web/app/assets/plane-logos/white-horizontal-with-blue-logo.png` | Binary — awaiting client files     |
| Logo (white horizontal SVG) | `apps/web/app/assets/plane-logos/white-horizontal.svg`                | Binary/SVG — awaiting client files |
| Logo (blue mark)            | `apps/web/app/assets/plane-logos/blue-without-text.png`               | Binary — awaiting client files     |
| Mobile PWA logo             | `apps/web/public/plane-logos/plane-mobile-pwa.png`                    | Binary — awaiting client files     |
| Auth gradient logo          | `apps/web/app/assets/auth/gradient-logo.webp`                         | Binary — awaiting client files     |
| Auth gradient bg logo       | `apps/web/app/assets/auth/gradient-bg-logo.webp`                      | Binary — awaiting client files     |
| Spinner light               | `apps/web/app/assets/images/logo-spinner-light.gif`                   | Binary — awaiting client files     |
| Spinner dark                | `apps/web/app/assets/images/logo-spinner-dark.gif`                    | Binary — awaiting client files     |

These are drop-in replacements: supply files at the exact paths above (keeping filenames) to complete the icon/asset rebrand. No code changes needed — all import references already point to these paths.

## Threat Flags

No new security-relevant surface introduced. All manifest icon src paths remain same-origin relative references. No new external URLs or network endpoints added. T-02-01 and T-02-02 mitigations confirmed (manifests parse as valid JSON, icon paths preserved same-origin).

## Self-Check: PASSED

- `apps/web/manifest.json` — modified, committed in 7fbcca33d0
- `apps/web/public/manifest.json` — modified, committed in 7fbcca33d0
- `apps/web/public/site.webmanifest.json` — modified, committed in 7fbcca33d0
- `apps/admin/public/site.webmanifest.json` — modified, committed in 7fbcca33d0
- `apps/space/public/site.webmanifest.json` — modified, committed in 7fbcca33d0
- `packages/propel/src/icons/brand/plane-logo.tsx` — modified, committed in e99ad9e8a2
- `packages/propel/src/icons/brand/plane-lockup.tsx` — modified, committed in e99ad9e8a2
