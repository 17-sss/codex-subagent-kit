# Feature Specification: Optional Orchestrator Installs

**Feature**: `032-optional-orchestrator`  
**Created**: 2026-03-27  
**Status**: Completed  
**Input**: User description: "필히 오케스트레이터가 없어도 될 것 같고, subagent들을 편하게 TOML 파일로 세팅하는 제품 정체성에 맞게 전반적으로 정리하고 싶다."

## User Scenarios & Testing

### User Story 1 - Project installs work without an orchestrator (Priority: P1)

사용자는 orchestrator 없이도 reviewer, code-mapper 같은 specialist subagent만 골라서 project scope에 설치하고 싶다.

**Independent Test**: `install --scope project --agents reviewer,code-mapper`가 성공하고 `.codex/agents/*.toml`만 생성되면 된다.

### User Story 2 - Experimental scaffold remains available when explicitly selected (Priority: P1)

사용자는 meta-orchestration agent를 선택했을 때만 experimental companion scaffold를 함께 seed하고 싶다.

**Independent Test**: project install에 `multi-agent-coordinator`를 포함하면 `.codex/subagent-kit/` scaffold가 생성되고, 포함하지 않으면 생성되지 않으면 된다.

### User Story 3 - Usage guidance adapts to installed agents (Priority: P1)

사용자는 orchestrator가 있든 없든 현재 설치된 subagent 조합을 바탕으로 Codex starter prompt를 받고 싶다.

**Independent Test**: `usage`가 meta-orchestration agent가 있으면 coordination-style prompt를, 없으면 direct specialist prompt를 출력하면 된다.

## Requirements

- **FR-001**: System MUST allow project installs that contain no meta-orchestration agents.
- **FR-002**: System MUST only generate the experimental `.codex/subagent-kit/` scaffold automatically when the selected install set includes a meta-orchestration agent.
- **FR-003**: System MUST keep orchestrator-aware templates and categories available as optional catalog entries.
- **FR-004**: System MUST update TUI copy and default selection so users are not forced toward orchestrator-first installs.
- **FR-005**: System MUST update usage guidance and documentation so the stable product identity is "subagent kit" first and orchestrator second.

## Success Criteria

- **SC-001**: Users can complete a project install with only specialist subagents and receive a clean validation result.
- **SC-002**: Users who intentionally choose a meta-orchestration agent still get the experimental scaffold and related output.
- **SC-003**: Documentation and starter prompts no longer imply that a root orchestrator is mandatory for the stable workflow.
