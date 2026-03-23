# Tasks: Doctor Validation

## Phase 1: Validation Logic

- [x] Add a doctor module that validates catalog roots and installed agent TOML files for the selected scope.
- [x] Report malformed files with actionable path-based issues.

## Phase 2: CLI

- [x] Add a stable `doctor` command to the CLI surface.
- [x] Return a non-zero exit code when issues are found.

## Phase 3: Validation / Docs

- [x] Add automated tests for healthy installs, malformed files, and missing explicit catalog roots.
- [x] Update README and testing docs with the new validation workflow.
