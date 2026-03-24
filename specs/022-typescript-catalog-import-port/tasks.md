# Tasks: TypeScript Catalog Import Port

## Phase 1: Import Engine

- [x] Port external catalog scanning and import planning to TypeScript.
- [x] Port target-root resolution and file-copy behavior for project/global catalog injection paths.

## Phase 2: CLI

- [x] Wire the TypeScript CLI `catalog import` command to the new implementation.

## Phase 3: Validation

- [x] Add TypeScript tests for selected-agent import.
- [x] Add TypeScript tests for full-category import.
- [x] Add TypeScript tests for preserve-without-overwrite behavior.
- [x] Add TypeScript tests for missing-agent rejection.
