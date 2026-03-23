# Implementation Plan: Launch CLI

**Feature**: `004-launch-cli` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-launch-cli/spec.md`

## Summary

현재 project-local launcher seed 위에 다음 두 가지를 추가한다.

1. `codex-subagent-kit launch --backend tmux|cmux` CLI surface
2. generated launcher file을 검증하고 실행하거나, `--dry-run`으로 preview하는 Python wrapper

이번 단계에서는 live queue drain이나 actual `spawn_agent` orchestration을 붙이지 않고, generated shell launcher를 first-class entrypoint로 승격하는 데 집중한다.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Python standard library only  
**Storage**: local filesystem under `.codex/subagent-kit/`  
**Testing**: `./scripts/test.sh` and focused CLI smoke commands  
**Target Platform**: local terminal environments on macOS/Linux  
**Project Type**: CLI/TUI utility with file-based control-plane  
**Performance Goals**: launch resolution and dry-run output should be effectively instant  
**Constraints**: keep launcher execution project-local, preserve script-driven backend soft-fail, avoid duplicating launcher template logic in runtime wrapper  
**Scale/Scope**: one root orchestrator team per project, one backend launch per CLI invocation

## Constitution Check

- `Codex-Native First`: pass. CLI entrypoint still consumes `.codex/subagent-kit` state in the current project.
- `Local-Over-Global Defaults`: pass. launch CLI is project-local only.
- `Static Definition and Runtime State Separation`: pass. runtime wrapper only resolves launchers, not agent definitions.
- `Reference Assets Are Seeds, Not Runtime`: pass. runtime wrapper calls generated project-local launchers, not legacy shell assets.
- `Re-runnable Generation and Clear Output`: pass if missing scaffold errors are explicit and dry-run output is clear.
- `Testable Changes and Explicit Validation`: pass if dry-run and error paths are covered by tests plus smoke.

## Project Structure

### Documentation (this feature)

```text
specs/004-launch-cli/
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
    ├── launch_runtime.py
    └── launchers.py

tests/
├── test_cli.py
└── test_launch_runtime.py
```

**Structure Decision**: keep launcher template generation in `launchers.py`, add a small `launch_runtime.py` wrapper for script resolution and execution, and expose it through `cli.py`.

## Complexity Tracking

No constitution violations are expected for this feature.
