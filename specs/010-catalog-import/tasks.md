# Tasks: Catalog Import

## Phase 1: Import Logic

- [x] Add a catalog import module that scans explicit source roots and copies selected categories or agents into project/global injection targets.
- [x] Preserve existing target files by default and support explicit overwrite.

## Phase 2: CLI

- [x] Add a stable `catalog import` command below the existing `catalog` surface.
- [x] Render clear output for imported categories, imported agents, created files, and preserved files.

## Phase 3: Validation / Docs

- [x] Add automated tests for agent import, category import, and rerun preservation behavior.
- [x] Update README and testing docs with the new persistent import workflow.
