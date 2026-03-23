# Feature Specification: Launch CLI

**Feature**: `004-launch-cli`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description: "generated launcher seed를 직접 실행하거나 래핑하는 first-class launch CLI를 추가한다. 사용자는 project install 이후 `codex-subagent-kit launch ...`만으로 terminal backend를 열 수 있어야 한다."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Launch the project control panel from one CLI entrypoint (Priority: P1)

operator나 개발자는 generated shell script 경로를 직접 찾아 실행하지 않고, `codex-subagent-kit launch`만으로 project-local terminal control panel backend를 열 수 있어야 한다.

**Why this priority**: launcher seed만 있으면 기능은 존재하지만 진입점이 분산된다. 제품 사용감 기준으로는 CLI surface가 있어야 실제 기능으로 볼 수 있다.

**Independent Test**: project install 이후 `launch --backend tmux --dry-run` 또는 `launch --backend cmux --dry-run`을 실행했을 때 현재 project metadata를 반영한 launcher path와 command가 출력되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** project-scope install이 끝나서 launcher seed가 생성된 상태에서, **When** 사용자가 `launch --backend tmux`를 실행하면, **Then** 시스템은 project-local `launch-tmux.sh`를 entrypoint로 사용해야 한다.
2. **Given** 같은 상태에서, **When** 사용자가 `launch --backend cmux`를 실행하면, **Then** 시스템은 project-local `launch-cmux.sh`를 entrypoint로 사용해야 한다.
3. **Given** 사용자가 `--dry-run`을 붙였을 때, **When** 출력을 확인하면, **Then** 실제 실행 대신 backend, launcher path, 최종 command가 보여야 한다.

---

### User Story 2 - Keep launch behavior explicit and safe (Priority: P1)

개발자는 launch CLI가 backend별 옵션 차이를 명확히 드러내고, scaffold가 없을 때도 다음 행동을 바로 이해할 수 있길 원한다.

**Why this priority**: launch CLI가 생기면 오히려 "왜 안 뜨지?"라는 혼란이 늘 수 있다. 진입점이 쉬워질수록 오류 메시지와 옵션 제약이 더 명확해야 한다.

**Independent Test**: scaffold 없이 launch를 실행하거나 `cmux`에 `--no-attach`를 주는 경우 명확한 오류를 반환하면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** `.codex/subagent-kit/launchers/`가 없는 project에서, **When** 사용자가 launch를 실행하면, **Then** 시스템은 project install이 먼저 필요하다는 점을 명확히 알려야 한다.
2. **Given** `tmux` backend를 쓸 때, **When** 사용자가 `--no-attach`를 지정하면, **Then** 시스템은 해당 옵션을 허용하고 launcher argument로 전달해야 한다.
3. **Given** `cmux` backend를 쓸 때, **When** 사용자가 `--no-attach`를 지정하면, **Then** 시스템은 backend와 맞지 않는 옵션이라는 명확한 오류를 반환해야 한다.

---

### User Story 3 - Preserve the optional-backend model (Priority: P2)

사용자는 first-class launch CLI가 생겨도 backend availability가 제품 전체를 막지 않길 원한다.

**Why this priority**: `tmux` / `cmux`는 optional dashboard backend라는 현재 제품 방향을 유지해야 한다.

**Independent Test**: launch CLI가 generated launcher를 그대로 호출하고, backend 부재 시 launcher의 soft-fail 동작을 유지하면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** backend binary가 없는 환경에서 launch를 실행할 때, **When** generated launcher가 시작되면, **Then** 기존 `SKIP` 동작이 그대로 유지되어야 한다.
2. **Given** 추후 launcher script가 수정될 수 있을 때, **When** CLI가 launch를 실행하면, **Then** Python runtime은 script 내용을 복제하지 않고 project-local launcher file 자체를 호출해야 한다.

## Edge Cases

- 사용자가 custom session/workspace name을 주지 않아도 backend별 기본 이름으로 실행 가능해야 한다.
- `--dry-run`은 launcher file 존재 여부를 검증하되, backend binary 존재 여부까지 선검사할 필요는 없다.
- launcher script가 존재하지 않으면 CLI는 shell `ENOENT` 대신 도메인 오류를 반환해야 한다.
- launch CLI는 project-local scaffold에만 의존해야 하며 global scope를 런타임 backend로 승격하지 않아야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose a `launch` CLI command for project-local backend launch.
- **FR-002**: System MUST support at least `tmux` and `cmux` as backend choices.
- **FR-003**: System MUST resolve and invoke the generated project-local launcher script under `.codex/subagent-kit/launchers/`.
- **FR-004**: System MUST support a `--dry-run` mode that prints the resolved backend, launcher path, and final command without executing it.
- **FR-005**: System MUST support a custom backend title/session name override through CLI input.
- **FR-006**: System MUST support `--no-attach` for `tmux` launches.
- **FR-007**: System MUST reject backend-incompatible options with a clear error.
- **FR-008**: System MUST return a clear project-install/scaffold error when required launcher files are missing.
- **FR-009**: System MUST delegate actual backend availability handling to the generated launcher script so existing soft-fail behavior remains intact.

### Key Entities *(include if feature involves data)*

- **Launch Request**: backend, project root, optional name override, attach mode, and dry-run 여부를 담는 CLI-level 실행 요청.
- **Launcher Target**: project-local `.codex/subagent-kit/launchers/launch-<backend>.sh` file과 실행 인자 조합.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자는 project install 이후 `codex-subagent-kit launch --backend tmux|cmux`로 backend launcher를 직접 호출할 수 있다.
- **SC-002**: 사용자는 `--dry-run`으로 launch command를 검토할 수 있다.
- **SC-003**: automated tests와 최소 `install -> launch --dry-run` smoke가 성공해야 한다.
- **SC-004**: launch CLI는 missing scaffold와 backend-incompatible option에 대해 명확한 오류를 반환한다.
