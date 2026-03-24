# Feature Specification: TypeScript Catalog Port

**Feature**: `018-typescript-catalog-port`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 포팅의 첫 실기능으로 shared path/model helper와 catalog browsing을 실제로 옮긴다."

## User Scenarios & Testing

### User Story 1 - Contributors can browse the stable catalog from the TypeScript CLI (Priority: P1)

기여자는 bootstrap만 있는 CLI가 아니라, 첫 stable command가 실제로 동작하는 포팅 기준선을 원한다.

**Independent Test**: TypeScript CLI의 `catalog` 명령이 built-in 카탈로그를 렌더링하면 된다.

### User Story 2 - External catalog roots and project/global overrides behave predictably in TypeScript (Priority: P1)

기여자는 이후 install 포팅 전에도 catalog precedence와 discovery 기준이 TS 쪽에서 유지되길 원한다.

**Independent Test**: TS 테스트가 external catalog root 로딩과 project-over-global agent precedence를 검증하면 된다.

## Requirements

- **FR-001**: System MUST port the stable catalog data model and path resolution helpers to TypeScript.
- **FR-002**: System MUST ship the app-owned built-in catalog assets inside the TypeScript package workspace.
- **FR-003**: System MUST implement the `catalog` command in the TypeScript CLI.
- **FR-004**: System MUST add TypeScript tests for built-in catalog discovery and precedence-sensitive overrides.

## Success Criteria

- **SC-001**: The TypeScript CLI can render the stable catalog without falling back to the Python runtime.
- **SC-002**: Contributors have a tested baseline for porting the rest of the stable core around the same catalog rules.
