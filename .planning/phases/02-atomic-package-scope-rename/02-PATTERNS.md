# Phase 02 Pattern Map

**Phase:** 02 - Atomic Package-Scope Rename
**Created:** 2026-06-01

## Purpose

Map the Phase 02 files to existing local patterns so execution can stay mechanical and avoid inventing new conventions.

## Existing Patterns

### Codemod Transform Pattern

**Analog files**

- `packages/codemods/function-declaration.ts`
- `packages/codemods/remove-directives.ts`
- `packages/codemods/tests/function-declaration.spec.ts`
- `packages/codemods/tests/remove-directives.spec.ts`

**Pattern to follow**

- Export a default `transform(file: FileInfo, api: API, options: Options)`.
- Use `const j = api.jscodeshift; const root = j(file.source);`.
- Return `root.toSource(options)`.
- Test with Vitest and `applyTransform` from `@hypermod/utils`.

**Phase 02 usage**

- Add `packages/codemods/rename-scope.ts`.
- Add `packages/codemods/tests/rename-scope.spec.ts`.
- Add a `rename-scope` script in `packages/codemods/package.json` matching the existing jscodeshift script style.

### Package Manifest Pattern

**Analog files**

- `packages/constants/package.json`
- `packages/propel/package.json`
- `apps/web/package.json`
- `apps/admin/package.json`

**Pattern to follow**

- Internal dependencies use `workspace:*`.
- External dependencies use `catalog:`.
- Package names are scoped for shared packages only.

**Phase 02 usage**

- Change every `@plane/<name>` package name and dependency key to `@bright-byte/<name>`.
- Preserve all dependency values exactly, especially `workspace:*` and `catalog:`.
- Do not rename app package names such as `web`, `admin`, `space`, `live`, or `plane-api` unless they are scoped `@plane/*`.

### TypeScript Config Pattern

**Analog files**

- `apps/web/tsconfig.json`
- `apps/admin/tsconfig.json`
- `packages/constants/tsconfig.json`

**Pattern to follow**

- App/package tsconfigs extend shared presets from `@plane/typescript-config/...`.
- Path aliases like `@/plane-web/*` and `@/plane-live/*` are local edition seams.

**Phase 02 usage**

- Change only `extends` values from `@plane/typescript-config/...` to `@bright-byte/typescript-config/...`.
- Preserve `@/plane-web/*` and `@/plane-live/*` path aliases.

### CSS Import Pattern

**Analog files**

- `apps/web/styles/globals.css`
- `apps/space/styles/globals.css`
- `packages/ui/styles/globals.css`
- `packages/propel/.storybook/tailwind.css`

**Pattern to follow**

- Shared package styles are imported by package subpath through CSS `@import`.

**Phase 02 usage**

- Change `@plane/tailwind-config`, `@plane/editor`, and `@plane/propel` style imports to `@bright-byte/...`.
- Do not change CSS class names or theme values.

### Icon Registry Pattern

**Analog files**

- `packages/propel/src/icons/sub-brand/pi-chat.tsx`
- `packages/propel/src/icons/sub-brand/index.ts`
- `packages/propel/src/icons/registry.ts`
- `packages/propel/src/icons/constants.tsx`

**Pattern to follow**

- Sub-brand icon components are exported from `sub-brand/index.ts`.
- `registry.ts` maps a string key to the component.
- `constants.tsx` lists an icon preview title.

**Phase 02 usage**

- Rename `PiChatLogo` to `ByteLogo`.
- Rename registry key `sub-brand.pi-chat` to `sub-brand.byte`.
- Update consumers in `apps/web/core/components/workspace/sidebar/user-menu.tsx`.

### AI Popover Pattern

**Analog files**

- `apps/web/core/components/core/modals/gpt-assistant-popover.tsx`
- `apps/web/core/components/issues/issue-modal/components/description-editor.tsx`
- `apps/web/core/components/issues/issue-modal/form.tsx`
- `apps/web/core/services/ai.service.ts`

**Pattern to follow**

- Component state is passed from issue modal form into description editor.
- AI service URL is centralized in `ai.service.ts`.

**Phase 02 usage**

- Rename component/file/state identifiers to Byte naming.
- Preserve the service endpoint `/api/workspaces/${workspaceSlug}/ai-assistant/`.
