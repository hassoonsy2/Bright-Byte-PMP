---
phase: 01-user-facing-rebrand
plan: 05
type: execute
wave: 2
depends_on: [01-04]
files_modified:
  - packages/i18n/src/locales/cs
  - packages/i18n/src/locales/de
  - packages/i18n/src/locales/es
  - packages/i18n/src/locales/fr
  - packages/i18n/src/locales/id
  - packages/i18n/src/locales/it
  - packages/i18n/src/locales/ja
  - packages/i18n/src/locales/ko
  - packages/i18n/src/locales/pl
  - packages/i18n/src/locales/pt-BR
  - packages/i18n/src/locales/ro
  - packages/i18n/src/locales/ru
  - packages/i18n/src/locales/sk
  - packages/i18n/src/locales/tr-TR
  - packages/i18n/src/locales/ua
  - packages/i18n/src/locales/vi-VN
  - packages/i18n/src/locales/zh-CN
  - packages/i18n/src/locales/zh-TW
autonomous: true
requirements: [BRAND-09, AI-01]
must_haves:
  truths:
    - "All 18 non-English locales read 'Bright-Byte PMP'/'Byte' for the brand mark, with surrounding translated copy intact"
    - "The pi_chat label is 'Byte' in every non-English locale (common.json + navigation.json)"
    - "i18n key parity (sync:check) still passes across all locales"
  artifacts:
    - path: "packages/i18n/src/locales/de/common.json"
      provides: "German locale brand strings incl. pi_chat"
      contains: "Byte"
    - path: "packages/i18n/src/locales/ja/navigation.json"
      provides: "Japanese locale pi_chat label"
      contains: "Byte"
  key_links:
    - from: "packages/i18n/src/locales/<locale>/*"
      to: "packages/i18n/src/locales/en/*"
      via: "EN canonical brand marks mirrored per the translate skill DNT rule"
      pattern: "pi_chat"
---

<objective>
Rebrand the brand mark across all 18 non-English locales (BRAND-09) and set the `pi_chat` AI label to "Byte" in every locale (AI-01, non-English portion). Per the project's `translate` skill, "Bright-Byte PMP" and "Byte" are do-not-translate brand marks — so this is a brand-mark mirror (replace the Latin brand token, keep the surrounding translated sentence), NOT a re-translation. This runs in Wave 2 after Plan 04 because EN is the i18n source of truth and Plan 04 establishes the canonical brand marks (and updates the translate-skill DNT glossary that governs correctness here).

Purpose: A client who switches language must not see "Plane"/"Plane AI" leak. Consistent polish across all shipped languages.
Output: All 18 non-English locale directories with the brand mark rebranded and `pi_chat` = "Byte".
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
@.planning/phases/01-user-facing-rebrand/01-04-SUMMARY.md

<interfaces>
<!-- Per the translate skill DNT glossary (updated in Plan 04): brand marks stay LATIN in every locale. -->
<!-- Current non-EN pi_chat values vary — some already localized "AI", some left "Plane AI": -->
- de/navigation.json L28 "pi_chat": "Plane AI"  → "Byte"
- de/common.json L835 "pi_chat": "AI Tschät"    → "Byte"
- ja/navigation.json L28 "pi_chat": "AIチャット" → "Byte"
- ja/common.json L835 "pi_chat": "AIチャット"    → "Byte"
(Every locale has pi_chat in BOTH common.json and navigation.json — confirmed present in all 18 dirs.)

The brand word "Plane" also appears inside translated sentences in many non-EN files (e.g. "...mit Plane", "...在 Plane 中"). Replace ONLY the brand token with the Latin "Bright-Byte PMP"; keep the surrounding localized words. Forbidden: translating the brand into the local word for an aircraft (the translate skill lists these as forbidden renderings) — never produce 飛行機/飞机/Самолёт/etc. for the brand.

EN reference (canonical, from Plan 04): brand mark = "Bright-Byte PMP", AI mark = "Byte".
</interfaces>
</context>

<constraints>
- REQUIRED READING before editing any src/locales file: `.claude/skills/translate/SKILL.md`. Follow the Two Iron Rules: (1) brand marks ("Bright-Byte PMP", "Byte") stay Latin and are never translated; (2) CLDR plural categories preserved — do NOT add/remove/merge plural-form keys.
- Brand marks are exactly "Bright-Byte PMP" and "Byte" — identical Latin string in every locale, including ja/ko/zh/ru/ua.
- Replace ONLY the brand token inside each value; preserve all surrounding translated words, every interpolation token (`{{count}}`, `<1>...</1>`, `%{name}`), and every JSON KEY (including `pi_chat`). Keep each file valid JSON and key-for-key identical to before (sync:check parity must pass).
- Do NOT translate a non-brand use of a word that merely resembles "plane" in the target language — verify each hit is the brand reference before editing.
- These JSON files have NO AGPL header to protect.
- Do NOT change the `pi_chat` KEY name, the route `/pi-chat/`, or any identifier (Phase 2 / AI-03).
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Set pi_chat = "Byte" in all 18 non-English locales</name>
  <read_first>
    - .claude/skills/translate/SKILL.md (DNT: "Byte" is a brand mark, stays Latin)
    - One representative pair to confirm shape: packages/i18n/src/locales/de/common.json + de/navigation.json (the pi_chat lines)
    - packages/i18n/src/locales/en/common.json + en/navigation.json (canonical reference from Plan 04)
  </read_first>
  <files>packages/i18n/src/locales/{cs,de,es,fr,id,it,ja,ko,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/common.json and .../navigation.json</files>
  <action>
    AI-01 (non-EN): In each of the 18 locale directories, set the `pi_chat` value to "Byte" in BOTH common.json and navigation.json (replacing "Plane AI", "AIチャット", "AI Tschät", or whatever the current localized value is). Keep the `pi_chat` KEY name unchanged. Do this per-file; do not touch other keys. Keep valid JSON.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && bad=0; for d in cs de es fr id it ja ko pl pt-BR ro ru sk tr-TR ua vi-VN zh-CN zh-TW; do for f in common navigation; do v=$(node -e "try{const j=require('./packages/i18n/src/locales/'+process.argv[1]+'/'+process.argv[2]+'.json');const find=(o)=>{for(const k in o){if(k==='pi_chat')return o[k];if(o[k]&&typeof o[k]==='object'){const r=find(o[k]);if(r!==undefined)return r}}};console.log(find(j))}catch(e){console.log('ERR')}" "$d" "$f"); if [ "$v" != "Byte" ]; then echo "MISS $d/$f.json = $v"; bad=1; fi; done; done; [ "$bad" -eq 0 ] && echo "PASS: pi_chat=Byte in all 36 files" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `pi_chat` resolves to exactly "Byte" in all 18 × 2 = 36 files (common.json + navigation.json per locale).
    - The `pi_chat` KEY name is unchanged in every file; all files valid JSON.
  </acceptance_criteria>
  <done>The AI assistant label reads "Byte" in every shipped language.</done>
</task>

<task type="auto">
  <name>Task 2: Rebrand the "Plane" brand token across all non-English locale values</name>
  <read_first>
    - .claude/skills/translate/SKILL.md (forbidden aircraft renderings; brand mark stays Latin)
    - For each locale dir, grep its files for "plane" (case-insensitive) to enumerate the brand hits before editing
    - packages/i18n/src/locales/en/* (canonical phrasing reference from Plan 04)
  </read_first>
  <files>packages/i18n/src/locales/{cs,de,es,fr,id,it,ja,ko,pl,pt-BR,ro,ru,sk,tr-TR,ua,vi-VN,zh-CN,zh-TW}/*.json</files>
  <action>
    BRAND-09: For every non-English locale file, replace the Latin brand token "Plane" (and "Plane AI"→"Byte", "Plane Pages"→"Bright-Byte PMP Pages") inside string VALUES with the Latin brand mark "Bright-Byte PMP", keeping the surrounding translated words intact (e.g. German "...mit Plane" → "...mit Bright-Byte PMP"; zh "...在 Plane 中" → "...在 Bright-Byte PMP 中"). Before each edit, confirm the hit is the brand reference (not a coincidental local word). Never translate the brand into a local aircraft word (forbidden per the skill). Preserve all interpolation tokens, JSON keys, and plural-form keys. Process locale-by-locale so each file stays valid JSON. Work through all 18 directories; do not skip any (BRAND-09 requires all 18). If context runs high, the SUMMARY must record exactly which locales are fully done so a follow-up plan can finish the rest — but the target is all 18 complete.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && rem=$(grep -ric "plane" packages/i18n/src/locales/cs packages/i18n/src/locales/de packages/i18n/src/locales/es packages/i18n/src/locales/fr packages/i18n/src/locales/id packages/i18n/src/locales/it packages/i18n/src/locales/ja packages/i18n/src/locales/ko packages/i18n/src/locales/pl packages/i18n/src/locales/pt-BR packages/i18n/src/locales/ro packages/i18n/src/locales/ru packages/i18n/src/locales/sk packages/i18n/src/locales/tr-TR packages/i18n/src/locales/ua packages/i18n/src/locales/vi-VN packages/i18n/src/locales/zh-CN packages/i18n/src/locales/zh-TW | awk -F: '{s+=$2} END{print s}'); echo "non-EN brand 'plane' hits remaining: $rem (want 0)"; [ "$rem" -eq 0 ] && echo "PASS" || echo "REVIEW remaining hits"</automated>
  </verify>
  <acceptance_criteria>
    - `grep -ric "plane"` across all 18 non-English locale dirs totals 0 (no brand "Plane" token remains).
    - No brand token was translated into a local aircraft word (spot-check ja/zh/ru per the skill's forbidden list).
    - Every edited file remains valid JSON with unchanged keys and preserved interpolation/plural-form keys.
  </acceptance_criteria>
  <done>All 18 non-English locales carry the Bright-Byte brand mark with their translated copy intact.</done>
</task>

<task type="auto">
  <name>Task 3: Verify full-catalog i18n parity</name>
  <read_first>
    - packages/i18n/package.json (confirm the sync:check script name)
  </read_first>
  <files>(verification only — no file edits)</files>
  <action>
    Run the i18n parity/sync check across the whole catalog to confirm the value edits introduced no missing/stale/collision keys and that every locale still mirrors EN key-for-key. If `sync:check` reports drift that PRE-EXISTED (not caused by this phase), record it in the SUMMARY for a follow-up; do not fix unrelated drift here. Confirm all locale JSON files parse.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && pnpm --filter @plane/i18n run sync:check 2>&1 | tail -15; node -e "const fs=require('fs');const root='packages/i18n/src/locales';let bad=0;for(const l of fs.readdirSync(root)){const p=root+'/'+l;if(!fs.statSync(p).isDirectory())continue;for(const f of fs.readdirSync(p)){if(f.endsWith('.json')){try{JSON.parse(fs.readFileSync(p+'/'+f))}catch(e){console.log('BAD JSON',p+'/'+f);bad=1}}}}process.exit(bad)" && echo "ALL JSON VALID"</automated>
  </verify>
  <acceptance_criteria>
    - `pnpm --filter @plane/i18n run sync:check` shows no NEW key drift attributable to this phase (value-only edits keep parity).
    - Every locale JSON file (all locales, all namespaces) parses successfully.
  </acceptance_criteria>
  <done>The full i18n catalog is valid and key-parity holds after the brand-mark rebrand.</done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| locale value → rendered UI | 18 languages × many namespaces interpolated at runtime; a corrupted token or dropped plural form ships a broken string to every user of that language. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-05-01 | Tampering | i18n interpolation/plural keys across 18 locales | mitigate | Edit brand token only; preserve interpolation tokens, JSON keys, and CLDR plural-form keys; Task 3 runs `sync:check` + JSON-parse over the whole catalog to catch any parity break before ship. |
| T-05-02 | Repudiation/Quality | brand mistranslation (aircraft word) | mitigate | Follow the translate-skill forbidden-renderings list; spot-check ja/zh/ru that the brand stayed Latin "Bright-Byte PMP"/"Byte". |
| T-05-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages (JSON value edits + a verification script run). No supply-chain surface. |
</threat_model>

<verification>
- `grep -ric "plane"` across all 18 non-English locale dirs = 0.
- `pi_chat` = "Byte" in all 36 (18×2) files.
- `pnpm --filter @plane/i18n run sync:check` reports no new drift; all locale JSON valid.
</verification>

<success_criteria>
- UI strings in all 18 non-English locales read Bright-Byte (ROADMAP Phase 1 success criterion 3, non-English portion).
- The AI label is "Byte" in every shipped language (criterion 4, i18n portion).
- i18n key parity preserved.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-05-SUMMARY.md` when done. If any locale is not fully complete, list exactly which remain.
</output>
