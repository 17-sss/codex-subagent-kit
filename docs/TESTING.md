# TESTING

Korean version: [TESTING.ko.md](./TESTING.ko.md)

## Goal

The testing workflow for `codex-orchestrator` protects three things:

- new work should not break existing CLI and TUI flows
- generator changes should preserve rerun safety and output contracts
- validation commands should catch malformed TOML before the user reaches Codex
- independent validation promised in SDD documents should carry through to implementation

## Core Principles

- if a change affects user experience or generated output, leave behind either automated coverage or an explicit manual smoke procedure
- automate in `tests/` with `unittest` whenever practical
- for changes like the curses TUI that are harder to automate fully, keep both automated checks and manual PTY smoke
- for bug fixes and regressions, add a reproduction test first when possible; if not possible, document the reason and the manual validation path

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

- validate pure logic and generator behavior with `unittest` under `tests/`
- validate CLI commands through stdout, stderr, and generated artifacts
- for TUI changes, automate pure helpers and pure logic first, then finish with a PTY smoke pass

### 5. Validation

Default gate:

```bash
python3 -m compileall src
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Integration smoke:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog import \
  --scope project \
  --project-root .tmp-smoke \
  --catalog-root /path/to/categories \
  --agents custom-helper
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --project-root .tmp-smoke \
  --agents cto-coordinator,reviewer \
  --validate
PYTHONPATH=src python3 -m codex_orchestrator.cli doctor \
  --scope project \
  --project-root .tmp-smoke
```

Additional checks for TUI changes:

- run `PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root <tmp-dir>` inside a PTY
- confirm that the flow reaches agent generation through real key input

## Current Automated Coverage

- catalog structure and key consistency
- persistent catalog import for selected agents, full categories, and rerun preservation
- generator file creation, preservation, and error handling
- doctor validation for healthy installs, malformed files, and missing explicit catalog roots
- install-time validation via `install --validate`
- CLI flows for `catalog`, `install`, control-plane mutations, launcher preview, and dispatch handoff
- pure helper coverage around TUI default selection and project validation rules

## Current Limits

- the full TUI flow is not fully automated end-to-end
- as `.codex/orchestrator` behavior grows, keep expanding coverage for scaffold, queue/dispatch, launcher, and runtime contracts
