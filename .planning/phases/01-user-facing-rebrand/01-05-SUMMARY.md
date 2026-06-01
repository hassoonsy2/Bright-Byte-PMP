---
phase: 01-user-facing-rebrand
plan: 05
subsystem: i18n
tags: [i18n, branding, locales, ai-assistant, dnt, brand-mark]

# Dependency graph
requires:
  - phase: 01-04 (AI-Byte + English i18n rebrand)
    provides: "Canonical English brand marks (Bright-Byte PMP / Byte) and the updated translate-skill DNT glossary that governs correctness here; example.com placeholder convention for undecided URL/email/domain hints"
provides:
  - "All 18 non-English locale namespaces carry the Latin brand mark Bright-Byte PMP / Byte; no Plane/Plane AI brand string leaks in any rendered value"
  - "pi_chat AI label = 'Byte' in every non-English locale (common.json + navigation.json), 36 files"
  - "i18n key parity preserved: sync:check 18/18 locales at 100% (3,837 keys each)"
  - "Non-English brand-mark mirror complete — Phase 1 user-facing rebrand language coverage done"
affects: [01-06-brand-leak-sweep, 02-package-rename-AI-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Brand-mark mirror (not re-translation): replace only the Latin brand token in VALUES, keep surrounding translated words, keys, interpolation tokens, and CLDR plural forms byte-identical"
    - "JSON.stringify(j, null, 2) + '\\n' round-trips byte-identically against the repo's locale files — enables surgical value edits with zero formatting noise"
    - "Word-boundary classifier: match 'Plane'/'plane' NOT followed by a lowercase Latin letter — auto-skips genuine non-brand plan-words (de Planen, es planes, pl planem, pt-BR Planejado) while catching brand + grammatical suffixes (CJK/Cyrillic/Hangul/Turkish-apostrophe)"

key-files:
  created:
    - .planning/phases/01-user-facing-rebrand/01-05-SUMMARY.md
  modified:
    - packages/i18n/src/locales/{cs,de,es,fr,id,it,ja,ko,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/*.json (18 non-English locale dirs)

key-decisions:
  - "grep -ric 'plane' gate interpreted against rendered VALUES (as in 01-04): 247 remaining grep hits = 234 JSON KEY identifiers (must stay byte-identical for parity) + 13 genuine non-brand target-language plan-words; 0 brand 'Plane' tokens remain in any rendered value"
  - "Illustrative URL/email/domain placeholders rebranded to RFC-2606 example.com forms (plane.so, planes.so, glab/gh.plane.town, plane.github.com, plane-github-enterprise), mirroring 01-04 — NOT an invented Bright-Byte domain (real product URL/email is undecided, owned by Plan 01-01)"
  - "German brand-possessive 'Planes' (Planes Arbeitsaufgabe / Planes KI-Assistent = Plane's …) rebranded to 'Bright-Byte PMP' (drops the genitive -s; the new brand takes no German genitive ending), matching 01-04's 'Plane's AI' -> 'Bright-Byte PMP's AI'"
  - "Lowercase brand mishaps in source ('your plane account' -> cs/fr/it/pl/sk empty-state) rebranded to Bright-Byte PMP; legitimate lowercase plan-words (planes, planem, planejar) preserved"
  - "Chinese embedded-Latin spacing left as the source had it (some with half-width space, some without) — brand-token-only value swap keeps surrounding characters intact; spacing normalization deferred to a future chore(i18n) sweep to avoid editing beyond the brand token"

patterns-established:
  - "Brand mark is exactly 'Bright-Byte PMP'; AI mark is exactly 'Byte' — identical Latin string in every locale incl. ja/ko/zh/ru/ua, never translated into an aircraft word"
  - "JSON KEY identifiers containing 'plane' (pi_chat, plane_pro, powered_by_plane_pages, new_to_plane, plane-intelligence, etc.) stay byte-identical — code identifiers reserved for Phase 2 / AI-03, never user-visible"

requirements-completed: [BRAND-09, AI-01]

# Metrics
duration: 5min
completed: 2026-06-01
---

# Phase 01 Plan 05: Non-English Locales Brand-Mark Rebrand Summary

**All 18 non-English locales rebranded from Plane / Plane AI to the Latin brand marks Bright-Byte PMP / Byte (values only), with pi_chat = "Byte" in every locale, surrounding translated copy intact, no aircraft-word renderings, and i18n key parity holding at 18/18 = 100%.**

## Performance

- **Duration:** ~5 min
- **Completed:** 2026-06-01
- **Tasks:** 3 (2 edit + 1 verification)
- **Files modified:** 303 locale JSON files across the 18 non-English locale directories

## Accomplishments

- **AI-01 (non-EN):** `pi_chat` set to exactly "Byte" in all 18 × 2 = 36 files (common.json + navigation.json), replacing the prior localized labels (Plane AI, AIチャット, AI Tschät, AI 聊天, ШІ Чат, 인공지능 챗, Obrolan AI, etc.). Key name unchanged.
- **BRAND-09:** The Latin brand token "Plane" rebranded to "Bright-Byte PMP" across every non-English locale value; "Plane AI" → "Byte"; "Plane Pages/Pro/Runner" → "Bright-Byte PMP Pages/Pro/Runner". Surrounding translated words, interpolation tokens (`{count}`, `{providerName}`, `{app}`), and CLDR plural forms all preserved.
- **No brand leak:** 0 brand "Plane" tokens remain in any rendered value. Verified the DNT forbidden list — no 飛行機 / 飞机 / 비행기 / Самолёт / Літак / バイト / 字节 / 바이트 anywhere.
- **Parity preserved:** `pnpm --filter @plane/i18n run sync:check` → all 18 locales at 100% (3,837 keys each), no missing/stale/collision keys. Every locale JSON parses.
- **Interpolation integrity:** automated token-multiset diff across all 303 changed files showed zero drift of any `{var}`, `<N>`, `%{...}`, or `$t(...)` token.

## Task Commits

Each task committed atomically:

1. **Task 1: Set pi_chat = "Byte" in all 18 non-English locales** — `827fecdf9a` (feat). 36 files, exactly 36 value-line changes (no key/structure change).
2. **Task 2: Rebrand the "Plane" brand token across all non-English locale values** — `1e03a0bb62` (feat). 303 files, 1801 value-line changes (balanced insert/delete = pure value swaps).
3. **Task 3: Verify full-catalog i18n parity** — verification only (no file edits); `sync:check` 18/18 at 100%, all JSON valid.

**Plan metadata:** final docs commit — this SUMMARY + STATE/ROADMAP/REQUIREMENTS.

## Files Created/Modified

- `packages/i18n/src/locales/{cs,de,es,fr,id,it,ja,ko,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/*.json` — brand value rebrand across all namespaces (303 files). English (`en/*`) intentionally untouched (source of truth, owned by 01-04).
- `.planning/phases/01-user-facing-rebrand/01-05-SUMMARY.md` — this summary.

## Decisions Made

- **grep gate vs key/word preservation:** The plan's `grep -ric "plane" = 0` gate is interpreted against rendered VALUES (as 01-04 did for English). After the rebrand, 247 grep hits remain across the 18 non-EN dirs: **234 are JSON KEY identifiers** (`pi_chat`, `plane_pro`, `powered_by_plane_pages`, `new_to_plane`, `new_at_plane`, `plane_project_connection`, `plane_project_connection_description`, `link_plane_project`, `open_plane_documentation`, `switch_to_plane_section`, `plane-intelligence`, `section_plane_events`, `plane_didnt_start_up_...`) that must stay byte-identical for i18n parity and are code identifiers (reserved for Phase 2 / AI-03 — never user-visible); **13 are genuine non-brand target-language plan-words** (de `Planen Sie`, es `planes de pago` / `Ver planes` / `supported_plans`, pl `Poza planem`, pt-BR `Planejado` / `Planeje` / `planejar` / `planejamento`). 0 brand "Plane" tokens remain in any value.
- **example.com placeholders (mirror 01-04):** Illustrative URL/email/domain hints (`plane.so`, `help@plane.so`, `https://planes.so/...`, `glab.plane.town`, `gh.plane.town`, `plane.github.com`, `plane-github-enterprise`) rebranded to RFC-2606 reserved `example.com` forms rather than inventing a Bright-Byte domain. The real WEBSITE_URL/SUPPORT_EMAIL is undecided and owned by Plan 01-01. The template "company name" placeholder ("Plane") became "Bright-Byte PMP" (a company-name example).
- **German brand-possessive `Planes`:** "Planes Arbeitsaufgabe" / "Planes KI-Assistent" (= "Plane's …") rebranded to "Bright-Byte PMP …" — the genitive -s is dropped because the new brand takes no German genitive ending, matching 01-04's "Plane's AI" → "Bright-Byte PMP's AI". Distinguished from the German verb "Planen Sie" (left intact).
- **Galileo retained:** the legacy "Galileo, Plane's AI assistant" empty-state copy keeps "Galileo"; only the "Plane('s)" brand portion was rebranded (e.g. de "Planes KI-Assistent" → "Bright-Byte PMP KI-Assistent", es "el asistente de IA de Plane" → "… de Bright-Byte PMP").
- **Chinese embedded-Latin spacing:** left exactly as the source had it (some hits had a half-width space around the Latin token, some did not). A brand-token-only value swap keeps the surrounding characters byte-identical; normalizing zh spacing per the translate skill would edit beyond the brand token, so it is deferred to a future `chore(i18n)` sweep (out of scope for a value-only brand mirror).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking resolution] example.com placeholders for undecided URL/email/domain hints**

- **Found during:** Task 2 (brand token rebrand)
- **Issue:** The acceptance gate (`grep -ric "plane" = 0`) conflicts with the scope guardrail forbidding invention of undecided brand strings (website URL, support email). Several non-EN hits were illustrative URL/email/domain placeholders pointing at plane.so / plane.town domains.
- **Fix:** Rebranded these illustrative placeholders to RFC-2606 `example.com` forms (mirroring 01-04), rather than inventing a product domain.
- **Files modified:** auth.json, template.json, integration.json (all 18 locales).
- **Committed in:** `1e03a0bb62`.

**2. [Rule 1 - Bug] Lowercase brand mishaps in source ("your plane account")**

- **Found during:** Task 2 verification
- **Issue:** Five empty-state strings (cs/fr/it/pl/sk) carried the brand lowercased mid-sentence ("…váš účet plane.", "…votre compte plane.", "…il tuo account plane.", "…konta plane.", "…váš účet plane.") — a translator lowercasing of the brand, which the English canonical rebranded as "your Plane account".
- **Fix:** Rebranded these lowercase brand references to "Bright-Byte PMP" while leaving legitimate lowercase plan-words (planes, planem, planejar) untouched.
- **Committed in:** `1e03a0bb62`.

### Acceptance-gate interpretation (not a deviation, documented for the verifier)

- `grep -ric "plane" = 0` is satisfied against rendered VALUES (0 brand tokens). The 247 remaining grep hits are 234 KEY identifiers + 13 genuine non-brand target-language plan-words — exactly the pattern 01-04 established for English (where 13 key hits remained). Plan 01-06 brand-leak sweep should treat these as expected.

**Total deviations:** 2 auto-fixed (1 blocking-resolution, 1 source-bug). No architectural changes; no checkpoints required.

## Issues Encountered

- **lint-staged internal `git stash` notices:** the pre-commit hook's lint-staged backup uses `git stash` on the main working tree (sequential mode, not a worktree). It backed up and restored cleanly on both commits — no contamination. oxfmt ran over the staged JSON and produced no further changes (the value-only edits already match the repo format).
- **Node engine warning:** local Node is v22.15.0 vs the repo's pinned `>=22.18.0` — a `[WARN] Unsupported engine` notice only; commits and the i18n tooling (sync:check, JSON parse) ran fine.

## Deferred Issues

- **Chinese (zh-CN/zh-TW) half-width spacing around the Latin brand token** is inconsistent in the source and was preserved as-is. A future `chore(i18n)` sweep can normalize per the translate skill (half-width space around embedded Latin brand tokens, no space before full-width punctuation). Not a brand-leak defect — the brand reads correctly either way.

## Known Stubs

None — all rebranded labels/values are wired to live i18n keys. No placeholder/empty-data stubs introduced.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- All shipped languages now present the Bright-Byte PMP / Byte brand marks; Phase 1 user-facing rebrand language coverage is complete (criterion 3 non-English portion, criterion 4 i18n portion).
- All internal AI/brand KEY identifiers and routes (pi_chat key, plane_pro, plane-intelligence, etc.) preserved for the Phase 2 / AI-03 internal rename.
- Plan 01-06 brand-leak sweep should treat the 234 "plane" KEY-name grep hits (and the 13 genuine non-brand plan-words) as expected, not leaks.

## Self-Check: PASSED

- Created file present: 01-05-SUMMARY.md ✓
- Task commits exist: 827fecdf9a, 1e03a0bb62 ✓
- sync:check 18/18 at 100%, all locale JSON valid ✓
- 0 brand "Plane" tokens in rendered values; no forbidden aircraft renderings ✓

---

_Phase: 01-user-facing-rebrand_
_Completed: 2026-06-01_
