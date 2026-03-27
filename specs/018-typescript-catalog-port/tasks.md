# Tasks: TypeScript Catalog Port

> Historical note: superseded in source-of-truth terms by [031-voltagent-catalog-sync](../031-voltagent-catalog-sync/spec.md).

## Phase 1: Shared Helpers

- [x] Add TypeScript model definitions for categories, agents, and catalog options.
- [x] Add TypeScript path helpers for project/global tool, catalog, and agent directories.
- [x] Vendor the app-owned built-in catalog assets into the TypeScript workspace.

## Phase 2: Catalog Command

- [x] Port catalog loading, parsing, and precedence handling into the TypeScript package.
- [x] Wire the `catalog` CLI command to the new TypeScript catalog renderer.

## Phase 3: Validation

- [x] Add TypeScript tests for built-in catalog discovery.
- [x] Add TypeScript tests for external catalog roots and project/global agent overrides.
