---
phase: 01-user-facing-rebrand
plan: 04
type: execute
wave: 1
depends_on: []
files_modified:
  - apps/web/core/constants/ai.ts
  - apps/web/core/components/core/modals/gpt-assistant-popover.tsx
  - packages/propel/src/icons/sub-brand/pi-chat.tsx
  - packages/i18n/src/locales/en/auth.json
  - packages/i18n/src/locales/en/automation.json
  - packages/i18n/src/locales/en/common.json
  - packages/i18n/src/locales/en/empty-state.json
  - packages/i18n/src/locales/en/home.json
  - packages/i18n/src/locales/en/integration.json
  - packages/i18n/src/locales/en/navigation.json
  - packages/i18n/src/locales/en/power-k.json
  - packages/i18n/src/locales/en/project-settings.json
  - packages/i18n/src/locales/en/project.json
  - packages/i18n/src/locales/en/settings.json
  - packages/i18n/src/locales/en/template.json
  - packages/i18n/src/locales/en/tour.json
  - packages/i18n/src/locales/en/wiki.json
  - packages/i18n/src/locales/en/work-item-type.json
  - packages/i18n/src/locales/en/workflow.json
  - packages/i18n/src/locales/en/workspace-settings.json
  - packages/i18n/src/locales/en/workspace.json
  - .claude/skills/translate/SKILL.md
autonomous: true
requirements: [AI-01, AI-02, BRAND-08]
must_haves:
  truths:
    - "The AI assistant presents as 'Byte' in user-visible labels (sidebar entry, generating-response text, popover)"
    - "The AI assistant icon shows the Byte mark wherever PiChatLogo is rendered"
    - "English UI strings read 'Bright-Byte PMP'/'Byte', not 'Plane'/'Plane AI'"
    - "The i18n locale parity check (sync:check) still passes after the EN value edits"
  artifacts:
    - path: "apps/web/core/constants/ai.ts"
      provides: "AI generating-response loading text"
      contains: "Byte is generating response"
    - path: "packages/propel/src/icons/sub-brand/pi-chat.tsx"
      provides: "AI assistant icon SVG (PiChatLogo) — visual mark"
      contains: "export function PiChatLogo"
    - path: "packages/i18n/src/locales/en/common.json"
      provides: "Canonical English brand strings incl. pi_chat label"
      contains: "Byte"
  key_links:
    - from: "apps/web/core/components/workspace/sidebar/user-menu.tsx"
      to: "packages/propel/src/icons/sub-brand/pi-chat.tsx"
      via: "import { PiChatLogo } and labelTranslationKey sidebar.pi_chat"
      pattern: "PiChatLogo|pi_chat"
    - from: "all locale files"
      to: "packages/i18n/src/locales/en/*"
      via: "EN is the i18n source of truth mirrored by every locale"
      pattern: "pi_chat"
---

<objective>
Rebrand the AI assistant to "Byte" in every user-visible label and its icon (AI-01 user labels + AI-02 icon), and rebrand all English i18n strings from "Plane"/"Plane AI" to "Bright-Byte PMP"/"Byte" (BRAND-08, 112 case-insensitive "plane" hits across 18 English namespaces, including the `pi_chat` key). English is the i18n source of truth — locking it down here makes the non-English pass (Plan 05) a mechanical brand-mark mirror.

This plan deliberately groups the AI non-locale surfaces with the English locale because the AI label `pi_chat` lives in `en/common.json` and `en/navigation.json` — keeping all English-language brand voice in one plan gives clean file ownership and a single canonical reference for Plan 05.

Purpose: Brand coherence — "Bright-**Byte**" → the assistant is "Byte". "Plane AI" leaking in a label, the sidebar, or the generating-response toast breaks the white-label.
Output: Updated `ai.ts`, `gpt-assistant-popover.tsx`, the `PiChatLogo` SVG (Byte mark), all 18 `en/*.json` locale files, and the translate skill's DNT glossary.
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
@.claude/skills/translate/SKILL.md

<interfaces>
<!-- AI non-locale surfaces (current values from the repo): -->
apps/web/core/constants/ai.ts: LOADING_TEXTS[AI_EDITOR_TASKS.ASK_ANYTHING] = "Pi is generating response". (Rename the user-visible string to "Byte is generating response". Keep the enum AI_EDITOR_TASKS and key ASK_ANYTHING unchanged — those are code identifiers.)
apps/web/core/components/core/modals/gpt-assistant-popover.tsx: L195 "Generate response"; L270-271 placeholders "Tell AI what action to perform on this content..." / "Ask AI anything...". These are generic "AI" strings — confirm whether any say "Pi"/"Plane AI" and rebrand those to "Byte"; the generic "AI" placeholders may stay or be branded "Ask Byte anything..." (prefer branding for coherence). Do NOT rename the component/identifier GptAssistantPopover (Phase 2 / AI-03).
packages/propel/src/icons/sub-brand/pi-chat.tsx: `export function PiChatLogo({ color = "currentColor", ...rest }: ISvgIcons)` returning an <IconWrapper viewBox="0 0 24 24"> with the Pi mark paths. AI-02 = swap the SVG geometry to the Byte mark. KEEP the export name PiChatLogo, the registry key "sub-brand.pi-chat", and the props (identifier renames are AI-03/Phase 2).

English i18n brand hits (case-insensitive "plane", verified in the live codebase — 112 total across 18 files): auth.json 8, automation.json 1, common.json 3, empty-state.json 2, home.json 4, integration.json 42, navigation.json 2, power-k.json 1, project-settings.json 4, project.json 4, settings.json 1, template.json 6, tour.json 8, wiki.json 1, work-item-type.json 1, workflow.json 1, workspace-settings.json 16, workspace.json 7. (Sum = 112; the acceptance gate is `grep -ric "plane" = 0`, so the exact count is informational — do not stop early if you find a couple more or fewer sibling hits; rebrand every brand reference until the gate is 0.) Examples:
- common.json L247 "powered_by_plane_pages": "Powered by Plane Pages" ; L823 service-failure string mentioning "Plane" ; L835 "pi_chat": "Plane AI"
- navigation.json L28 "pi_chat": "Plane AI"
- integration.json: ~42 "with Plane" / "Plane project" phrasings (genuine product-name brand text → "Bright-Byte PMP")

translate skill DNT glossary (.claude/skills/translate/SKILL.md): currently lists "Plane" and "Plane AI" (formerly PI Chat) as do-not-translate brand marks for every locale. These entries are now WRONG for our fork — they must become "Bright-Byte PMP" and "Byte". This governs the correctness of Plan 05.
</interfaces>
</context>

<constraints>
- The AI assistant display name is exactly "Byte". The product name is exactly "Bright-Byte PMP".
- AI-01/AI-02 are USER-VISIBLE labels and icon ONLY. Do NOT rename code identifiers: keep `PiChatLogo`, the registry key `sub-brand.pi-chat`, the `pi_chat` i18n KEY name, the route segment `/pi-chat/`, the `GptAssistantPopover` component, and the `AI_EDITOR_TASKS` enum. Those internal renames are AI-03 / Phase 2. You change string VALUES and the icon SVG, never key/identifier/route NAMES.
- This is a locale edit — `.claude/skills/translate/SKILL.md` is REQUIRED READING before touching any `src/locales/*` file. Follow its Two Iron Rules: brand marks stay Latin and are not translated; CLDR plural forms preserved. (For EN this mainly means: rebrand the brand mark, keep everything else.)
- Preserve every i18n placeholder/interpolation token (`{{count}}`, `<1>...</1>`, `%{name}`, etc.) and every JSON key name exactly. Only string VALUES change. Keep files as valid JSON, key-for-key identical to before (the `pnpm --filter @plane/i18n run sync:check` parity check must still pass).
- NEVER edit AGPL headers in ai.ts, gpt-assistant-popover.tsx, or pi-chat.tsx. (Locale JSON files have no headers.)
- Do NOT translate or alter non-brand uses of words — e.g. an English string that legitimately uses "plane" in a non-brand sense (none expected in EN, but verify each hit is a brand reference before editing).
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Rebrand AI labels and the Byte icon (non-locale)</name>
  <read_first>
    - apps/web/core/constants/ai.ts (full file)
    - apps/web/core/components/core/modals/gpt-assistant-popover.tsx (around L195, L270-271, and any "Pi"/"Plane AI" string)
    - packages/propel/src/icons/sub-brand/pi-chat.tsx (full file — note PiChatLogo export, viewBox, paths)
    - packages/propel/src/icons/registry.ts (confirm key "sub-brand.pi-chat" stays)
  </read_first>
  <files>apps/web/core/constants/ai.ts, apps/web/core/components/core/modals/gpt-assistant-popover.tsx, packages/propel/src/icons/sub-brand/pi-chat.tsx</files>
  <action>
    AI-01 (ai.ts): change the loading text value to "Byte is generating response". Keep the `AI_EDITOR_TASKS` enum and `ASK_ANYTHING` key.
    AI-01 (popover): rebrand any "Pi"/"Plane AI" string to "Byte"; for the generic placeholders, prefer "Ask Byte anything..." and a Byte-consistent action prompt for brand coherence (keep them natural). Do NOT rename the GptAssistantPopover component.
    AI-02 (pi-chat.tsx): replace the inner SVG geometry with the Byte mark. Keep `export function PiChatLogo`, the `ISvgIcons` props, `color = "currentColor"` theming, and the viewBox dimensions (or update viewBox to fit the new mark while keeping the props signature). Do NOT change the registry key "sub-brand.pi-chat". If the client has not supplied a Byte icon SVG, transcribe the brand mark from the logo supplied in Plan 02; otherwise use a faithful Byte glyph that reads as the assistant icon.
    Do not edit AGPL headers.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -q "Byte is generating response" apps/web/core/constants/ai.ts && ! grep -iq "Pi is generating\|Plane AI" apps/web/core/constants/ai.ts apps/web/core/components/core/modals/gpt-assistant-popover.tsx && grep -q "export function PiChatLogo" packages/propel/src/icons/sub-brand/pi-chat.tsx && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `ai.ts` loading text reads "Byte is generating response"; `AI_EDITOR_TASKS`/`ASK_ANYTHING` unchanged.
    - No "Pi is generating" or "Plane AI" string remains in ai.ts or the popover.
    - `PiChatLogo` export name, props, and the `sub-brand.pi-chat` registry key are unchanged; the SVG geometry is the Byte mark.
    - AGPL headers unchanged in all three files.
  </acceptance_criteria>
  <done>The assistant shows "Byte" labels and the Byte icon; all internal identifiers/keys/routes preserved for Phase 2.</done>
</task>

<task type="auto">
  <name>Task 2: Rebrand all English locale string values</name>
  <read_first>
    - .claude/skills/translate/SKILL.md (REQUIRED before editing any src/locales file — Two Iron Rules, DNT glossary)
    - packages/i18n/src/locales/en/common.json (L247 powered_by_plane_pages, L823 service-failure, L835 pi_chat)
    - packages/i18n/src/locales/en/navigation.json (L28 pi_chat)
    - packages/i18n/src/locales/en/integration.json (the 42 "with Plane" hits)
    - each remaining en/*.json with brand hits listed in files_modified
  </read_first>
  <files>packages/i18n/src/locales/en/auth.json, packages/i18n/src/locales/en/automation.json, packages/i18n/src/locales/en/common.json, packages/i18n/src/locales/en/empty-state.json, packages/i18n/src/locales/en/home.json, packages/i18n/src/locales/en/integration.json, packages/i18n/src/locales/en/navigation.json, packages/i18n/src/locales/en/power-k.json, packages/i18n/src/locales/en/project-settings.json, packages/i18n/src/locales/en/project.json, packages/i18n/src/locales/en/settings.json, packages/i18n/src/locales/en/template.json, packages/i18n/src/locales/en/tour.json, packages/i18n/src/locales/en/wiki.json, packages/i18n/src/locales/en/work-item-type.json, packages/i18n/src/locales/en/workflow.json, packages/i18n/src/locales/en/workspace-settings.json, packages/i18n/src/locales/en/workspace.json</files>
  <action>
    BRAND-08 + AI-01 (pi_chat EN): For each en/*.json, replace brand "Plane" with "Bright-Byte PMP" and "Plane AI" with "Byte" in string VALUES only. Specifically: `pi_chat` value (common.json L835 and navigation.json L28) → "Byte". "Powered by Plane Pages" → "Powered by Bright-Byte PMP Pages" (keep feature-noun "Pages"). The ~42 integration.json "with Plane"/"Plane project" phrasings → "Bright-Byte PMP". The service-failure string → replace "Plane" with "Bright-Byte PMP". Before each edit confirm the hit is a brand reference (no legitimate non-brand "plane" expected in EN, but verify). Keep every JSON KEY name byte-identical (including `pi_chat`). Preserve all interpolation tokens/tags. Keep valid JSON. The 112-hit total is the expected order of magnitude; the gate is 0 remaining, not a fixed count — rebrand every brand reference you find.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && rem=$(grep -ric "plane" packages/i18n/src/locales/en/ | awk -F: '{s+=$2} END{print s}'); echo "EN brand hits remaining: $rem (want 0)"; node -e "const fs=require('fs');for(const f of fs.readdirSync('packages/i18n/src/locales/en')){if(f.endsWith('.json'))JSON.parse(fs.readFileSync('packages/i18n/src/locales/en/'+f))}" && echo "JSON: all valid"; [ "$rem" -eq 0 ] && echo "PASS" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -ric "plane" packages/i18n/src/locales/en/` totals 0 (no "Plane"/"plane" brand string remains in English values).
    - Every en/*.json parses as valid JSON.
    - The `pi_chat` value is "Byte" in both common.json and navigation.json; the KEY `pi_chat` is unchanged.
    - All interpolation tokens (`{{...}}`, `<n>...</n>`) and key names are byte-identical to before (only values changed).
  </acceptance_criteria>
  <done>English UI strings read Bright-Byte PMP/Byte; keys, tokens, and JSON validity preserved; canonical source ready for Plan 05.</done>
</task>

<task type="auto">
  <name>Task 3: Update the translate-skill DNT glossary + verify i18n parity</name>
  <read_first>
    - .claude/skills/translate/SKILL.md (DNT glossary table: "Plane" and "Plane AI" rows)
  </read_first>
  <files>.claude/skills/translate/SKILL.md</files>
  <action>
    Update the Do-Not-Translate glossary so the brand marks reflect the fork: change the "Plane" source-term row to "Bright-Byte PMP" and the "Plane AI" row to "Byte" (these remain DNT brand marks — Latin in every locale, never translated). Keep the other brand/feature/tier rows (Power K, PQL, Intake, Pro, Business, etc.) unchanged. This makes Plan 05's non-English rebrand a correct brand-mark mirror rather than a re-translation. Update the prose example "Plane's brand marks (Plane, Plane AI, ...)" to "Bright-Byte PMP, Byte, ...". Then run the i18n parity check to confirm the EN edits did not break key parity.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && grep -q "Bright-Byte PMP" .claude/skills/translate/SKILL.md && grep -qi "Byte" .claude/skills/translate/SKILL.md && (pnpm --filter @plane/i18n run sync:check 2>&1 | tail -5; echo "(sync:check run — review output: parity must pass)") && echo "DNT updated"</automated>
  </verify>
  <acceptance_criteria>
    - The translate skill DNT glossary lists "Bright-Byte PMP" and "Byte" as the brand marks (the "Plane"/"Plane AI" brand rows updated). Other DNT terms unchanged.
    - `pnpm --filter @plane/i18n run sync:check` reports no missing/stale/collision key errors introduced by the EN value edits (EN value changes don't change keys, so parity holds; any pre-existing drift is noted, not fixed here).
  </acceptance_criteria>
  <done>The translation source-of-truth doc reflects the Bright-Byte brand marks; i18n key parity intact.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| i18n value → rendered UI (with interpolation) | Locale values are interpolated with runtime data (`{{count}}`, `<1>link</1>`); corrupting a token can break rendering or markup. |
| icon SVG → DOM | The PiChatLogo SVG is rendered inline; malformed/foreign markup could affect layout (no script in this stack's icon SVGs). |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-04-01 | Tampering | i18n interpolation tokens / JSON keys | mitigate | Edit only string values; acceptance criteria assert all tokens and key names byte-identical and every file valid JSON, and `sync:check` confirms key parity — preventing runtime render breakage. |
| T-04-02 | Tampering | PiChatLogo inline SVG | mitigate | Replace path geometry only; keep IconWrapper/props; no `<script>`/foreignObject/event handlers in the icon (consistent with existing icons). |
| T-04-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages (string/SVG/JSON edits). No supply-chain surface. |
</threat_model>

<verification>
- `grep -ric "plane" packages/i18n/src/locales/en/` = 0; all en/*.json valid JSON.
- `grep -i "Pi is generating\|Plane AI"` across ai.ts + popover = 0; `PiChatLogo`/`sub-brand.pi-chat`/`pi_chat` key names unchanged.
- `pnpm --filter @plane/i18n run sync:check` passes (no new key drift).
- `pnpm --filter @plane/propel run check:types` passes (PiChatLogo edit).
- AGPL headers unchanged in ai.ts, gpt-assistant-popover.tsx, pi-chat.tsx.
</verification>

<success_criteria>
- The AI assistant presents as "Byte" — labels, generating-response text, and the assistant icon — everywhere a user sees it (ROADMAP Phase 1 success criterion 4).
- English UI strings read Bright-Byte (ROADMAP criterion 3, English portion).
- All internal AI identifiers/keys/routes preserved for the Phase 2 (AI-03) rename.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-04-SUMMARY.md` when done.
</output>
</output>
