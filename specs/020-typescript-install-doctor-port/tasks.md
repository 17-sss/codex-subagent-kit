# Tasks: TypeScript Install And Doctor Port

## Phase 1: Installation

- [x] Port install target resolution and agent file rendering to TypeScript.
- [x] Port the current project-scope scaffold generation required by install.
- [x] Wire the TypeScript CLI `install` command to the new implementation.

## Phase 2: Validation

- [x] Port doctor scanning and report rendering to TypeScript.
- [x] Wire `doctor` and `install --validate` to the new implementation.

## Phase 3: Validation

- [x] Add TypeScript tests for install success and orchestrator requirements.
- [x] Add TypeScript tests for external catalog-root installs.
- [x] Add TypeScript tests for doctor success and malformed-agent reporting.
