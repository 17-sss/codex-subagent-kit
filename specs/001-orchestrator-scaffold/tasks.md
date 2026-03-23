# Tasks: Orchestrator Scaffold Generation

**Input**: Design documents from `/specs/001-orchestrator-scaffold/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Foundation

- [x] T001 Align canonical agent TOML output in `src/codex_subagent_kit/generator.py` with the chosen Codex-compatible structure.
- [x] T002 Add or update automated tests in `tests/test_generator.py` and `tests/test_cli.py` to lock the new TOML rendering contract.
- [x] T003 Commit the canonical TOML change as an isolated reviewable unit.

## Phase 2: Orchestrator Seed

- [x] T004 Add team manifest and scaffold generation logic in `src/codex_subagent_kit/generator.py` for project-scope installs.
- [x] T005 Ensure the seed manifest contains one explicit root orchestrator and the remaining worker agents.
- [x] T006 Report created and preserved scaffold paths in CLI output from `src/codex_subagent_kit/cli.py`.
- [x] T007 Add or update automated tests covering scaffold generation, scope behavior, and re-run behavior.
- [x] T008 Commit the scaffold generation change as a second isolated reviewable unit.

## Phase 3: TUI Integration And Docs

- [x] T009 Update `src/codex_subagent_kit/tui.py` so project-scope install still works cleanly with scaffold generation and root orchestrator rules.
- [x] T010 Sync README, HANDOFF, and feature docs with the implemented behavior.
- [x] T011 Run `./scripts/test.sh` plus CLI/TUI smoke validation and commit the integration/docs finish as a third isolated reviewable unit.
