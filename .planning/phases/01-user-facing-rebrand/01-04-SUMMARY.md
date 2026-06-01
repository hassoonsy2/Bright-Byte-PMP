---
phase: 01-user-facing-rebrand
plan: 04
subsystem: ui
tags: [i18n, branding, react, svg, locales, ai-assistant]

# Dependency graph
requires:
  - phase: 01-01 (app-metadata-and-brand-constants)
    provides: "Env-driven WEBSITE_URL/SUPPORT_EMAIL defaults (plane.so kept undecided) — informed the example.com placeholder decision in i18n"
provides:
  - "AI assistant presents as 'Byte' in all user-visible English labels (ai.ts loading text, popover placeholders/toast, pi_chat label)"
  - "Byte assistant icon (PiChatLogo SVG geometry swapped to a B-glyph + spark mark)"
  - "All 18 English locale namespaces rebranded: Plane -> Bright-Byte PMP, Plane AI -> Byte; 0 brand strings in rendered values"
  - "Canonical English i18n source of truth ready for Plan 05's non-English brand-mark mirror"
  - "translate-skill DNT glossary updated to Bright-Byte PMP/Byte brand marks"
affects: [01-05-non-english-locales, 01-06-brand-leak-sweep, 02-package-rename-AI-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "i18n value-only edits: keys + interpolation tokens byte-identical, only string VALUES change (sync:check parity preserved)"
    - "RFC-2606 example.com used for illustrative URL/email/domain placeholders to avoid inventing undecided product brand values"

key-files:
  created:
    - .planning/phases/01-user-facing-rebrand/deferred-items.md
  modified:
    - apps/web/core/constants/ai.ts
    - apps/web/core/components/core/modals/gpt-assistant-popover.tsx
    - packages/propel/src/icons/sub-brand/pi-chat.tsx
    - packages/i18n/src/locales/en/*.json (18 namespaces)
    - .claude/skills/translate/SKILL.md

key-decisions:
  - "Illustrative URL/email/domain placeholders (plane.so, glab.plane.town, gh.plane.town, plane-github-enterprise) rebranded to RFC-2606 example.com forms, NOT an invented Bright-Byte domain — the product's real website/support email is undecided and owned by Plan 01-01"
  - "Acceptance gate grep -ric plane = 0 interpreted against rendered VALUES (0 achieved); 13 remaining grep hits are JSON KEY identifiers that must stay byte-identical for i18n parity (never user-visible)"
  - "Byte icon = original Pi mark replaced with a B-glyph plus the assistant spark, keeping PiChatLogo export, ISvgIcons props, currentColor theming, and viewBox 0 0 24 24"
  - "Galileo (legacy AI feature name in project/workspace page empty-states) kept; only the 'Plane's AI' brand portion rebranded to 'Bright-Byte PMP's AI'"

patterns-established:
  - "AI assistant display name is exactly 'Byte'; product name is exactly 'Bright-Byte PMP'"
  - "Code identifiers/keys/routes (PiChatLogo, sub-brand.pi-chat, pi_chat key, AI_EDITOR_TASKS, GptAssistantPopover) preserved for Phase 2 / AI-03"

requirements-completed: [AI-01, AI-02, BRAND-08]

# Metrics
duration: 13min
completed: 2026-06-01
---

# Phase 01 Plan 04: AI → "Byte" + English i18n Rebrand Summary

**AI assistant rebranded to "Byte" (labels, generating-response text, popover, icon SVG) and all 18 English locale namespaces rebranded from Plane/Plane AI to Bright-Byte PMP/Byte with zero brand strings left in rendered values and i18n key parity intact.**

## Performance

- **Duration:** ~13 min
- **Started:** 2026-06-01T01:52Z (approx, first task commit)
- **Completed:** 2026-06-01T00:05Z
- **Tasks:** 3
- **Files modified:** 22 (3 code, 18 i18n JSON, 1 skill) + 1 created (deferred-items.md)

## Accomplishments

- AI loading text now reads "Byte is generating response"; popover placeholders read "Ask Byte anything..." / "Tell Byte what action to perform..."; the `pi_chat` label and `plane-intelligence` title/heading now render "Byte".
- `PiChatLogo` SVG geometry swapped from the Pi (π) mark to a Byte mark (stylized "B" + assistant spark), keeping the export name, props, `currentColor` theming, viewBox, and the `sub-brand.pi-chat` registry key.
- All 18 English locale namespaces rebranded: 0 "plane" brand strings remain in any rendered value (verified by a parsed values-only scan). Keys and interpolation tokens byte-identical; every file valid JSON.
- `pnpm --filter @plane/i18n run sync:check` passes — 18/18 locales at 100% parity (EN value edits did not change keys).
- translate-skill DNT glossary now lists Bright-Byte PMP and Byte as the brand marks (with legacy "Plane AI"/"PI Chat" kept as forbidden renderings), making Plan 05 a correct brand-mark mirror.

## Task Commits

Each task was committed atomically:

1. **Task 1: Rebrand AI labels and the Byte icon (non-locale)** - `baed8f84a6` (feat)
2. **Task 2: Rebrand all English locale string values** - `949717b6f9` (feat)
3. **Task 3: Update translate-skill DNT glossary + verify i18n parity** - `24b2956429` (docs)

**Plan metadata:** (final docs commit — this SUMMARY + STATE/ROADMAP/REQUIREMENTS)

## Files Created/Modified

- `apps/web/core/constants/ai.ts` - LOADING_TEXTS value → "Byte is generating response" (enum/key unchanged)
- `apps/web/core/components/core/modals/gpt-assistant-popover.tsx` - placeholders + invalid-task toast rebranded to "Byte" (GptAssistantPopover component unchanged)
- `packages/propel/src/icons/sub-brand/pi-chat.tsx` - SVG geometry → Byte mark (PiChatLogo export + props + viewBox + registry key preserved, AGPL header untouched)
- `packages/i18n/src/locales/en/{auth,automation,common,empty-state,home,integration,navigation,power-k,project-settings,project,settings,template,tour,wiki,work-item-type,workflow,workspace-settings,workspace}.json` - brand value rebrand (18 files)
- `.claude/skills/translate/SKILL.md` - DNT glossary + brand-mark prose updated to Bright-Byte PMP/Byte
- `.planning/phases/01-user-facing-rebrand/deferred-items.md` - logged pre-existing propel check:types failures (out of scope)

## Decisions Made

- **example.com for illustrative placeholders:** URL/email/domain placeholder hints (`plane.so`, `help@plane.so`, `https://planes.so/...`, `glab.plane.town`, `gh.plane.town`, `plane-github-enterprise`) are user-fill examples, not the product's own URL. The real website/support email is undecided and owned by Plan 01-01 (which keeps `plane.so` as the env-default). Rather than invent a Bright-Byte domain (scope-guardrail forbids inventing undecided brand strings), used RFC-2606 reserved `example.com` forms — clears the brand leak without inventing values. The template "company name" placeholder ("Plane") became "Bright-Byte PMP" (a company-name example, our company).
- **grep gate vs key preservation:** The 13 remaining `grep -ric "plane"` hits are all JSON KEY identifiers (`pi_chat`, `plane_pro`, `powered_by_plane_pages`, `new_to_plane`, `plane_project_connection`, `plane-intelligence`, etc.). Keys must stay byte-identical for i18n parity and are code identifiers (AI-03/Phase 2). The brand-leak gate was satisfied against rendered VALUES (0). Keys are never user-visible.
- **Galileo retained:** the legacy "Galileo, Plane's AI assistant" empty-state copy kept "Galileo"; only "Plane's AI" → "Bright-Byte PMP's AI".

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking resolution] example.com placeholders for undecided URL/email/domain hints**

- **Found during:** Task 2 (English locale rebrand)
- **Issue:** The acceptance gate (`grep -ric "plane" = 0`) conflicted with the scope guardrail forbidding invention of undecided brand strings (website URL, support email). Several i18n hits were illustrative URL/email/domain placeholders pointing at plane.so domains.
- **Fix:** Rebranded these illustrative placeholders to RFC-2606 reserved `example.com` forms (and the company-name example to "Bright-Byte PMP") rather than inventing a product domain. Confirmed against Plan 01-01, which owns and intentionally keeps `plane.so` as the env-default for the real (undecided) WEBSITE_URL/SUPPORT_EMAIL.
- **Files modified:** auth.json, template.json, integration.json
- **Verification:** Parsed values-only scan = 0 brand hits; all files valid JSON; tokens/keys byte-identical.
- **Committed in:** `949717b6f9` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking-resolution). No architectural changes; no checkpoints required.
**Impact on plan:** The example.com choice resolves the gate-vs-guardrail tension without inventing undecided values or scope creep. All other edits followed the plan exactly.

## Issues Encountered

- **Pre-existing `@plane/propel` check:types failures (out of scope):** `pnpm --filter @plane/propel run check:types` reports 34 errors — `TS2307 Cannot find module '@plane/constants'/'@plane/types'` (their `dist/` is not built in this environment) plus cascading implicit-`any` errors in unrelated chart/state-icon files. The edited `pi-chat.tsx` produces ZERO type errors. Root cause is unbuilt sibling workspace packages (turbo `^build` ordering), not this rebrand. Logged to `deferred-items.md`; SCOPE BOUNDARY rule applied (only fix issues directly caused by the task).

## Deferred Issues

- propel `check:types` requires a full `pnpm build` of workspace packages to resolve `@plane/*` module references — flagged in `deferred-items.md` for Phase 2 (atomic rename lands with a green build) or a build-env setup pass. Not a code defect in this plan's changes.

## Known Stubs

None — all rebranded labels/values are wired to live i18n keys and the icon renders via the existing registry. No placeholder/empty-data stubs introduced.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- English i18n is the locked source of truth — Plan 05 can mirror brand marks into the 18 non-English locales (DNT glossary already updated).
- All internal AI identifiers/keys/routes (PiChatLogo, sub-brand.pi-chat, pi_chat key, AI_EDITOR_TASKS, GptAssistantPopover, /pi-chat/) preserved for the Phase 2 / AI-03 internal rename.
- Plan 01-06 brand-leak sweep should treat the 13 remaining "plane" key-name grep hits as expected (keys, not values).

## Self-Check: PASSED

- Created files present: 01-04-SUMMARY.md, deferred-items.md ✓
- Modified files present: ai.ts, gpt-assistant-popover.tsx, pi-chat.tsx, en/\*.json, SKILL.md ✓
- Task commits exist: baed8f84a6, 949717b6f9, 24b2956429 ✓

---

_Phase: 01-user-facing-rebrand_
_Completed: 2026-06-01_
