---
phase: 02
slug: atomic-package-scope-rename
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-01
---

# Phase 02 - Validation Strategy

Per-phase validation contract for the atomic package-scope rename.

## Test Infrastructure

| Property           | Value                                                       |
| ------------------ | ----------------------------------------------------------- |
| Framework          | Vitest for codemods; Turborepo build/type/lint for monorepo |
| Config file        | `packages/codemods/vitest.config.ts`, `turbo.json`          |
| Quick run command  | `pnpm --filter @bright-byte/codemods run test`              |
| Full suite command | `pnpm build && pnpm check:types && pnpm check:lint`         |
| Estimated runtime  | Repository-dependent; expect several minutes                |

## Sampling Rate

- After codemod implementation: run `pnpm --filter @plane/codemods run test`.
- After manifest/package rename: run `pnpm --filter @bright-byte/codemods run test`.
- After lockfile regeneration: run the source-scoped residual grep gates.
- Before final commit: run the full suite command.
- Max feedback latency: one task; no code task may proceed after a failed gate without fixing it.

## Per-Task Verification Map

| Task ID  | Plan | Wave | Requirement | Threat Ref | Secure Behavior                                                              | Test Type     | Automated Command                                                                                                     | File Exists                  | Status    |
| -------- | ---- | ---- | ----------- | ---------- | ---------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------- | ---------------------------- | --------- | --------------------- | ----------------------- | --------------------------- | --- | ------- |
| 02-01-01 | 01   | 1    | RENAME-01   | T-02-01    | Codemod rewrites only `@plane/` package specifiers                           | unit          | `pnpm --filter @plane/codemods run test` then `pnpm --filter @bright-byte/codemods run test`                          | yes                          | pending   |
| 02-01-02 | 01   | 1    | RENAME-01   | T-02-01    | Package identity and dependency graph use `@bright-byte/*` consistently      | source/search | `git grep -n "@plane/" -- apps packages package.json pnpm-workspace.yaml turbo.json .npmrc AGENTS.md .github .claude` | yes                          | pending   |
| 02-01-03 | 01   | 1    | RENAME-02   | T-02-02    | Edition aliases and Python package remain untouched                          | source/search | `git grep -n "@/bright-byte-web\\                                                                                     | @/bright-byte-live" -- apps` | yes       | pending               |
| 02-01-04 | 01   | 1    | AI-03       | T-02-03    | Byte source identifiers replace Pi/GPT names without changing AI service URL | source/search | `git grep -n "PiChatLogo\\                                                                                            | sub-brand\\.pi-chat\\        | pi_chat\\ | GptAssistantPopover\\ | gpt-assistant-popover\\ | /pi-chat" -- apps packages` | yes | pending |
| 02-01-05 | 01   | 1    | RENAME-03   | T-02-01    | The renamed workspace builds, type-checks, and lints clean                   | integration   | `pnpm build && pnpm check:types && pnpm check:lint`                                                                   | yes                          | pending   |
| 02-01-06 | 01   | 1    | RENAME-02   | T-02-04    | AGPL headers and license files are untouched                                 | compliance    | `git diff -- LICENSE.txt COPYRIGHT.txt` plus header diff grep                                                         | yes                          | pending   |

## Wave 0 Requirements

Existing infrastructure covers all phase requirements:

- `packages/codemods` already has Vitest infrastructure.
- `turbo.json` already wires build/type/lint tasks through package dependencies.
- No new test framework is required.

## Manual-Only Verifications

| Behavior                     | Requirement          | Why Manual                                                | Test Instructions                                                                             |
| ---------------------------- | -------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Atomic final commit boundary | RENAME-01, RENAME-03 | Commit policy cannot be fully asserted by automated tests | Confirm there is no intermediate committed state where package names and imports disagree.    |
| Dirty worktree preservation  | RENAME-01, AI-03     | User changes may exist before execution                   | Confirm any pre-existing Phase 1 locale edits are preserved while `pi_chat` keys are renamed. |

## Validation Sign-Off

- [ ] Codemod unit tests pass before and after package rename.
- [ ] Source-scoped `@plane/` residual grep returns no output.
- [ ] Edition aliases remain `@/plane-web/*` and `@/plane-live/*`.
- [ ] Python package/imports under `apps/api/plane` remain untouched.
- [ ] AI service endpoint remains `/ai-assistant/`.
- [ ] `pnpm build && pnpm check:types && pnpm check:lint` is green.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending
