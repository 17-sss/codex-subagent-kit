# Tasks: Dispatch Lifecycle

**Input**: Design documents from `/specs/002-dispatch-lifecycle/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Dispatch Open

- [x] T001 Extend `src/codex_orchestrator/control_plane.py` with queue-command selection and dispatch-ticket creation.
- [x] T002 Add CLI surface in `src/codex_orchestrator/cli.py` for opening a dispatch from the current queue state.
- [x] T003 Update tests in `tests/test_control_plane.py`, `tests/test_cli.py`, and `tests/test_panel.py` for queue-to-dispatch transitions.
- [x] T004 Run `./scripts/test.sh` and smoke `install -> enqueue -> dispatch-open -> panel`.
- [x] T005 Commit the dispatch-open slice as an isolated reviewable unit.

## Phase 2: Result Apply

- [x] T006 Extend `src/codex_orchestrator/control_plane.py` with result-apply transitions for `completed`, `failed`, and `cancelled`.
- [x] T007 Update runtime-state mutation so active roles return to the correct post-result status.
- [x] T008 Add CLI surface in `src/codex_orchestrator/cli.py` for applying a dispatch result.
- [x] T009 Update automated tests for ledger, queue, runtime, and panel consistency after result application.
- [x] T010 Run `./scripts/test.sh` and smoke `install -> enqueue -> dispatch-open -> apply-result -> panel`.
- [x] T011 Commit the result-apply slice as a second isolated reviewable unit.

## Phase 3: Docs Sync

- [x] T012 Sync README, HANDOFF, and relevant feature docs with the implemented dispatch lifecycle behavior.
- [x] T013 Commit the lifecycle docs sync as a final isolated reviewable unit.
