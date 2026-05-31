---
phase: 01-user-facing-rebrand
plan: 06
type: execute
wave: 3
depends_on: [01-01, 01-02, 01-03, 01-04, 01-05]
files_modified:
  - .planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md
autonomous: false
requirements: [BRAND-11]
must_haves:
  truths:
    - "A case-insensitive 'plane' sweep across manifests, i18n, EMAIL_FROM, generated PDFs, and telemetry/user-agent strings is triaged with zero un-explained user-facing brand leaks"
    - "Every remaining 'plane' hit is classified as KEEP (AGPL header / @plane scope / non-brand / out-of-phase) or is fixed"
    - "AGPL copyright headers and LICENSE.txt/COPYRIGHT.txt are untouched (verified)"
  artifacts:
    - path: ".planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md"
      provides: "The triaged brand-leak audit: every plane hit classified KEEP/FIXED/OUT-OF-PHASE with reason"
      contains: "BRAND SWEEP"
  key_links:
    - from: "this sweep"
      to: "Plans 01-05 output"
      via: "verifies the rebrand across all user-facing surfaces"
      pattern: "Bright-Byte"
---

<objective>
Run the Pitfall-8 final brand-leak sweep (BRAND-11): a case-insensitive `plane` triage across the whole tree, focused on the surfaces the success criteria name — manifests, i18n, `EMAIL_FROM`, generated PDFs, and telemetry/user-agent strings. Every hit is classified as KEEP (legitimate), FIXED (a real leak we close now), or OUT-OF-PHASE (the `@plane/*` package scope = Phase 2; telemetry repoint = Phase 5; AGPL headers = never). Produce a triaged audit file and close any genuine user-facing leak that Plans 01–05 did not cover.

Purpose: This is the phase's exit gate. Success criterion 5 is "a case-insensitive `plane` sweep comes back clean (excluding verbatim AGPL headers)." A single missed manifest/i18n/email string fails the white-label.
Output: `01-06-BRAND-SWEEP.md` (the triaged audit) and any fixes for genuine leaks discovered.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/research/PITFALLS.md
@.planning/research/FEATURES.md
@.planning/phases/01-user-facing-rebrand/01-01-SUMMARY.md
@.planning/phases/01-user-facing-rebrand/01-02-SUMMARY.md
@.planning/phases/01-user-facing-rebrand/01-03-SUMMARY.md
@.planning/phases/01-user-facing-rebrand/01-04-SUMMARY.md
@.planning/phases/01-user-facing-rebrand/01-05-SUMMARY.md

<interfaces>
<!-- Classification rules for the triage (decided during research) -->
KEEP (legitimate "plane" — NOT a user-facing brand leak, do NOT edit):
  - AGPL source-file headers: `Copyright (c) 2023-present Plane Software, Inc.` / `SPDX-License-Identifier: AGPL-3.0-only` comment blocks. NEVER edit.
  - LICENSE.txt, COPYRIGHT.txt. NEVER edit.
  - The `@plane/*` npm package scope (imports, package.json names/deps) — renamed in Phase 2, not here.
  - The `@/plane-web/*` / `@/plane-live/*` edition aliases and tsconfig paths — internal seam, Phase 2.
  - The Python package `plane` (apps/api/plane/...), directory names, and code identifiers (PiChatLogo, GptAssistantPopover, renderPlaneDocToPdf*, sub-brand.pi-chat key, pi_chat KEY, /pi-chat/ route) — internal identifiers, Phase 2 (AI-03).
  - apps/web/app/assets/plane-logos/ and public/plane-logos/ directory/file NAMES — paths kept intentionally (Plan 02 replaced contents, not names).
  - Build/migration artifacts, node_modules, dist, .git.

OUT-OF-PHASE (real leak, but explicitly scheduled later — RECORD, do not fix here):
  - Telemetry default `https://telemetry.plane.so` (apps/api/plane/utils/otlp_endpoints.py _DEFAULT_OTLP_ENDPOINT) — repoint/disable is SEC-03 / Phase 5. Record as a tracked item.
  - Webhook user-agent `"Autopilot"` and the generic `Mozilla/5.0 ...` link-task UA (apps/api/plane/bgtasks/{webhook_task.py,work_item_link_task.py}) — neither literally says "Plane"; note they are clean for brand purposes. If any UA literally contains "Plane", that IS in-phase — fix it.

FIXED (genuine user-facing brand leak NOT covered by Plans 01-05 — close it now):
  - Any user-visible "Plane" string in a manifest, i18n value, email body, page title/meta, or PDF header/footer text that slipped through. Fix in place (respecting AGPL headers).

PDF note: apps/live/src/lib/pdf/* uses function NAMES like renderPlaneDocToPdf* (KEEP — Phase 2) and has no user-visible "Plane" TEXT in headers/footers (verified in research). Re-confirm there is no literal "Plane" string rendered into exported PDFs; if found, FIX.
</interfaces>
</context>

<constraints>
- NEVER edit AGPL copyright headers, LICENSE.txt, or COPYRIGHT.txt. The sweep EXCLUDES these by design — they are expected to contain "Plane" and that is correct.
- Do NOT rename the `@plane/*` scope, `@/plane-web` aliases, the Python `plane` package, asset directory names, or any code identifier/route (all Phase 2). Those "plane" hits are KEEP/OUT-OF-PHASE, never fixed here.
- Telemetry repoint and security items are Phase 5 — RECORD them, do not implement.
- Only FIX genuine user-facing brand-text leaks (manifest/i18n/email/title/meta/PDF text). Everything else is classified, not edited.
</constraints>

<tasks>

<task type="auto">
  <name>Task 1: Run the case-insensitive sweep and triage every hit</name>
  <read_first>
    - .planning/research/PITFALLS.md (Pitfall 8 surface list + the "Looks Done But Isn't" brand-sweep checklist)
    - The five prior SUMMARYs (what each plan already covered)
    - apps/api/plane/utils/otlp_endpoints.py (telemetry default — confirm it is the OUT-OF-PHASE item)
    - apps/api/plane/bgtasks/webhook_task.py, work_item_link_task.py (user-agent strings — confirm no literal "Plane")
  </read_first>
  <files>.planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md</files>
  <action>
    Run a whole-tree case-insensitive `plane` search EXCLUDING node_modules, dist, build, .turbo, and .git, focused first on the success-criterion surfaces (manifests, all locales, EMAIL_FROM, PDF text, telemetry/user-agent), then the broader tree. Suggested commands (record the exact ones used in the audit):
      grep -rin "plane" apps packages --include="*.json" --include="*.html" --include="*.tsx" --include="*.ts" --include="*.webmanifest" --include="*.py" -l   (then inspect)
      Targeted: all *manifest*/*.webmanifest; packages/i18n/src/locales/**; EMAIL_FROM (instance_value.py); apps/live/src/lib/pdf/** (text vs fn-names); otlp_endpoints.py; bgtasks UA strings.
    Build `01-06-BRAND-SWEEP.md` with a table: every hit (file:line, the string) classified KEEP / OUT-OF-PHASE / FIXED with a one-line reason mapped to the rules in <interfaces>. Use `grep -v` filters (e.g. exclude lines matching `Copyright (c) 2023-present Plane Software` and `SPDX-License-Identifier`) so AGPL headers are correctly EXCLUDED, not counted as leaks. Tally: total hits, KEEP, OUT-OF-PHASE, FIXED.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && test -f .planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md && grep -qiE "KEEP|OUT-OF-PHASE|FIXED" .planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md && echo "PASS: audit exists with classifications" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - `01-06-BRAND-SWEEP.md` exists and classifies EVERY "plane" hit found (in the success-criterion surfaces and the broader tree) as KEEP, OUT-OF-PHASE, or FIXED, each with a reason.
    - AGPL headers / LICENSE / COPYRIGHT are explicitly listed under KEEP (excluded by design), not counted as leaks.
    - Telemetry default and any UA finding are recorded under OUT-OF-PHASE with the target phase (5).
  </acceptance_criteria>
  <done>A complete, reasoned triage of every brand "plane" hit exists; no hit is unclassified.</done>
</task>

<task type="auto">
  <name>Task 2: Close any genuine user-facing brand leaks found</name>
  <read_first>
    - 01-06-BRAND-SWEEP.md (the FIXED list produced in Task 1)
    - Each file flagged FIXED
  </read_first>
  <files>(the specific files flagged FIXED in Task 1 — manifests / i18n / email / title-meta / PDF text only)</files>
  <action>
    For each hit classified FIXED, edit the user-visible "Plane" brand string to "Bright-Byte PMP" (or "Byte" for the AI mark) in place, applying the same rules as the source plans (preserve JSON keys/tokens, Django `{{ }}` placeholders, AGPL headers, asset path names). Do NOT touch anything classified KEEP or OUT-OF-PHASE. Re-run the targeted greps to confirm each FIXED surface is now clean. Update the audit's FIXED rows to "RESOLVED" with the new value.
    If the FIXED list is empty (Plans 01-05 caught everything), record "no residual leaks" in the audit and skip editing.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && manifests=$(grep -ric "plane" $(find apps -iname "*manifest*" -o -iname "*.webmanifest" | grep -vE "node_modules|dist") 2>/dev/null | awk -F: '{s+=$2} END{print s+0}'); i18n=$(grep -ric "plane" packages/i18n/src/locales 2>/dev/null | awk -F: '{s+=$2} END{print s+0}'); emailfrom=$(grep -c "mailer.plane.so\|Team Plane" apps/api/plane/license/utils/instance_value.py 2>/dev/null); echo "manifests=$manifests i18n=$i18n EMAIL_FROM_plane=$emailfrom (all want 0)"; [ "$manifests" -eq 0 ] && [ "$i18n" -eq 0 ] && [ "$emailfrom" -eq 0 ] && echo "PASS: success-criterion surfaces clean" || echo "FAIL"</automated>
  </verify>
  <acceptance_criteria>
    - All four code-checkable success-criterion surfaces are clean: manifests `grep -ric plane` = 0, i18n = 0, `EMAIL_FROM` default has no plane.
    - PDF export has no user-visible "Plane" text (function names are KEEP).
    - No KEEP/OUT-OF-PHASE item was edited (AGPL headers, @plane scope, telemetry, identifiers untouched).
  </acceptance_criteria>
  <done>Every genuine user-facing brand leak is closed; the audit reflects RESOLVED status; out-of-phase items remain recorded for Phases 2/5.</done>
</task>

<task type="auto">
  <name>Task 3: Confirm AGPL integrity is intact across the whole phase</name>
  <read_first>
    - .planning/codebase/CONVENTIONS.md (the exact AGPL header templates for TS and Python)
    - .planning/research/PITFALLS.md (Pitfall 2/3 — addlicense enforcement)
  </read_first>
  <files>.planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md</files>
  <action>
    Verify the rebrand did not touch any AGPL artifact: confirm LICENSE.txt and COPYRIGHT.txt are unchanged in this phase's diff, and that no source-file `Copyright (c) 2023-present Plane Software` / `SPDX-License-Identifier` header line was added or removed by any Phase-1 commit. Use `git diff <phase-base>..HEAD -- LICENSE.txt COPYRIGHT.txt` (empty) and a diff filter on header lines. If `addlicense` is available locally, run the check on the changed TS/Python files; otherwise rely on the header-diff being empty. Append an "AGPL Integrity" section to the audit recording the result.
  </action>
  <verify>
    <automated>cd /Users/Hussi/Desktop/Bright-Byte-PMP && lic=$(git diff -- LICENSE.txt COPYRIGHT.txt 2>/dev/null | wc -l | tr -d ' '); hdr=$(git diff 2>/dev/null | grep -E "^[-+].*(Copyright \(c\) 2023-present Plane Software|SPDX-License-Identifier: AGPL-3.0-only)" | wc -l | tr -d ' '); echo "LICENSE/COPYRIGHT diff lines=$lic (want 0); AGPL header diff lines=$hdr (want 0)"; [ "$lic" -eq 0 ] && [ "$hdr" -eq 0 ] && echo "PASS: AGPL intact" || echo "FAIL: AGPL artifact changed"</automated>
  </verify>
  <acceptance_criteria>
    - `git diff -- LICENSE.txt COPYRIGHT.txt` is empty (these files unchanged in Phase 1).
    - No AGPL header line (`Copyright (c) 2023-present Plane Software` / `SPDX-License-Identifier`) was added or removed in any Phase-1 diff.
    - The audit's "AGPL Integrity" section records the verification result.
  </acceptance_criteria>
  <done>AGPL headers and LICENSE/COPYRIGHT are provably untouched by the rebrand; copyright-check.yml will pass.</done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
    The full brand-leak sweep is triaged (`01-06-BRAND-SWEEP.md`), genuine leaks are closed, and AGPL integrity is verified. Code-checkable surfaces (manifests, i18n, EMAIL_FROM, PDF text) are clean; out-of-phase items (telemetry → Phase 5; @plane scope/identifiers → Phase 2) are recorded.
  </what-built>
  <how-to-verify>
    1. Open `.planning/phases/01-user-facing-rebrand/01-06-BRAND-SWEEP.md` and confirm the triage looks right — every hit is KEEP / RESOLVED / OUT-OF-PHASE with a sensible reason, and the OUT-OF-PHASE list (telemetry, package scope, identifiers) matches your expectation for Phases 2/5.
    2. Run the app (`pnpm build` then load web/admin/space) and confirm visually: browser tab title, OG preview, sidebar/auth logo, loading spinner, PWA install name, and the AI assistant label/icon all read Bright-Byte/Byte — no "Plane" anywhere a human looks.
    3. Trigger a test email (or review the rebranded templates) and confirm the sender, logo, and body read Bright-Byte.
    4. Confirm any "values to confirm" items from Plans 01/03 (website URL, support email, social handle, EMAIL_FROM, email logo host, legal footer) are either finalized or acceptably placeholdered for v1.
  </how-to-verify>
  <resume-signal>Type "approved" to close Phase 1, or list the surfaces still showing "Plane" / placeholders to fix.</resume-signal>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| audit ↔ AGPL artifacts | The sweep must distinguish protected AGPL headers (keep) from user-facing brand leaks (fix); mis-editing a header is an AGPL violation + CI break. |
| out-of-phase telemetry beacon | `telemetry.plane.so` default phones home; recorded here, repointed/disabled in Phase 5. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-06-01 | Tampering / Compliance | AGPL headers, LICENSE.txt, COPYRIGHT.txt | mitigate | Task 3 proves (via empty header/LICENSE diff) that no AGPL artifact was edited during the phase; the sweep explicitly excludes them. Protects against the Pitfall-3 AGPL violation + copyright-check.yml failure. |
| T-06-02 | Information Disclosure | telemetry default `telemetry.plane.so` | accept (defer) | Real leak but scoped to Phase 5 (SEC-03); recorded as OUT-OF-PHASE in the audit, not implemented here. Not a brand-text leak. |
| T-06-03 | Spoofing/Brand | residual user-facing "Plane" string | mitigate | Task 2 closes any genuine brand leak in manifest/i18n/email/title/PDF surfaces; greps assert the success-criterion surfaces are clean. |
| T-06-SC | Tampering | npm/pip/cargo installs | accept | This plan installs no packages (audit + targeted string fixes). No supply-chain surface. |
</threat_model>

<verification>
- `01-06-BRAND-SWEEP.md` exists with a complete KEEP/RESOLVED/OUT-OF-PHASE triage and an AGPL-Integrity section.
- Code-checkable surfaces clean: manifests = 0, i18n = 0, EMAIL_FROM = 0 plane hits; PDF text has no "Plane".
- `git diff -- LICENSE.txt COPYRIGHT.txt` empty; no AGPL header line added/removed in the phase.
- Human verification checkpoint approved.
</verification>

<success_criteria>
- A case-insensitive `plane` sweep across manifests, i18n, `EMAIL_FROM`, generated PDFs, and telemetry/user-agent strings comes back clean (excluding verbatim AGPL headers) — ROADMAP Phase 1 success criterion 5.
- Out-of-phase "plane" references (package scope → Phase 2; telemetry → Phase 5) are explicitly documented, not silently left.
- AGPL compliance provably intact.
</success_criteria>

<output>
Create `.planning/phases/01-user-facing-rebrand/01-06-SUMMARY.md` when done (in addition to the 01-06-BRAND-SWEEP.md audit artifact).
</output>
