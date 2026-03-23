# Implementation Plan: Dispatch Lifecycle

**Feature**: `002-dispatch-lifecycle` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-dispatch-lifecycle/spec.md`

## Summary

현재 queue enqueue와 seeded panel 위에 다음 두 가지를 추가한다.

1. queue command를 dispatch ticket으로 여는 mutation
2. dispatch 결과를 queue / ledger / runtime state에 반영하는 mutation

이번 단계에서는 live launcher를 붙이지 않고, launcher가 소비할 수 있는 파일 기반 lifecycle을 먼저 닫는다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Python standard library only  
**Storage**: local filesystem under `.codex/subagent-kit/runtime`, `.codex/subagent-kit/queue`, `.codex/subagent-kit/ledger`  
**Testing**: `./scripts/test.sh` and focused CLI smoke commands  
**Target Platform**: local terminal environments on macOS/Linux  
**Project Type**: CLI/TUI utility with file-based control-plane  
**Performance Goals**: state mutations should remain effectively instant for small local teams  
**Constraints**: keep legacy shell assets as reference only, preserve current CLI behavior, keep state files human-readable  
**Scale/Scope**: single local project team with one orchestrator and a small number of workers

## Constitution Check

- `Codex-Native First`: pass. lifecycle remains in local `.codex/subagent-kit`.
- `Local-Over-Global Defaults`: pass. lifecycle mutations are project-local.
- `Static Definition and Runtime State Separation`: pass. agent definitions stay in `.codex/agents`, lifecycle stays in `.codex/subagent-kit`.
- `Reference Assets Are Seeds, Not Runtime`: pass if dispatch state logic is implemented in `src/codex_subagent_kit/`.
- `Re-runnable Generation and Clear Output`: pass if mutation commands report ids and paths clearly.
- `Testable Changes and Explicit Validation`: pass if queue/dispatch/result transitions are covered by tests and smoke.

## Project Structure

### Documentation (this feature)

```text
specs/002-dispatch-lifecycle/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── spec.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── codex_subagent_kit/
    ├── cli.py
    ├── control_plane.py
    ├── generator.py
    └── panel.py

tests/
├── test_cli.py
├── test_control_plane.py
└── test_panel.py
```

**Structure Decision**: keep lifecycle mutations in `control_plane.py`, keep `panel.py` as read-only renderer, and extend `cli.py` with thin user-facing commands.

## Complexity Tracking

No constitution violations are expected for this feature.
