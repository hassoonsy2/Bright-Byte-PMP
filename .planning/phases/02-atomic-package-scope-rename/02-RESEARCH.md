# Phase 02 Research: Atomic Package-Scope Rename

**Phase:** 02 - Atomic Package-Scope Rename
**Researched:** 2026-06-01
**Status:** Complete
**Inputs:** `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/research/{ARCHITECTURE,PITFALLS,SUMMARY}.md`, live repo inspection

## RESEARCH COMPLETE

Phase 02 is a mechanical but high-risk monorepo rename. The correct unit of execution is one atomic implementation plan: the repo cannot be left with some packages named `@bright-byte/*` while consumers still depend on `@plane/*`.

## Phase Boundary

This phase delivers:

- `@plane/*` package scope renamed to `@bright-byte/*` across package names, dependency keys, import/export specifiers, tsconfig `extends`, CSS `@import`s, hoist config, and command documentation.
- A new tested codemod under `packages/codemods` to rewrite TypeScript/TSX import surfaces safely.
- Regenerated `pnpm-lock.yaml` via `pnpm install`; no hand edits.
- Internal AI identifiers renamed from Pi/GPT assistant naming to Byte naming where listed by `AI-03`.
- Full verification with `pnpm build`, `pnpm check:types`, `pnpm check:lint`, codemod tests, and residual grep gates.

This phase does not deliver:

- Renaming the Django Python package `apps/api/plane`.
- Renaming `@/plane-web/*` or `@/plane-live/*` edition aliases.
- Editing AGPL headers, `LICENSE.txt`, or `COPYRIGHT.txt`.
- Billing/upsell removal or Render deployment work.

## Key Findings

### Atomicity

The workspace uses `workspace:*` dependency links. A partial rename breaks install/build resolution because package identity and consumer dependency keys must match. The implementation must land all rename surfaces together and verify before the final commit.

### Rename Surfaces

Current repo inspection confirms these exact surfaces:

| Surface                 | Current examples                                                                                        | Target                                              |
| ----------------------- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Package names           | `packages/constants/package.json` -> `@plane/constants`                                                 | `@bright-byte/constants`                            |
| Dependency keys         | `apps/web/package.json` -> `@plane/ui`: `workspace:*`                                                   | `@bright-byte/ui`: `workspace:*`                    |
| TS config extends       | `@plane/typescript-config/react-router.json`                                                            | `@bright-byte/typescript-config/react-router.json`  |
| CSS imports             | `@import "@plane/tailwind-config/index.css";`                                                           | `@import "@bright-byte/tailwind-config/index.css";` |
| TS/TSX imports          | `from "@plane/types"`                                                                                   | `from "@bright-byte/types"`                         |
| Dynamic/require imports | `import("@plane/...")`, `require("@plane/...")` if present                                              | `@bright-byte/...`                                  |
| Tooling docs            | `.npmrc`, `.github/instructions/bash.instructions.md`, `.claude/skills/translate/SKILL.md`, `AGENTS.md` | update package filter/scope strings                 |

There are 15 scoped package names and 19 package manifests with scoped dependency references. A current `git grep -l '@plane/' -- apps packages .github .claude AGENTS.md .npmrc` finds about 1,871 files, mostly import sites under `apps/` and `packages/`.

### Codemod Harness

`packages/codemods` already provides:

- jscodeshift transforms (`function-declaration.ts`, `remove-directives.ts`).
- Vitest tests using `@hypermod/utils` and `applyTransform`.
- Package-local `pnpm --filter @plane/codemods run test`.

Add `packages/codemods/rename-scope.ts` and `packages/codemods/tests/rename-scope.spec.ts`. The test source should avoid leaving raw `@plane/` text in the repository after the rename by building the old specifier token at runtime, for example from `["@plane", "types"].join("/")`.

### Things To Preserve

The rename must explicitly preserve these namespaces:

- `@/plane-web/*` in `apps/web/tsconfig.json` and its imports.
- `@/plane-live/*` in `apps/live/tsconfig.json` and its imports.
- `next/link`, `next/navigation`, `next/script`, and the compat shim files under `apps/web/app/compat/next`.
- Django imports, settings, migrations, and Celery references using the Python package name `plane`.
- AGPL copyright headers and license files.

### AI Identifier Scope

`AI-03` is source-level naming cleanup folded into this phase. Current concrete targets:

- `packages/propel/src/icons/sub-brand/pi-chat.tsx` -> Byte-named icon module and exported component.
- `PiChatLogo` import/export/usages -> `ByteLogo`.
- Icon registry key `sub-brand.pi-chat` -> `sub-brand.byte`.
- Icon constants title `PiChatLogo` -> `ByteLogo`.
- Sidebar key/translation key `pi_chat` -> `byte`.
- `GptAssistantPopover` component/file/state names -> `ByteAssistantPopover` names.
- Sidebar route/path checks using `pi-chat` -> Byte-named path if no backend service URL is affected.

The AI backend service contract remains unchanged: `apps/web/core/services/ai.service.ts` still posts to `/api/workspaces/${workspaceSlug}/ai-assistant/`.

## Implementation Strategy

1. Record the dirty worktree and abort execution if there are uncommitted changes overlapping files to be rewritten, unless the executor can preserve them exactly.
2. Add and test the `rename-scope` codemod while the package is still named `@plane/codemods`.
3. Rewrite package manifests, tsconfig extends, CSS imports, `.npmrc`, and package-scope command docs from `@plane/*` to `@bright-byte/*`.
4. Run the codemod over TS/TSX source under apps and packages.
5. Rename Byte internal identifiers in source and locale keys while preserving user-facing values from the active rebrand work.
6. Run `pnpm install` to regenerate `pnpm-lock.yaml`.
7. Run all verification gates before the final atomic commit.

## Validation Architecture

### Primary Commands

| Purpose                             | Command                                        |
| ----------------------------------- | ---------------------------------------------- |
| Codemod test before manifest rename | `pnpm --filter @plane/codemods run test`       |
| Codemod test after manifest rename  | `pnpm --filter @bright-byte/codemods run test` |
| Regenerate lockfile                 | `pnpm install`                                 |
| Full build                          | `pnpm build`                                   |
| Typecheck                           | `pnpm check:types`                             |
| Lint                                | `pnpm check:lint`                              |

### Residual Search Gates

Run after `pnpm install` and before final commit:

- `git grep -n "@plane/" -- apps packages package.json pnpm-workspace.yaml turbo.json .npmrc AGENTS.md .github .claude` returns no output.
- `git grep -n "@bright-byte/" -- apps/api` returns no output unless a non-Python frontend package reference is intentionally added later.
- `git grep -n "@/bright-byte-web\\|@/bright-byte-live" -- apps` returns no output.
- `git grep -n "@/plane-web\\|@/plane-live" -- apps/web apps/live` still returns the known edition seam references.
- `git grep -n "PiChatLogo\\|sub-brand\\.pi-chat\\|pi_chat\\|GptAssistantPopover\\|gpt-assistant-popover\\|/pi-chat" -- apps packages` returns no output, except historical planning artifacts if the command is intentionally scoped wider than source.
- `git diff -- LICENSE.txt COPYRIGHT.txt` is empty.
- `git diff | grep -E "^[-+].*(Copyright \\(c\\) 2023-present Plane Software|SPDX-License-Identifier: AGPL-3.0-only)"` returns no output.

### Acceptance Gate

The phase is not complete unless all of these pass:

- `pnpm install`
- `pnpm --filter @bright-byte/codemods run test`
- `pnpm build`
- `pnpm check:types`
- `pnpm check:lint`
- Source-scoped residual grep gates above

## Planning Guidance

Use one `PLAN.md`, not multiple implementation plans. The executor may use internal task checkpoints, but the code rename itself must not be committed or considered complete until package names, consumers, imports, lockfile, and AI identifiers are all green together.
