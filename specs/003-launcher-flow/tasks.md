# Tasks: Launcher Flow

**Input**: Design documents from `/specs/003-launcher-flow/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Role Boards

- [x] T001 Add a read-only role board renderer in `src/codex_orchestrator/dashboard.py`.
- [x] T002 Add CLI surface in `src/codex_orchestrator/cli.py` for rendering a role board.
- [x] T003 Add automated tests in `tests/test_dashboard.py` and `tests/test_cli.py` for role-board rendering.
- [x] T004 Run `./scripts/test.sh` and smoke `install -> board -> panel`.
- [x] T005 Commit the role-board slice as an isolated reviewable unit.

## Phase 2: Launcher Seeds

- [x] T006 Add launcher script template/rendering logic in `src/codex_orchestrator/launchers.py`.
- [x] T007 Extend project scaffold generation in `src/codex_orchestrator/generator.py` to create launcher script seeds and backfill missing ones on rerun.
- [x] T008 Add automated tests in `tests/test_generator.py` for launcher seed generation and preservation behavior.
- [x] T009 Run `./scripts/test.sh` and smoke generated launcher artifacts.
- [x] T010 Commit the launcher-seed slice as a second isolated reviewable unit.

## Phase 3: Docs Sync

- [x] T011 Sync README, HANDOFF, and relevant feature docs with the implemented launcher flow behavior.
- [x] T012 Commit the launcher docs sync as a final isolated reviewable unit.
