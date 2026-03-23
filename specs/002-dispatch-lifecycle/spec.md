# Feature Specification: Dispatch Lifecycle

**Feature**: `002-dispatch-lifecycle`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description: "현재 queue enqueue와 panel seed까지 왔으니, 다음은 queue command를 dispatch ticket으로 열고 결과를 적용해 runtime/ledger/panel이 함께 움직이게 한다."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open a dispatch from a queued command (Priority: P1)

operator는 queue에 넣은 command를 실제 작업 단위인 dispatch ticket으로 승격할 수 있어야 한다.

**Why this priority**: `enqueue`만 있고 dispatch가 없으면 control-plane이 backlog 보관함에 머문다. 다음 단계의 최소 실체는 queue에서 dispatch ledger로 넘어가는 전이다.

**Independent Test**: project scaffold가 있는 디렉터리에서 queue command를 하나 넣은 뒤 dispatch open 명령을 실행했을 때 queue status와 ledger entry가 함께 갱신되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** project queue에 `pending` command가 하나 이상 있을 때, **When** 사용자가 dispatch open 명령을 실행하면, **Then** 시스템은 하나의 dispatch ticket을 `ledger/dispatches.toml`에 기록한다.
2. **Given** dispatch ticket이 열렸을 때, **When** queue command를 다시 보면, **Then** 원본 command는 더 이상 단순 `pending`이 아니고 dispatch와 연결된 상태로 갱신된다.
3. **Given** 사용자가 panel을 다시 렌더링할 때, **When** queue/ledger summary를 확인하면, **Then** queue와 dispatch 카운트가 방금 열린 dispatch를 반영한다.

---

### User Story 2 - Apply agent results back into runtime state (Priority: P1)

operator 또는 main Codex는 dispatch 결과를 control-plane 파일에 반영해 다음 상태를 명확히 남길 수 있어야 한다.

**Why this priority**: dispatch를 열기만 하고 끝내면 운영 기록이 쌓이지 않는다. 결과 반영이 있어야 queue, runtime state, panel이 실제 lifecycle을 표현한다.

**Independent Test**: `ready` 또는 `dispatched` 상태의 dispatch에 대해 `completed`, `failed`, `cancelled` 결과 중 하나를 적용했을 때 queue, ledger, runtime 상태가 함께 갱신되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 활성 dispatch가 있을 때, **When** 사용자가 결과 적용 명령을 실행하면, **Then** 시스템은 dispatch 상태를 결과 상태로 바꾼다.
2. **Given** worker가 dispatch를 수행 중이었다고 기록된 상태에서, **When** 결과를 적용하면, **Then** runtime state는 다시 다음 작업을 받을 수 있는 상태로 정리된다.
3. **Given** panel을 다시 렌더링할 때, **When** 결과 반영 직후 상태를 보면, **Then** dispatch/queue/runtime 요약이 최신 결과를 보여준다.

---

### User Story 3 - Keep the lifecycle generic and launcher-ready (Priority: P2)

제품 개발자는 dispatch lifecycle이 특정 shell 스크립트 구현에 묶이지 않으면서, 나중에 `tmux` / `cmux` launcher와 연결할 수 있는 중립적인 파일 흐름이길 원한다.

**Why this priority**: 이 제품은 Python-native control-plane으로 가고 있고, legacy shell 자산은 참고 자료일 뿐이다. dispatch lifecycle도 launcher 독립적인 기준 데이터가 먼저 있어야 한다.

**Independent Test**: 생성된 queue/ledger/runtime 파일만으로 dispatch의 준비, 진행, 결과가 추적 가능하고, 런처 없이도 panel에서 상태를 이해할 수 있으면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 사용자가 lifecycle 파일을 직접 열어 볼 때, **When** queue/ledger/runtime를 확인하면, **Then** 각 파일의 역할이 분명하고 launcher 없이도 상태 흐름을 이해할 수 있어야 한다.
2. **Given** 추후 launcher를 붙이려는 개발자가 있을 때, **When** 이 dispatch lifecycle 데이터를 사용하면, **Then** `tmux` / `cmux`는 이 상태를 소비하는 UI 계층으로 연결될 수 있어야 한다.

## Edge Cases

- queue에 `pending` command가 하나도 없을 때 dispatch open 명령은 명확한 오류를 반환해야 한다.
- 존재하지 않는 `command-id` 또는 `dispatch-id`를 대상으로 한 변경은 실패해야 한다.
- 이미 완료된 dispatch에 다시 결과를 적용하는 동작은 허용하지 않아야 한다.
- runtime seed 파일이 일부 비어 있거나 누락되어도, 현재 scaffold를 복구 가능한 방식으로 처리해야 한다.
- orchestrator 자신을 target으로 한 command와 worker를 target으로 한 command 모두 처리 가능해야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow an operator command already stored in `queue/commands.toml` to be promoted into a dispatch ticket in `ledger/dispatches.toml`.
- **FR-002**: System MUST define a deterministic identifier scheme for queue commands and dispatch tickets so state transitions are traceable.
- **FR-003**: System MUST update queue state when a dispatch ticket is opened from a queued command.
- **FR-004**: System MUST allow a dispatch result to be applied as one of `completed`, `failed`, or `cancelled`.
- **FR-005**: System MUST update ledger, queue, and runtime state together when a dispatch result is applied.
- **FR-006**: System MUST keep the lifecycle file format vendor-neutral and independent from the legacy shell scripts under `reference/legacy_shell_control_plane/`.
- **FR-007**: System MUST expose lifecycle mutations through CLI commands that can be used without the TUI.
- **FR-008**: System MUST keep `panel` output aligned with the latest queue, ledger, and runtime state after each mutation.
- **FR-009**: System MUST reject invalid lifecycle transitions with explicit error output instead of silently rewriting state.
- **FR-010**: System MUST preserve the control-plane hierarchy `operator/user -> orchestrator -> workers` while recording dispatch ownership and outcomes.

### Key Entities *(include if feature involves data)*

- **Queue Command**: operator가 enqueue한 작업 요청. dispatch 전 backlog 단위다.
- **Dispatch Ticket**: 특정 command에서 파생된 실제 작업 배정 단위다.
- **Runtime Agent State**: orchestrator 또는 worker가 현재 `idle`, `busy` 같은 어떤 상태인지 나타내는 파일 기반 상태다.
- **Dispatch Result**: `completed`, `failed`, `cancelled` 중 하나의 결과와 그 요약이다.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자는 queue에 넣은 command를 CLI 한 번으로 dispatch ticket으로 열 수 있다.
- **SC-002**: 결과 적용 후 queue, ledger, runtime state가 서로 모순되지 않는다.
- **SC-003**: `panel`은 dispatch open과 result apply 직후 상태를 올바르게 요약한다.
- **SC-004**: 검증 시 최소한 automated tests와 `install -> enqueue -> dispatch open -> apply result -> panel` smoke가 성공해야 한다.
