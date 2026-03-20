# Tasks: Launcher Flow

**Input**: Design documents from `/specs/003-launcher-flow/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Role Boards

- [ ] T001 Add a read-only role board renderer in `src/codex_orchestrator/dashboard.py`.
- [ ] T002 Add CLI surface in `src/codex_orchestrator/cli.py` for rendering a role board.
- [ ] T003 Add automated tests in `tests/test_dashboard.py` and `tests/test_cli.py` for role-board rendering.
- [ ] T004 Run `./scripts/test.sh` and smoke `install -> board -> panel`.
- [ ] T005 Commit the role-board slice as an isolated reviewable unit.

## Phase 2: Launcher Seeds

- [ ] T006 Add launcher script template/rendering logic in `src/codex_orchestrator/launchers.py`.
- [ ] T007 Extend project scaffold generation in `src/codex_orchestrator/generator.py` to create launcher script seeds and backfill missing ones on rerun.
- [ ] T008 Add automated tests in `tests/test_generator.py` for launcher seed generation and preservation behavior.
- [ ] T009 Run `./scripts/test.sh` and smoke generated launcher artifacts.
- [ ] T010 Commit the launcher-seed slice as a second isolated reviewable unit.

## Phase 3: Docs Sync

- [ ] T011 Sync README, HANDOFF, and relevant feature docs with the implemented launcher flow behavior.
- [ ] T012 Commit the launcher docs sync as a final isolated reviewable unit.
