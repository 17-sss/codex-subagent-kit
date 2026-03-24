# Feature Specification: TypeScript Port Plan

**Feature**: `016-typescript-port-plan`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "npm 배포를 목표로 TypeScript 버전 작업을 시작하되, 구현 전에 포팅 범위와 기준선을 먼저 정의한다."

## User Scenarios & Testing

### User Story 1 - The port target is explicit before implementation begins (Priority: P1)

사용자는 TypeScript 작업을 시작하기 전에 어떤 명령이 첫 포팅 대상인지 분명히 알고 싶다.

**Independent Test**: 포팅 계획 문서가 stable 범위와 first-pass 제외 범위를 명시하면 된다.

### User Story 2 - The TypeScript port has a parity contract (Priority: P1)

사용자는 TypeScript 구현이 Python 기준선에서 드리프트되지 않도록 비교 기준을 알고 싶다.

**Independent Test**: 문서가 golden fixture, CLI 계약, 우선 parity 대상을 명시하면 된다.

## Requirements

- **FR-001**: System MUST document the stable command scope for the first TypeScript/npm port.
- **FR-002**: System MUST document the experimental commands that are out of scope for the first TypeScript pass.
- **FR-003**: System MUST document the recommended Node/TypeScript stack for the npm-targeted CLI.
- **FR-004**: System MUST define Python-based parity references to guide the future port.

## Success Criteria

- **SC-001**: A contributor can start the TypeScript implementation with a clear stable-core scope.
- **SC-002**: The repository documents Python as the current source of truth until stable-core parity is reached.
