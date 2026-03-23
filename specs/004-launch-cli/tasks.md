# Tasks: Launch CLI

**Input**: Design documents from `/specs/004-launch-cli/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Launch Runtime

- [x] T001 Add launcher resolution and execution wrapper in `src/codex_subagent_kit/launch_runtime.py`.
- [x] T002 Add `launch` CLI surface in `src/codex_subagent_kit/cli.py`.
- [x] T003 Add automated tests in `tests/test_launch_runtime.py` and `tests/test_cli.py` for dry-run and validation errors.
- [x] T004 Run `./scripts/test.sh` and smoke `install -> launch --dry-run`.
- [x] T005 Commit the launch-runtime slice as an isolated reviewable unit.

## Phase 2: Docs Sync

- [x] T006 Sync README, HANDOFF, and relevant feature docs with the implemented launch CLI behavior.
- [x] T007 Commit the launch CLI docs sync as a final isolated reviewable unit.
