# Tasks: Dispatch Handoff

**Input**: Design documents from `/specs/005-dispatch-handoff/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Handoff Runtime

- [ ] T001 Add dispatch handoff rendering and `dispatched` lifecycle mutation in `src/codex_orchestrator/control_plane.py`.
- [ ] T002 Add `dispatch-prepare` and `dispatch-begin` CLI surfaces in `src/codex_orchestrator/cli.py`.
- [ ] T003 Extend panel queue summary in `src/codex_orchestrator/panel.py` to show `dispatched`.
- [ ] T004 Add automated tests in `tests/test_control_plane.py`, `tests/test_cli.py`, and `tests/test_panel.py`.
- [ ] T005 Run `./scripts/test.sh` and smoke `enqueue -> dispatch-open -> dispatch-prepare -> dispatch-begin -> panel`.
- [ ] T006 Commit the handoff-runtime slice as an isolated reviewable unit.

## Phase 2: Docs Sync

- [ ] T007 Sync README, HANDOFF, and relevant feature docs with the implemented dispatch handoff behavior.
- [ ] T008 Commit the dispatch handoff docs sync as a final isolated reviewable unit.
