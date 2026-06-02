---
phase: 04
slug: render-topology-infra
status: approved
shadcn_initialized: false
preset: none
created: 2026-06-03
reviewed_at: 2026-06-03
---

# Phase 04 - UI Design Contract

> Visual and interaction contract for Phase 4 deployment, onboarding, and admin-facing verification surfaces.

---

## Design System

| Property          | Value                                                             |
| ----------------- | ----------------------------------------------------------------- |
| Tool              | Existing internal design system                                   |
| Preset            | Not applicable                                                    |
| Component library | `@bright-byte/ui`, `@bright-byte/propel`, existing app components |
| Icon library      | `lucide-react` and `@bright-byte/propel/icons`                    |
| Font              | Existing app font stack and Tailwind text tokens                  |

Contract source:

- Use `packages/tailwind-config/AGENTS.md` for canvas, surface, and layer rules.
- Use `packages/tailwind-config/variables.css` semantic tokens.
- Use `packages/ui` and `packages/propel` controls before creating any phase-specific UI.
- Do not initialize shadcn for this phase.

---

## Phase UI Scope

Phase 4 is primarily infrastructure. It should not redesign the product or add a new marketing/landing surface.

Allowed UI touchpoints:

- Existing sign-in and magic-link flow used for live onboarding verification.
- Existing project/workspace creation flow used for client onboarding verification.
- Existing attachment upload states used to verify Cloudflare R2 presigned PUT/GET.
- Existing admin email configuration/test flow used to verify SMTP.
- Existing error, loading, and toast surfaces needed to make deployment-origin failures understandable.

Out of scope:

- New product navigation.
- New deployment dashboard unless explicitly required by implementation.
- New brand palette, typography scale, or illustration system.
- Any billing, upsell, or edition-gating UI.

---

## Visual Hierarchy

| Surface                   | Focal Point                                    | Secondary Information                     | Interaction Rule                                                     |
| ------------------------- | ---------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------- |
| Sign-in and magic-link    | Email/code form title and primary action       | Inline validation and helper text         | Keep one primary action visible at a time                            |
| Project creation          | Project name input and create action           | Optional metadata and avatar/upload state | Preserve existing modal/form density                                 |
| Attachment upload         | Upload action and upload progress/error state  | File type/icon metadata                   | Do not hide failed upload recovery behind icon-only controls         |
| Admin email configuration | SMTP host/port/security fields and test action | Provider credential helper text           | Keep destructive credential changes separated from test/send actions |
| Deployment-origin errors  | Error message and retry/check action           | Service name or origin that failed        | State the failed dependency and next action                          |

Focal-point rule: the primary action or failed dependency must be the first visual anchor in any changed UI. Secondary text uses `text-secondary` or `text-tertiary`, never accent color.

Icon-only rule: icon-only actions must use existing tooltip patterns and an accessible label. Use lucide icons where one already exists; otherwise use `@bright-byte/propel/icons`.

---

## Spacing Scale

Declared values:

| Token | Value | Usage                     |
| ----- | ----- | ------------------------- |
| xs    | 4px   | Icon gaps, inline padding |
| sm    | 8px   | Compact element spacing   |
| md    | 16px  | Default element spacing   |
| lg    | 24px  | Section padding           |
| xl    | 32px  | Layout gaps               |
| 2xl   | 48px  | Major section breaks      |
| 3xl   | 64px  | Page-level spacing        |

Exceptions: none for new Phase 4 UI. Existing package-defined button/input padding may remain unchanged.

Layout rules:

- Root application background remains `bg-canvas`; do not introduce another canvas.
- Page and panel areas use `bg-surface-1` or `bg-surface-2` as siblings.
- Nested cards, rows, inputs, popovers, and modals use the matching `bg-layer-*` tokens.
- Do not put UI cards inside other cards.
- Keep repeated verification/status rows stable in height so loading, success, and error states do not shift layout.

---

## Typography

Use exactly these roles for any new or edited Phase 4 UI copy:

| Role    | Size | Weight | Line Height |
| ------- | ---- | ------ | ----------- |
| Label   | 13px | 500    | 1.4         |
| Body    | 14px | 400    | 1.4         |
| Heading | 16px | 500    | 1.2         |
| Display | 20px | 500    | 1.2         |

Rules:

- Use `text-13`, `text-14`, `text-16`, and `text-20` only for new Phase 4 surfaces.
- Use only `font-normal` and `font-medium` for new Phase 4 text.
- Letter spacing remains the existing default token.
- Do not add hero-scale type to operational/admin surfaces.

---

## Color

Use existing semantic tokens, not raw hex values:

| Role          | Value                                                              | Usage                                                                                    |
| ------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| Dominant 60%  | `bg-surface-1`, `text-primary`                                     | Main app/admin surfaces and body text                                                    |
| Secondary 30% | `bg-layer-1`, `bg-layer-2`, `text-secondary`, `border-subtle`      | Cards, form fields, rows, helper copy, dividers                                          |
| Accent 10%    | `bg-accent-primary`, `text-accent-primary`, `border-accent-strong` | Primary CTA, active field focus ring, active nav/selected state, live-check success link |
| Destructive   | `bg-danger-primary`, `text-danger-primary`, `border-danger-strong` | Credential revocation, failed destructive actions, unrecoverable dependency errors       |

Accent reserved for:

- Primary action buttons such as `Apply Render settings`, `Send test email`, and `Create project`.
- Active navigation or selected state already present in the app.
- Focus rings and active controls.
- One success-path link per status/error surface when a next action is needed.

Accent is not reserved for all links, all icons, all status badges, or passive informational text.

Status colors:

- Success uses existing success tokens for completed checks only.
- Warning uses warning tokens for incomplete external setup.
- Danger uses danger tokens for failed deploy checks, failed upload, failed email, or credential revocation.

---

## Copywriting Contract

| Element                  | Copy                                                                                                                             |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Primary CTA              | Apply Render settings                                                                                                            |
| Empty state heading      | Deployment is not connected                                                                                                      |
| Empty state body         | Add the Render, R2, SMTP, and broker values before running the live onboarding check.                                            |
| Error state              | Deployment check failed. Review the failed service settings, then run the check again.                                           |
| Destructive confirmation | Revoke deployment credential: This will stop new deploy verification requests that use this credential. Type revoke to continue. |

Additional action labels:

| Context                           | Required Label       |
| --------------------------------- | -------------------- |
| SMTP test                         | Send test email      |
| Attachment verification           | Upload attachment    |
| Client onboarding                 | Create project       |
| Invite or magic-link verification | Send invite          |
| Retry failed live check           | Run deployment check |
| Broker verification               | Check worker queue   |

Copy rules:

- Do not use generic primary labels such as `Submit`, `OK`, `Save`, or `Cancel` for new Phase 4 primary actions.
- Error copy must name the failed dependency when known: Render, R2, SMTP, broker, live WebSocket, API, or auth cookies.
- Empty states must include the next action, not only the absence of data.
- Loading copy should use verb phrases: `Checking worker queue`, `Sending test email`, `Uploading attachment`.

---

## Component Contract

Use existing components and patterns:

| Need                 | Required Pattern                                                                                      |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| Primary action       | `Button` from `@bright-byte/ui` or `@bright-byte/propel/button`, variant `primary`, size `md` or `lg` |
| Secondary action     | Existing neutral/outline button pattern                                                               |
| Destructive action   | Existing danger button and alert modal pattern                                                        |
| Text input           | Existing `Input` with `mode="primary"` and inline error state                                         |
| Modal                | Existing modal core or app modal pattern; no nested cards inside modal body                           |
| Tooltip              | Existing `Tooltip` component for icon-only or truncated status text                                   |
| Status row           | Existing row/list/card layer tokens with icon, label, value, and action slot                          |
| Toast/error feedback | Existing toast/error mechanism used by the touched app                                                |

Do not add:

- New third-party UI registries.
- New global CSS variables for Phase 4.
- New one-off button/input/modal implementations.
- Decorative gradient, orb, bokeh, or marketing-style sections.

---

## Registry Safety

| Registry                      | Blocks Used                                 | Safety Gate                                               |
| ----------------------------- | ------------------------------------------- | --------------------------------------------------------- |
| Internal Bright-Byte packages | `@bright-byte/ui`, `@bright-byte/propel`    | Internal workspace packages; no registry vetting required |
| Existing icon dependencies    | `lucide-react`, `@bright-byte/propel/icons` | Existing dependencies; no registry import required        |
| Third-party registries        | none                                        | PASS - no third-party registry blocks declared            |

---

## Accessibility and Responsive Contract

- All form inputs must have visible labels or existing accessible label equivalents.
- Icon-only controls require tooltip text and accessible names.
- Error text appears next to the failed field or status row and must not rely on color alone.
- Mobile layouts stack form/status rows vertically with stable action placement.
- Button text must fit at 320px viewport width; prefer wrapping to truncating action labels.
- Preserve keyboard focus order through changed forms, modals, and status rows.

---

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS

**Approval:** approved 2026-06-03
