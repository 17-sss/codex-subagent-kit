# Tasks: Install Validation

## Phase 1: CLI Flow

- [x] Add an optional `--validate` flag to `install`.
- [x] Reuse `doctor` after successful install and propagate validation failure as a non-zero exit code.

## Phase 2: Validation / Docs

- [x] Add automated tests for successful validated installs and failing validated installs.
- [x] Update README and testing docs with the combined install-and-validate workflow.
