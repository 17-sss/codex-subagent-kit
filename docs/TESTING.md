# TESTING

Korean version: [TESTING.ko.md](./TESTING.ko.md)

## Goal

The testing workflow for `codex-subagent-kit` protects three things:

- stable CLI and TUI flows should remain usable from the packaged TypeScript surface
- generated TOML and template output should keep their contract
- validation commands should catch malformed TOML before the user reaches Codex
- independent validation promised in SDD documents should carry through to implementation

## GitHub Actions CI

The repository also has a pull-request CI workflow for visibility before merge.

- workflow file: [ci.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/ci.yml)
- trigger: `pull_request` targeting `main`
- manual trigger: `workflow_dispatch`
- repository gate: `npm ci` followed by `./scripts/test.sh`
- packaged consumer smoke: included inside `./scripts/test.sh`

## Core Principles

- if a change affects user experience or generated output, leave behind either automated coverage or an explicit manual smoke procedure
- automate in the package test suite whenever practical
- for TUI changes that are harder to automate fully, keep both automated checks and one manual smoke
- for bug fixes and regressions, add a reproduction test first when possible; if not possible, document the reason and the manual validation path
- for stable CLI and generated-output contracts, prefer a small number of golden fixtures over many fragile one-off assertions

## Testing Workflow Inside SDD

### 1. Spec

- write an `Independent Test` for each user story
- include edge cases and failure conditions in `spec.md`

### 2. Plan

- list concrete validation commands in the `Testing` section of `plan.md`
- distinguish automated checks from manual checks

### 3. Tasks

- keep test tasks under the same story as the implementation tasks
- where possible, add the test first, confirm failure, and then implement

### 4. Implementation

- validate pure logic and generator behavior with the TypeScript package tests
- validate CLI commands through stdout, stderr, and generated artifacts
- for TUI changes, automate pure helpers and pure logic first, then finish with one interactive smoke pass

### 5. Validation

Default gate:

```bash
./scripts/test.sh
```

Integration smoke:

```bash
npm install
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js catalog
node packages/codex-subagent-kit/dist/cli.js catalog sync \
  --scope project \
  --project-root .tmp-smoke \
  --source-root /path/to/awesome-codex-subagents
node packages/codex-subagent-kit/dist/cli.js catalog import \
  --scope project \
  --project-root .tmp-smoke \
  --catalog-root /path/to/categories \
  --agents custom-helper
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root .tmp-smoke \
  --agents reviewer,code-mapper \
  --validate
node packages/codex-subagent-kit/dist/cli.js doctor \
  --scope project \
  --project-root .tmp-smoke
```

Additional checks for TUI changes:

- run `node packages/codex-subagent-kit/dist/cli.js tui --project-root <tmp-dir>` inside a PTY
- confirm that the flow reaches agent generation through real key input

## Current Automated Coverage

- catalog structure and key consistency
- VoltAgent-backed built-in snapshot availability and local `catalog sync` flows
- persistent catalog import for selected agents, full categories, and rerun preservation
- generator file creation, preservation, and error handling
- doctor validation for healthy installs, malformed files, and missing explicit catalog roots
- install-time validation via `install --validate`
- golden fixtures for representative generated TOML, `usage` output, and `doctor` output
- CLI flows for `catalog`, `catalog sync`, `catalog import`, `install`, and root path handling
- pure helper coverage around TUI default selection and project validation rules

## Current Limits

- the full TUI flow is not fully automated end-to-end
- keep consumer smoke and one manual TUI pass in the release checklist
