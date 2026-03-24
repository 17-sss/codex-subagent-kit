# Feature Specification: TypeScript Usage Port

**Feature**: `021-typescript-usage-port`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 마이그레이션 다음 단계로 usage helper를 포팅해 설치된 agent 기준 starter prompt를 생성한다."

## User Scenarios & Testing

### User Story 1 - Contributors can generate Codex starter prompts from the TypeScript CLI (Priority: P1)

기여자는 TS CLI만으로 설치된 agent 기준 starter prompt를 바로 보고 싶다.

**Independent Test**: TS CLI의 `usage` 명령이 visible installed agents와 starter prompt를 렌더링하면 된다.

### User Story 2 - The usage helper stays aligned with the current Python wording and fallback behavior (Priority: P1)

기여자는 Python 기준선과 크게 어긋나지 않는 usage wording과 no-installed-agents failure behavior를 원한다.

**Independent Test**: TS 테스트가 orchestrator prompt, task injection, no-agents failure를 검증하면 된다.

## Requirements

- **FR-001**: System MUST port visible-installed-agent discovery for the usage helper to TypeScript.
- **FR-002**: System MUST port starter prompt rendering to TypeScript.
- **FR-003**: System MUST wire the `usage` CLI command to the new TypeScript implementation.
- **FR-004**: System MUST add TypeScript tests for starter prompt rendering, task injection, and failure without installed agents.

## Success Criteria

- **SC-001**: The TypeScript CLI can render usage guidance without invoking the Python runtime.
- **SC-002**: Contributors can use the TypeScript package to validate the end-to-end stable workflow up to prompt generation.
