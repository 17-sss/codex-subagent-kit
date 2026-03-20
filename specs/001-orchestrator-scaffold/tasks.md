# Tasks: Orchestrator Scaffold Generation

**Input**: Design documents from `/specs/001-orchestrator-scaffold/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Foundation

- [ ] T001 Align canonical agent TOML output in `src/codex_orchestrator/generator.py` with the chosen Codex-compatible structure.
- [ ] T002 Add or update automated tests in `tests/test_generator.py` and `tests/test_cli.py` to lock the new TOML rendering contract.
- [ ] T003 Commit the canonical TOML change as an isolated reviewable unit.

## Phase 2: Orchestrator Seed

- [ ] T004 Add team manifest and scaffold generation logic in `src/codex_orchestrator/generator.py` for project-scope installs.
- [ ] T005 Ensure the seed manifest contains one explicit root orchestrator and the remaining worker agents.
- [ ] T006 Report created and preserved scaffold paths in CLI output from `src/codex_orchestrator/cli.py`.
- [ ] T007 Add or update automated tests covering scaffold generation, scope behavior, and re-run behavior.
- [ ] T008 Commit the scaffold generation change as a second isolated reviewable unit.

## Phase 3: TUI Integration And Docs

- [ ] T009 Update `src/codex_orchestrator/tui.py` so project-scope install still works cleanly with scaffold generation and root orchestrator rules.
- [ ] T010 Sync README, HANDOFF, and feature docs with the implemented behavior.
- [ ] T011 Run `./scripts/test.sh` plus CLI/TUI smoke validation and commit the integration/docs finish as a third isolated reviewable unit.
