# Feature Specification: Dispatch Handoff

**Feature**: `005-dispatch-handoff`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description: "queue / dispatch lifecycle를 실제 agent I/O와 닿게 만들되, 제품 CLI 안에서는 main Codex conversation이 `send_input` 하기 직전 단계까지를 표준화한다."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prepare a ready-to-send dispatch package (Priority: P1)

operator나 coordinator는 `ready` dispatch를 실제 subagent에게 넘기기 전에, role / command / role-definition path가 포함된 준비된 payload를 CLI에서 바로 얻고 싶다.

**Why this priority**: 지금 control-plane은 `dispatch-open`까지만 있고, 그 다음 실제 전달 메시지는 매번 사람이 임의로 조립해야 한다. 이 빈칸이 가장 먼저 메워져야 한다.

**Independent Test**: ready dispatch를 만든 뒤 `dispatch-prepare --dispatch-id ...`를 실행했을 때 dispatch id, role, command 요약, role definition path, suggested send_input payload가 출력되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** project-local team에 `ready` dispatch가 있을 때, **When** 사용자가 `dispatch-prepare`를 실행하면, **Then** 시스템은 해당 dispatch의 handoff brief와 suggested send_input message를 출력해야 한다.
2. **Given** dispatch가 특정 worker role을 가리킬 때, **When** 출력을 확인하면, **Then** 현재 project-local role definition path와 command summary가 함께 보여야 한다.
3. **Given** dispatch가 root orchestrator role을 가리킬 때, **When** 출력을 확인하면, **Then** top-level orchestrator 역할이라는 점이 드러나야 한다.

---

### User Story 2 - Mark a prepared dispatch as in-flight (Priority: P1)

main Codex conversation이 실제 `send_input`을 보낸 직후에는, control-plane 상태도 `ready`에서 `dispatched`로 넘어가야 한다.

**Why this priority**: `ready`와 `dispatched`를 구분하지 않으면 dashboard와 lifecycle이 실제 운영 상태를 반영하지 못한다.

**Independent Test**: ready dispatch에 대해 `dispatch-begin --dispatch-id ...`를 실행했을 때 queue, ledger, runtime이 `dispatched` in-flight 상태를 반영하면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** `ready` dispatch가 있을 때, **When** 사용자가 `dispatch-begin`을 실행하면, **Then** dispatch status는 `dispatched`로 바뀌어야 한다.
2. **Given** 같은 dispatch를 가리키는 queue command가 있을 때, **When** `dispatch-begin`이 끝나면, **Then** queue command status도 `dispatched`로 바뀌어야 한다.
3. **Given** panel을 다시 렌더링할 때, **When** 상태를 확인하면, **Then** queue와 dispatch summary가 `dispatched`를 포함해야 한다.

---

### User Story 3 - Keep the live tool boundary explicit (Priority: P2)

개발자는 제품 CLI가 마치 실제 `send_input` / `wait_agent`까지 자동으로 해주는 것처럼 보이지 않길 원한다.

**Why this priority**: 현재 아키텍처에서 실제 live tool 호출은 main Codex conversation이 수행해야 한다. 이 경계가 흐려지면 제품 설명과 실제 능력이 어긋난다.

**Independent Test**: `dispatch-prepare`와 `dispatch-begin`이 명확히 "handoff bridge" 역할로 동작하고, 실제 agent I/O는 여전히 외부 단계라는 점이 문서와 CLI에서 일관되게 드러나면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 사용자가 `dispatch-prepare` 출력을 볼 때, **When** 마지막 안내를 읽으면, **Then** 이 payload는 main Codex conversation이 실제 `send_input`에 사용할 메시지라는 점이 드러나야 한다.
2. **Given** `dispatch-begin`을 실행했을 때, **When** 상태를 확인하면, **Then** 시스템은 lifecycle만 갱신하고 실제 agent result는 `apply-result` 단계에서 별도로 반영하게 유지해야 한다.

## Edge Cases

- `dispatch-prepare`는 존재하지 않는 dispatch id에 대해 명확한 오류를 반환해야 한다.
- `dispatch-begin`은 `ready` 상태가 아닌 dispatch에 대해 명확한 오류를 반환해야 한다.
- role definition path가 project-local TOML로 해석되지 않더라도, 최소한 role key와 description은 출력 가능해야 한다.
- 기존 `apply-result`는 `dispatched` 상태의 dispatch에도 계속 동작해야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a `dispatch-prepare` CLI command for rendering a ready dispatch handoff package.
- **FR-002**: System MUST expose a `dispatch-begin` CLI command for marking a `ready` dispatch as `dispatched`.
- **FR-003**: System MUST include role key, command id, dispatch id, priority, source, and command summary in the prepared handoff output.
- **FR-004**: System MUST include the current role definition path when it is available from project/global agent discovery.
- **FR-005**: System MUST distinguish `ready` and `dispatched` states in queue/dispatch lifecycle data.
- **FR-006**: System MUST keep actual agent result handling in the existing `apply-result` phase rather than folding it into `dispatch-begin`.
- **FR-007**: System MUST keep the handoff output vendor-neutral and rooted in current project metadata.

### Key Entities *(include if feature involves data)*

- **Dispatch Handoff Package**: coordinator가 main Codex conversation으로 넘길 준비된 dispatch brief와 suggested send_input payload.
- **In-Flight Dispatch**: 이미 실제 agent로 전달됐다고 간주되어 `dispatched` status를 가진 dispatch/queue pair.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자는 `dispatch-open -> dispatch-prepare -> dispatch-begin -> apply-result` 흐름을 CLI로 순차 수행할 수 있다.
- **SC-002**: `dispatch-prepare` 출력만으로 main Codex conversation이 다음 `send_input` payload를 조립하지 않고 바로 사용할 수 있다.
- **SC-003**: automated tests와 최소 `enqueue -> dispatch-open -> dispatch-prepare -> dispatch-begin -> panel` smoke가 성공해야 한다.
- **SC-004**: panel summary가 queue `dispatched` 상태를 보여준다.
