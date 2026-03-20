# Implementation Plan: Orchestrator Scaffold Generation

**Branch**: `001-orchestrator-scaffold` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-orchestrator-scaffold/spec.md`

## Summary

현재 installer MVP를 확장해 다음 두 가지를 구현한다.

1. built-in agent output을 VoltAgent-style Codex-compatible TOML에 가깝게 정렬한다.
2. project-scope install 시 `.codex/orchestrator` scaffold와 root orchestrator가 명시된 team manifest seed를 함께 생성한다.

이번 단계에서는 terminal control panel 전체를 구현하지 않고, 그 기반이 되는 canonical format, team topology, scaffold seed까지만 책임진다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Python standard library only  
**Storage**: local filesystem under `.codex/agents` and `.codex/orchestrator`  
**Testing**: `python3 -m compileall src`, `PYTHONPATH=src python3 -m unittest discover -s tests -v`  
**Target Platform**: local terminal environments on macOS/Linux  
**Project Type**: CLI/TUI utility  
**Performance Goals**: install/catalog operations should remain effectively instant for small local team definitions  
**Constraints**: preserve current CLI/TUI flow, keep reference shell assets as read-only seeds, avoid vendor-specific defaults  
**Scale/Scope**: single-repo Python package with tens of agent definitions, local project/global installation

## Constitution Check

### Before Phase 0

- `Codex-Native First`: pass. output remains local `.codex` assets.
- `Local-Over-Global Defaults`: pass. scaffold is project-scope only.
- `Static Definition and Runtime State Separation`: pass. `.codex/agents` and `.codex/orchestrator` stay separate.
- `Reference Assets Are Seeds, Not Runtime`: pass. legacy shell assets remain reference only.
- `Re-runnable Generation and Clear Output`: pass if created/skipped/preserved paths are reported.
- `Testable Changes and Explicit Validation`: pass if TOML rendering and scaffold generation are covered by unit tests plus CLI smoke.

### After Phase 1

- No constitution exception is currently expected.

## Project Structure

### Documentation (this feature)

```text
specs/001-orchestrator-scaffold/
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
    ├── catalog.py
    ├── cli.py
    ├── generator.py
    ├── models.py
    └── tui.py

tests/
├── test_catalog.py
├── test_cli.py
└── test_generator.py
```

**Structure Decision**: keep the current single-package CLI/TUI structure. Add scaffold-generation logic next to the existing generator/install flow rather than introducing a new package.

## Complexity Tracking

No constitution violations are expected for this feature.
