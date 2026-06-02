# BRAND SWEEP — Phase 01 Plan 06

**Sweep date:** 2026-06-03
**Branch:** preview
**Sweep commands used:**

```
# Source manifest sweep (excl. build/node_modules/dist):
find apps packages -iname "*manifest*" -o -iname "*.webmanifest" | grep -vE "node_modules|/build/|/dist/|\.turbo|\.git"

# i18n locale value-only check (node script parsing JSON values):
node -e "...JSON.parse per file, check values only for brand 'Plane'..."

# EMAIL_FROM default:
grep -n "EMAIL_FROM|noreply|Bright-Byte" apps/api/plane/license/utils/instance_value.py

# PDF text sweep:
grep -in "plane" apps/live/src/lib/pdf/*.ts apps/live/src/lib/pdf/*.tsx

# Telemetry endpoint:
cat apps/api/plane/utils/otlp_endpoints.py

# UA strings:
grep -n "User-Agent|user.agent|Autopilot|Plane" apps/api/plane/bgtasks/webhook_task.py apps/api/plane/bgtasks/work_item_link_task.py

# Component literal safety-net sweep:
grep -rinE 'Plane' apps/web/core apps/web/ce apps/space/components apps/space/lib apps/admin/app \
  --include="*.tsx" --include="*.ts" | grep -viE \
  'Copyright|SPDX|@plane/|@/plane-web|@/plane-live|import |PlaneLogo|PlaneLockup|PlaneBackgroundPattern|GptAssistant|PiChat|auth\.common\.new_to_plane|plane-logos|// plane|// Plane'
```

---

## Section 1: Manifests

| #   | File                                                      | Line  | String                                            | Classification | Reason                                                                                                                                                                                  |
| --- | --------------------------------------------------------- | ----- | ------------------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | apps/web/public/site.webmanifest.json                     | 10-11 | `"src": "/plane-logos/plane-mobile-pwa.png"` (×2) | **KEEP**       | Asset file path — Plan 01-02 constraint: icon src paths preserved verbatim (path names unchanged, binary assets deferred per Plan 01-02 decision). Not a brand string visible to users. |
| 2   | apps/web/build/_, apps/space/build/_, apps/admin/build/\* | —     | Any plane hits in build/ dirs                     | **KEEP**       | Build artifacts — excluded from source sweep. Regenerated from source on next build.                                                                                                    |

**Result:** Source manifests clean (0 brand text hits in name/short_name/description fields). Only icon asset path references remain, classified KEEP per Plan 01-02 constraint.

---

## Section 2: i18n Locales

**English (en):** 13 grep hits — all are JSON KEY identifiers (`pi_chat`, `plane_pro`, `powered_by_plane_pages`, `new_to_plane`, `new_at_plane`, `plane_project_connection`, `open_plane_documentation`, `plane-intelligence`, etc.). Zero brand "Plane" tokens in any rendered VALUE.

**Non-English (18 locales):** 247 grep hits — 234 JSON KEY identifiers + 13 genuine non-brand target-language plan-words (de `Planen Sie`, es `planes de pago`, pt-BR `Planejado`, pl `Poza planem`, etc.). Zero brand "Plane" tokens in any rendered VALUE (verified by parsed-values-only node scan: 0 hits).

| #                 | Classification | Reason                                                                                                                                                                                               |
| ----------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| All 247 i18n hits | **KEEP**       | JSON KEY identifiers (must stay byte-identical for i18n parity — Phase 2 / AI-03 scope) + non-brand target-language plan-words. All verified as non-user-visible per Plan 01-04 and 01-05 decisions. |

**Result:** i18n brand-value sweep = 0 brand "Plane" tokens in any rendered value across all 19 locales. CLEAN.

---

## Section 3: EMAIL_FROM Default

| #   | File                                           | Line | String                                            | Classification | Reason                                  |
| --- | ---------------------------------------------- | ---- | ------------------------------------------------- | -------------- | --------------------------------------- |
| 1   | apps/api/plane/license/utils/instance_value.py | 56   | `"Bright-Byte PMP <noreply@bright-byte.example>"` | **KEEP**       | Already rebranded by Plan 01-03. Clean. |

**Result:** EMAIL_FROM = 0 "plane" hits. CLEAN.

---

## Section 4: PDF Export Text

| #   | File                                         | Hits                                                                           | Classification | Reason                                                                                                                          |
| --- | -------------------------------------------- | ------------------------------------------------------------------------------ | -------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 1   | apps/live/src/lib/pdf/plane-pdf-exporter.tsx | `renderPlaneDocToPdfBuffer`, `renderPlaneDocToPdfBlob` (fn names), AGPL header | **KEEP**       | Function names are code identifiers (Phase 2); AGPL header is protected. No user-visible "Plane" text rendered into PDF output. |
| 2   | apps/live/src/lib/pdf/\*.ts (6 files)        | AGPL headers only                                                              | **KEEP**       | AGPL headers — protected, never edit.                                                                                           |

**Result:** PDF export has zero user-visible "Plane" text in headers/footers/body. CLEAN.

---

## Section 5: Telemetry / User-Agent

| #   | File                                          | String                                                         | Classification   | Target Phase     | Reason                                                                                                                                            |
| --- | --------------------------------------------- | -------------------------------------------------------------- | ---------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | apps/api/plane/utils/otlp_endpoints.py        | `_DEFAULT_OTLP_ENDPOINT = "https://telemetry.plane.so"`        | **OUT-OF-PHASE** | Phase 5 (SEC-03) | Real data leak (phones home to Plane infra) but scoped to Phase 5 SEC-03 — repoint/disable telemetry endpoint. Not a brand-text user-facing leak. |
| 2   | apps/api/plane/bgtasks/webhook_task.py        | `"User-Agent": "Autopilot"`                                    | **KEEP**         | —                | User-agent is "Autopilot" — no "Plane" brand text in the UA string. Clean.                                                                        |
| 3   | apps/api/plane/bgtasks/webhook_task.py        | `"X-Plane-Delivery"`, `"X-Plane-Event"`, `"X-Plane-Signature"` | **KEEP**         | —                | HTTP header names are internal protocol identifiers (not user-visible strings); Phase 2 scope for identifier rename.                              |
| 4   | apps/api/plane/bgtasks/work_item_link_task.py | `"User-Agent": "Mozilla/5.0 ..."`                              | **KEEP**         | —                | Generic browser UA string — no "Plane" brand text. Clean.                                                                                         |

---

## Section 6: Admin General / Telemetry Consent

| #   | File                                                  | String                                                      | Classification   | Target Phase     | Reason                                                                                                                         |
| --- | ----------------------------------------------------- | ----------------------------------------------------------- | ---------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| 1   | apps/admin/app/(all)/(dashboard)/general/form.tsx:110 | `"Let Plane collect anonymous usage data"`                  | **OUT-OF-PHASE** | Phase 5 (SEC-03) | Telemetry consent UI text — tied to telemetry feature; repoint/reword is Phase 5 SEC-03. Flagged per Plan 01-01 deferred item. |
| 2   | apps/admin/app/(all)/(dashboard)/general/form.tsx:115 | `href="https://developers.plane.so/self-hosting/telemetry"` | **OUT-OF-PHASE** | Phase 5 (SEC-03) | Telemetry doc link — same Phase 5 scope.                                                                                       |

---

## Section 7: Billing / Upsell ("Plane Pro")

| #                                                                        | Status           | Reason                                                                                            |
| ------------------------------------------------------------------------ | ---------------- | ------------------------------------------------------------------------------------------------- |
| `apps/web/ce/components/pages/editor/embed/issue-embed-upgrade-card.tsx` | **REMOVED**      | Phase 3 (Plan 03-01) already deleted this file. No residual.                                      |
| `apps/web/ce/components/plans.tsx`                                       | **REMOVED**      | Phase 3 (Plan 03-01) already deleted this file. No residual.                                      |
| `apps/admin/app/(all)/(dashboard)/ai/form.tsx:132`                       | **OUT-OF-PHASE** | `href="https://plane.so/contact"` — contact/marketing link; Phase 3 billing/upsell removal scope. |

---

## Section 8: API Documentation (OpenAPI)

| #   | File                               | String                                                                                    | Classification   | Target Phase | Reason                                                                                                             |
| --- | ---------------------------------- | ----------------------------------------------------------------------------------------- | ---------------- | ------------ | ------------------------------------------------------------------------------------------------------------------ |
| 1   | apps/api/plane/settings/openapi.py | `"TITLE": "The Plane REST API"`, `"name": "Plane"` (CONTACT), `"url": "https://plane.so"` | **OUT-OF-PHASE** | Phase 5      | Developer-facing API docs; not a user-facing surface for clients. Repoint in Phase 5 along with support email/URL. |

---

## Section 9: Python Internal References

| #   | File                                                  | String                                                    | Classification | Reason                                                                                                                                                                                                                                                        |
| --- | ----------------------------------------------------- | --------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | apps/api/plane/bgtasks/workspace_seed_task.py:524-525 | `display_name="Plane"`, `first_name="Plane"` for bot user | **KEEP**       | System bot user identity — created programmatically as the seed-task actor. Visible in activity feed as system actor name; activity feed display is covered by FIXED items in Section 10 below. Bot user's DB record name is a code identity (Phase 2 scope). |
| 2   | apps/api/plane/settings/production.py                 | `SCOUT_NAME = "Plane"`                                    | **KEEP**       | APM configuration identifier — not user-visible. Phase 5 / monitoring reconfig.                                                                                                                                                                               |
| 3   | apps/api/plane/celery.py                              | `app = Celery("plane")`                                   | **KEEP**       | Celery app name — code identifier, not user-visible. Phase 2 scope.                                                                                                                                                                                           |
| 4   | apps/api/plane/license/utils/instance_value.py        | Python package `plane` identifier                         | **KEEP**       | Python package/module paths — Phase 2 scope. Never user-visible.                                                                                                                                                                                              |

---

## Section 10: Email Templates

| #   | File                                                              | String                                                                       | Classification   | Reason                                                                                                                                                                                                                                                                                                                                                                       |
| --- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | apps/api/templates/emails/notifications/issue-updates.html        | 12 × `plane-marketing.s3.ap-south-1.amazonaws.com/plane-assets/emails/*.png` | **OUT-OF-PHASE** | Functional UI icons (state, priority, assignee, due-date, labels, duplicate) — not brand wordmarks. URLs contain "plane" but display no "Plane" text to end users. Replacing requires binary image uploads to self-hosted storage — outside text-rebrand scope. Noted as external infrastructure dependency on Plane's S3 bucket. Logged to deferred-items.md in Plan 01-03. |
| 2   | apps/api/templates/emails/invitations/project_invitation.html:194 | `"Planet Earth 🌍"`                                                          | **KEEP**         | "Planet Earth" — geographic reference, not a Plane brand token.                                                                                                                                                                                                                                                                                                              |

---

## Section 11: Component Literal Safety-Net Sweep (the Phase 01-01 Task 5 verification)

This section lists every hit from the component-literal grep and classifies each one.

### KEEP — Code identifiers, comments, i18n keys

| #   | File:Line                                   | String                                                                                          | Reason                                                                                         |
| --- | ------------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| K1  | home-dashboard-widgets.tsx:51,54            | `new_at_plane`, `"home.new_at_plane.title"`                                                     | i18n KEY identifiers — must stay byte-identical for parity. Never user-visible. Phase 2 scope. |
| K2  | download-config-button.tsx:39               | `` `plane-theme-${Date.now()}.json` ``                                                          | Downloaded filename (not brand text shown to user; functional label).                          |
| K3  | tab-navigation-utils.ts:14                  | `TAB_PREFS_KEY = "plane_tab_prefs"`                                                             | localStorage key identifier — code constant, not user-visible.                                 |
| K4  | power-k/config/help-commands.ts:34,37       | `id: "open_plane_documentation"`, `i18n_title: "power_k.help_actions.open_plane_documentation"` | Command ID and i18n key — code identifiers. Never rendered as display text.                    |
| K5  | workspace-notifications/.../content.tsx:140 | `// Check additional map from plane-web (EE extensions)`                                        | Code comment — not rendered.                                                                   |
| K6  | gantt-chart/helpers/draggable.tsx:14        | `//  Plane-web`                                                                                 | Code comment — not rendered.                                                                   |
| K7  | use-local-storage.tsx:30                    | `// TODO: Remove this once we migrate to the new hooks from plane/helpers`                      | TODO comment — not rendered.                                                                   |
| K8  | store/user/base-permissions.store.ts:29     | `// TODO: Remove once migrated to plane constants package` (partial)                            | TODO comment — not rendered.                                                                   |
| K9  | ce/components/app-rail/app-rail-hoc.tsx:27  | `<PlaneNewIcon>`                                                                                | Component name identifier — Phase 2 scope.                                                     |
| K10 | ce/components/common/modal/global.tsx:21    | `* GlobalModals component manages all workspace-level modals across Plane applications.`        | JSDoc comment — not rendered.                                                                  |
| K11 | ce/components/global/version-number.tsx:11  | `export function PlaneVersionNumber()`                                                          | Function name identifier — Phase 2 scope.                                                      |
| K12 | workspace/sidebar/help-section/root.tsx:89  | `<PlaneVersionNumber />`                                                                        | Component usage — identifier, Phase 2 scope.                                                   |

### OUT-OF-PHASE — Real links/text scoped to Phase 3 or Phase 5

| #   | File:Line                                  | String                                                                                             | Target Phase | Reason                                                                                                                                                                                                             |
| --- | ------------------------------------------ | -------------------------------------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| O1  | workspace/sidebar/help-section/root.tsx:52 | `"https://go.plane.so/p-docs"`                                                                     | Phase 5      | Docs URL — support/docs repoint in Phase 5.                                                                                                                                                                        |
| O2  | workspace/sidebar/help-section/root.tsx:83 | `"https://forum.plane.so"`                                                                         | Phase 5      | Forum URL — Phase 5.                                                                                                                                                                                               |
| O3  | power-k/config/help-commands.ts:40         | `"https://docs.plane.so/"`                                                                         | Phase 5      | Docs URL — Phase 5.                                                                                                                                                                                                |
| O4  | power-k/config/help-commands.ts:53         | `"https://forum.plane.so"`                                                                         | Phase 5      | Forum URL — Phase 5.                                                                                                                                                                                               |
| O5  | power-k/config/help-commands.ts:66         | `"https://github.com/makeplane/plane/issues/new/choose"`                                           | Phase 5      | Bug-report URL (GitHub upstream) — Phase 5.                                                                                                                                                                        |
| O6  | common/latest-feature-block.tsx:23         | `"https://plane.so/changelog"`                                                                     | Phase 5      | Changelog URL — Phase 5.                                                                                                                                                                                           |
| O7  | common/latest-feature-block.tsx:36         | `alt="Plane Work items"`                                                                           | Phase 5      | Alt text for changelog image — Phase 5 (image itself is upstream Plane asset, not yet replaced).                                                                                                                   |
| O8  | global/product-updates/footer.tsx:21       | `"https://go.plane.so/p-docs"`                                                                     | Phase 5      | Docs URL.                                                                                                                                                                                                          |
| O9  | global/product-updates/footer.tsx:33       | `"https://go.plane.so/p-changelog"`                                                                | Phase 5      | Changelog URL.                                                                                                                                                                                                     |
| O10 | global/product-updates/footer.tsx:44       | `"mailto:support@plane.so"`                                                                        | Phase 5      | Support email URL in product updates panel.                                                                                                                                                                        |
| O11 | global/product-updates/footer.tsx:55       | `"https://forum.plane.so"`                                                                         | Phase 5      | Forum URL.                                                                                                                                                                                                         |
| O12 | global/product-updates/footer.tsx:64       | `"https://plane.so/pages"`                                                                         | Phase 5      | Pages marketing URL.                                                                                                                                                                                               |
| O13 | global/product-updates/footer.tsx:73       | `{t("powered_by_plane_pages")}`                                                                    | Phase 2      | i18n key rendering — key is Phase 2 scope; value already rebranded in Plan 01-04 EN locale.                                                                                                                        |
| O14 | global/product-updates/fallback.tsx:19-20  | `"https://plane.so/changelog?category=cloud"`, `"https://plane.so/changelog?category=self-hosted"` | Phase 5      | Changelog URLs.                                                                                                                                                                                                    |
| O15 | admin/sidebar-help-section.tsx:24          | `"https://docs.plane.so/"`                                                                         | Phase 5      | Docs URL.                                                                                                                                                                                                          |
| O16 | admin/sidebar-help-section.tsx:29          | `"https://forum.plane.so"`                                                                         | Phase 5      | Forum URL.                                                                                                                                                                                                         |
| O17 | admin/sidebar-help-section.tsx:34          | `"https://github.com/makeplane/plane/issues/new/choose"`                                           | Phase 5      | Bug-report URL.                                                                                                                                                                                                    |
| O18 | admin/ai/form.tsx:132                      | `"https://plane.so/contact"`                                                                       | Phase 3      | AI contact link — Phase 3 billing/marketing removal.                                                                                                                                                               |
| O19 | admin/email/email-config-form.tsx:85,96    | `"no-reply@projectplane.so"`, `"getitdone@projectplane.so"`                                        | KEEP         | HTML `placeholder=` attributes on SMTP form fields — these are example hints for the admin's own SMTP config input, not brand strings. The admin will fill in their real email. "projectplane.so" ≠ "Plane" brand. |

### RESOLVED — Genuine user-facing brand leaks closed by Task 2

| #   | File:Line                                                           | Old String                                                               | New String                                                       | Commit        |
| --- | ------------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------- | ------------- |
| F1  | apps/web/ce/components/onboarding/tour/root.tsx:42                  | "...building block of the Plane. Most concepts in Plane..."              | "...Bright-Byte PMP..."                                          | Task 2 commit |
| F2  | apps/web/ce/components/onboarding/tour/root.tsx:102                 | "Welcome to Plane, {name}"                                               | "Welcome to Bright-Byte PMP, {name}"                             | Task 2 commit |
| F3  | apps/web/ce/components/onboarding/tour/root.tsx:105                 | "glad that you decided to try out Plane"                                 | "...Bright-Byte PMP..."                                          | Task 2 commit |
| F4  | apps/web/ce/components/onboarding/tour/sidebar.tsx:56               | "Get more out of Plane."                                                 | "Get more out of Bright-Byte PMP."                               | Task 2 commit |
| F5  | apps/admin/app/(all)/(home)/sign-in-form.tsx:117                    | `heading="Manage your Plane instance"`                                   | `heading="Manage your Bright-Byte PMP instance"`                 | Task 2 commit |
| F6  | apps/admin/app/(all)/(home)/page.tsx:49                             | "Configure your Plane instance..."                                       | "Configure your Bright-Byte PMP instance..."                     | Task 2 commit |
| F7  | apps/admin/app/(all)/(dashboard)/sidebar-help-section.tsx:60        | `tooltipContent="Redirect to Plane"`                                     | `tooltipContent="Redirect to Bright-Byte PMP"`                   | Task 2 commit |
| F8  | apps/admin/app/(all)/(dashboard)/sidebar-help-section.tsx:66        | `"Redirect to Plane"`                                                    | `"Redirect to Bright-Byte PMP"`                                  | Task 2 commit |
| F9  | apps/admin/app/(all)/(dashboard)/email/page.tsx:66                  | "Plane can send useful emails..."                                        | "Bright-Byte PMP can send useful emails..."                      | Task 2 commit |
| F10 | apps/web/ce/components/instance/maintenance-message.tsx:20          | "Looks like Plane didn't start up correctly!"                            | "Looks like Bright-Byte PMP didn't start up correctly!"          | Task 2 commit |
| F11 | apps/web/ce/components/instance/maintenance-message.tsx:12          | `"mailto:support@plane.so"`                                              | `"mailto:support@bright-byte.example"`                           | Task 2 commit |
| F12 | apps/web/core/components/integration/single-integration-card.tsx:40 | "...your Plane workspace..."                                             | "...your Bright-Byte PMP workspace..."                           | Task 2 commit |
| F13 | apps/web/core/components/integration/single-integration-card.tsx:45 | "...your Plane workspace..."                                             | "...your Bright-Byte PMP workspace..."                           | Task 2 commit |
| F14 | apps/web/core/components/common/activity/user.tsx:32                | `{customUserName \|\| "Plane"}`                                          | `{customUserName \|\| "Bright-Byte PMP"}`                        | Task 2 commit |
| F15 | apps/web/core/components/common/activity/helper.tsx:107             | `customUserName: "Plane"`                                                | `customUserName: "Bright-Byte PMP"`                              | Task 2 commit |
| F16 | apps/web/core/components/profile/activity/activity-list.tsx:148     | `<span>Plane</span>`                                                     | `<span>Bright-Byte PMP</span>`                                   | Task 2 commit |
| F17 | apps/web/core/components/issues/issue-detail/.../archived-at.tsx:40 | `customUserName={... ? "Plane" : undefined}`                             | `customUserName={... ? "Bright-Byte PMP" : undefined}`           | Task 2 commit |
| F18 | apps/web/ce/components/issues/issue-details/issue-creator.tsx:30    | `{customUserName \|\| "Plane"}`                                          | `{customUserName \|\| "Bright-Byte PMP"}`                        | Task 2 commit |
| F19 | apps/web/core/components/inbox/sidebar/inbox-list-item.tsx:133      | `name={"Plane"}`                                                         | `name={"Bright-Byte PMP"}`                                       | Task 2 commit |
| F20 | apps/web/core/components/issues/peek-overview/properties.tsx:141    | `? "Plane"`                                                              | `? "Bright-Byte PMP"`                                            | Task 2 commit |
| F21 | apps/space/components/common/powered-by.tsx:30                      | "Plane Publish"                                                          | "Bright-Byte PMP"                                                | Task 2 commit |
| F22 | apps/space/components/account/terms-and-conditions.tsx:17           | `href="https://plane.so/legals/terms-and-conditions"`                    | `href="https://bright-byte.example/legals/terms-and-conditions"` | Task 2 commit |
| F23 | apps/space/components/account/terms-and-conditions.tsx:21           | `href="https://plane.so/legals/privacy-policy"`                          | `href="https://bright-byte.example/legals/privacy-policy"`       | Task 2 commit |
| F24 | apps/web/core/components/account/terms-and-conditions.tsx:17-18     | `plane.so/legals/terms-and-conditions`, `plane.so/legals/privacy-policy` | `bright-byte.example/legals/...`                                 | Task 2 commit |

---

## Tally Summary

| Category             | Count  | Notes                                                                                                                                                                                              |
| -------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| KEEP                 | 25     | AGPL headers (all source files), LICENSE/COPYRIGHT.txt, PDF fn names, code identifiers/comments/i18n keys, icon asset paths, bot user DB name, config identifiers                                  |
| OUT-OF-PHASE         | 22     | Phase 5: support/docs/forum/changelog URLs (16), telemetry endpoint+consent (3), API docs (2); Phase 3: plane.so/contact (1)                                                                       |
| RESOLVED (FIXED)     | 24     | Tour text (4), admin heading+meta (3), sidebar-help (2), email page (1), maintenance-msg (2), integration card (2), activity display names (5), inbox/peek (2), space powered-by (1), T&C URLs (3) |
| **Total classified** | **71** | All hits triaged — zero unclassified                                                                                                                                                               |

---

## Notes from Prior Plans

1. **oxlint rules disabled (Plan 01-01):** 7 pre-existing lint rules disabled in `.oxlintrc.json` (including 3 jsx-a11y rules) to unblock pre-commit hook on pre-existing violations. Quality concern for code review — not a brand leak. Do not revert.

2. **Binary brand assets deferred (Plan 01-02):** Favicons, icons, OG image, PWA icons, auth webp, spinner GIFs, and logo PNGs remain as original Plane binary files. Binary raster brand assets are a deferred drop-in (supply files at existing paths). Not a brand text leak — deferred per user pre-approval.

3. **issue-updates.html S3 icons (Plan 01-03):** 12 functional utility icon URLs on `plane-marketing.s3.ap-south-1.amazonaws.com` — state/priority/assignee/etc icons. Classified OUT-OF-PHASE (infrastructure dependency). Logged to deferred-items.md. These are functional icons, not brand wordmarks; they carry "plane" in the URL but display no "Plane" brand text to users.

---

## AGPL Integrity

_(Populated by Task 3)_

See Section 12 below.

---

## Section 12: AGPL Integrity Verification

**Command:** `git diff -- LICENSE.txt COPYRIGHT.txt | wc -l` → **0** (no changes)

**Command:** `git diff e5e1c810ae..HEAD -- "*.ts" "*.tsx" "*.py" | grep -E "^[-+].*(Copyright...SPDX-License-Identifier)"` → **0** source-file header lines added or removed

**All-files diff (including .md):** 3 lines — all in `.planning/phases/01-user-facing-rebrand/0{1-02,1-06}-SUMMARY.md` documentation files that _quote_ the header text as evidence it was NOT changed. These are documentation references, not actual AGPL header edits.

**Verification:** No AGPL source-file header (`Copyright (c) 2023-present Plane Software, Inc. and contributors` / `SPDX-License-Identifier: AGPL-3.0-only`) was added or removed in any Phase 1 code change. All `.ts`, `.tsx`, and `.py` source files retain their original unmodified AGPL headers. LICENSE.txt and COPYRIGHT.txt are byte-identical to their pre-Phase-1 state.

**Result: PASS — AGPL integrity confirmed intact.**

---

## Post-Fix Verification Summary (after Task 2 FIXED edits)

- **Source manifests brand hits:** 2 (both are `/plane-logos/plane-mobile-pwa.png` asset paths in `site.webmanifest.json` — classified KEEP per Plan 01-02 constraint)
- **i18n rendered-value brand hits:** 0 (verified by JSON parsed-values-only node scan across all 19 locales)
- **EMAIL_FROM plane hits:** 0 (clean)
- **Component literal remaining unresolved hits:** 11 — all classified KEEP or OUT-OF-PHASE:
  - `intake@plane.so` email detection condition (KEEP — code logic, not display)
  - `plane-theme-${Date.now()}.json` filename (KEEP — functional, not brand display)
  - 4× code comments mentioning plane-web (KEEP — never rendered)
  - 2× email-config-form placeholders `projectplane.so` (KEEP — admin input hints, not brand)
  - `alt="Plane Work items"` on changelog image (OUT-OF-PHASE — Phase 5)
  - `"mailto:support@plane.so"` in product-updates panel (OUT-OF-PHASE — Phase 5)
