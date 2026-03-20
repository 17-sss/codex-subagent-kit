# Implementation Plan: Launcher Flow

**Feature**: `003-launcher-flow` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-launcher-flow/spec.md`

## Summary

현재 queue / dispatch / runtime lifecycle 위에 다음 두 가지를 추가한다.

1. orchestrator 또는 worker별 read-only terminal board
2. `.codex/orchestrator/launchers/` 아래 project-local launcher script seed

이번 단계에서는 actual `spawn_agent` orchestration까지 하지 않고, shared state를 읽는 terminal dashboard path를 먼저 닫는다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Python standard library only  
**Storage**: local filesystem under `.codex/orchestrator/`  
**Testing**: `./scripts/test.sh` and focused CLI smoke commands  
**Target Platform**: local terminal environments on macOS/Linux  
**Project Type**: CLI/TUI utility with file-based control-plane  
**Performance Goals**: board/panel rendering should remain effectively instant for small local teams  
**Constraints**: keep legacy shell assets as reference only, soft-fail optional backends, preserve existing launcher scripts on rerun  
**Scale/Scope**: single project-local team with one root orchestrator and a small number of workers

## Constitution Check

- `Codex-Native First`: pass. dashboard state remains under `.codex/orchestrator`.
- `Local-Over-Global Defaults`: pass. launcher flow is project-local.
- `Static Definition and Runtime State Separation`: pass. boards consume runtime state only.
- `Reference Assets Are Seeds, Not Runtime`: pass if generated launchers are rendered from Python code, not copied from legacy shell.
- `Re-runnable Generation and Clear Output`: pass if missing launchers backfill and preserved launchers are reported.
- `Testable Changes and Explicit Validation`: pass if board rendering and launcher generation are covered by tests plus smoke.

## Project Structure

### Documentation (this feature)

```text
specs/003-launcher-flow/
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
└── codex_orchestrator/
    ├── cli.py
    ├── dashboard.py
    ├── generator.py
    └── launchers.py

tests/
├── test_cli.py
├── test_dashboard.py
└── test_generator.py
```

**Structure Decision**: keep read-only terminal rendering in a dedicated `dashboard.py` module and keep launcher script template/rendering in `launchers.py`, with `generator.py` responsible for writing those seeds into the scaffold.

## Complexity Tracking

No constitution violations are expected for this feature.
