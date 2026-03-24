# Feature Specification: TypeScript Template Port

**Feature**: `019-typescript-template-port`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 마이그레이션 다음 단계로 template init과 TOML rendering을 실제로 포팅한다."

## User Scenarios & Testing

### User Story 1 - Contributors can scaffold custom agent templates from the TypeScript CLI (Priority: P1)

기여자는 Python CLI에 의존하지 않고도 custom category와 agent TOML 골격을 TypeScript 쪽에서 만들고 싶다.

**Independent Test**: TypeScript CLI의 `template init`가 category README와 agent TOML을 생성하면 된다.

### User Story 2 - Generated template TOML stays compatible with the Python baseline (Priority: P1)

기여자는 install 포팅 전에 generated TOML의 기본 shape와 escaping 동작이 Python 기준선과 어긋나지 않길 원한다.

**Independent Test**: TS 테스트가 generated TOML parsing과 quoted string escaping을 검증하면 된다.

## Requirements

- **FR-001**: System MUST port agent TOML rendering utilities to the TypeScript workspace.
- **FR-002**: System MUST port template scaffolding and path selection behavior to the TypeScript workspace.
- **FR-003**: System MUST implement the `template init` command in the TypeScript CLI.
- **FR-004**: System MUST add TypeScript tests for template creation, orchestrator override, preserve-without-overwrite, and TOML escaping.

## Success Criteria

- **SC-001**: The TypeScript workspace can generate custom category and agent templates without invoking the Python runtime.
- **SC-002**: The generated template TOML remains structurally aligned with the Python stable-core contract.
