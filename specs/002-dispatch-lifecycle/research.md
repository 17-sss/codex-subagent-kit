# Research: Dispatch Lifecycle

## Decision 1: Queue and dispatch stay as separate files

- **Decision**: keep `queue/commands.toml` and `ledger/dispatches.toml` as separate sources of truth.
- **Rationale**: queue command는 backlog, dispatch ticket은 실제 배정 시도라는 의미가 다르다. legacy reference도 이 둘을 분리한다.
- **Alternatives considered**:
  - single unified task file: simpler at first, but lifecycle semantics가 금방 섞인다.

## Decision 2: Implement mutation logic in Python, not shell wrappers

- **Decision**: dispatch open / result apply는 `src/codex_orchestrator/control_plane.py`에 구현한다.
- **Rationale**: 이 프로젝트의 source of truth는 Python package여야 하고, legacy shell은 참고만 해야 한다.
- **Alternatives considered**:
  - shell script reuse: 빠를 수는 있지만, 새 제품의 canonical runtime과 다시 분리된다.

## Decision 3: Keep panel as a consumer, not a mutator

- **Decision**: `panel`은 상태를 읽기만 하고, lifecycle 변경은 별도 CLI 명령이 담당한다.
- **Rationale**: 읽기와 쓰기를 분리하면 테스트가 단순해지고, launcher가 나중에 같은 상태를 소비하기 쉽다.
- **Alternatives considered**:
  - panel command with embedded actions: UX는 짧아질 수 있으나 책임이 빨리 커진다.
