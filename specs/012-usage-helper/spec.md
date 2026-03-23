# Feature Specification: Usage Helper

**Feature**: `012-usage-helper`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "설치 후 Codex에서 어떻게 agent를 부를지 바로 보여주는 usage 또는 prompt helper를 추가한다."

## User Scenarios & Testing

### User Story 1 - Show starter prompts for installed agents (Priority: P1)

사용자는 설치된 agent를 기준으로 Codex에 바로 붙여 넣을 수 있는 starter prompt를 보고 싶다.

**Independent Test**: `usage --scope project --project-root <path>` 실행 시 visible installed agents와 starter prompt가 출력되면 된다.

### User Story 2 - Inject the current task into the prompt (Priority: P2)

사용자는 실제 작업 문장을 넣어 바로 쓸 수 있는 prompt를 받고 싶다.

**Independent Test**: `usage --task "Review the failing auth flow"` 실행 시 출력 prompt에 해당 task가 포함되면 된다.

## Requirements

- **FR-001**: System MUST provide a stable `usage` CLI command.
- **FR-002**: System MUST read visible installed agents for the selected scope rather than only the built-in catalog.
- **FR-003**: System MUST generate at least one starter prompt appropriate for the visible agents.
- **FR-004**: System MUST support an optional task string that is substituted into the rendered prompt.
- **FR-005**: System MUST fail clearly when no installed agents are available for the selected scope.

## Success Criteria

- **SC-001**: A user can copy a starter prompt into Codex immediately after install.
- **SC-002**: The output reflects the actual installed agents visible in the selected scope.
