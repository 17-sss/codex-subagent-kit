# Implementation Plan: Dispatch Handoff

**Feature**: `005-dispatch-handoff` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-dispatch-handoff/spec.md`

## Summary

현재 `dispatch-open`과 `apply-result` 사이에 비어 있는 handoff 구간을 메운다.

1. `dispatch-prepare`로 ready dispatch의 brief와 suggested send_input payload를 렌더링한다.
2. `dispatch-begin`으로 실제 send 직후 lifecycle을 `dispatched`로 전환한다.

이번 단계에서는 실제 `send_input` / `wait_agent` tool 호출을 자동화하지 않고, main Codex conversation이 개입하기 직전/직후 상태를 제품 CLI로 표준화한다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Python standard library only  
**Storage**: local filesystem under `.codex/subagent-kit/` and `.codex/agents/`  
**Testing**: `./scripts/test.sh` and focused CLI smoke commands  
**Target Platform**: local terminal environments on macOS/Linux  
**Project Type**: CLI/TUI utility with file-based control-plane  
**Performance Goals**: handoff rendering should remain effectively instant for small teams  
**Constraints**: do not fake actual agent I/O, keep handoff vendor-neutral, preserve the existing file-based lifecycle  
**Scale/Scope**: single project-local team with one root orchestrator and a small number of workers

## Constitution Check

- `Codex-Native First`: pass. handoff uses current project-local `.codex` assets only.
- `Local-Over-Global Defaults`: pass. runtime bridge remains project-local.
- `Static Definition and Runtime State Separation`: pass. role definition lookup reads `.codex/agents`, while lifecycle writes stay in `.codex/subagent-kit`.
- `Reference Assets Are Seeds, Not Runtime`: pass. shell reference informs shape, but runtime behavior is implemented in Python.
- `Re-runnable Generation and Clear Output`: pass if CLI errors and handoff text stay explicit.
- `Testable Changes and Explicit Validation`: pass if handoff rendering and dispatched-state transitions are covered by tests plus smoke.

## Project Structure

### Documentation (this feature)

```text
specs/005-dispatch-handoff/
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
    └── panel.py

tests/
├── test_cli.py
├── test_control_plane.py
└── test_panel.py
```

**Structure Decision**: keep handoff rendering and `dispatched` lifecycle mutation in `control_plane.py`, expose them through `cli.py`, and extend `panel.py` so the monitor reflects queue `dispatched` state.

## Complexity Tracking

No constitution violations are expected for this feature.
