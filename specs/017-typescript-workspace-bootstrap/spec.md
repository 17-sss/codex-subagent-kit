# Feature Specification: TypeScript Workspace Bootstrap

**Feature**: `017-typescript-workspace-bootstrap`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 포팅 계획 다음 단계로, 실제 npm/TS 작업이 바로 시작될 수 있는 워크스페이스와 CLI 부트스트랩을 만든다."

## User Scenarios & Testing

### User Story 1 - Contributors can start the TypeScript port without inventing the workspace shape (Priority: P1)

기여자는 별도의 초기 세팅 없이 TypeScript 패키지 위치와 기본 엔트리포인트를 바로 이해하고 싶다.

**Independent Test**: 저장소 안에 dedicated npm workspace와 `codex-subagent-kit` CLI bootstrap entrypoint가 존재하면 된다.

### User Story 2 - The first TypeScript package exposes only the intended stable command surface (Priority: P1)

기여자는 포팅 초기에 experimental 명령까지 섞이지 않도록 stable surface만 드러난 CLI 골격을 원한다.

**Independent Test**: TypeScript CLI help와 소스가 stable command bootstrap만 포함하고 experimental 범위를 명시하면 된다.

## Requirements

- **FR-001**: System MUST add a dedicated npm workspace for the TypeScript port.
- **FR-002**: System MUST provide a bootstrapped `codex-subagent-kit` CLI entrypoint in that workspace.
- **FR-003**: System MUST limit the bootstrapped CLI surface to the stable commands selected in the TypeScript port plan.
- **FR-004**: System MUST document that the Python CLI remains the production source of truth until parity work is complete.

## Success Criteria

- **SC-001**: A contributor can run npm install and build the TypeScript workspace without inventing missing packaging files.
- **SC-002**: The TypeScript workspace exposes a clear starting point for stable-core parity work while avoiding accidental product drift.
