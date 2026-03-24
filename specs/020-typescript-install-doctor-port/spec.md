# Feature Specification: TypeScript Install And Doctor Port

**Feature**: `020-typescript-install-doctor-port`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 마이그레이션 다음 단계로 install과 doctor를 포팅해 stable install 흐름을 한 사이클로 연결한다."

## User Scenarios & Testing

### User Story 1 - Contributors can install agent TOML files from the TypeScript CLI (Priority: P1)

기여자는 Python runtime을 통하지 않고도 TS CLI로 `.codex/agents/*.toml` 설치를 수행하고 싶다.

**Independent Test**: TS CLI의 `install` 명령이 project/global 대상에 agent TOML을 생성하면 된다.

### User Story 2 - Contributors can validate the installed TS output immediately (Priority: P1)

기여자는 install 직후 TS 쪽에서도 validation 결과를 확인하고 싶다.

**Independent Test**: TS CLI의 `doctor`가 fresh install을 `ok`로 보고하고, malformed file을 issue로 잡으면 된다.

## Requirements

- **FR-001**: System MUST port agent installation to the TypeScript workspace.
- **FR-002**: System MUST preserve the current project-scope orchestrator requirement in the TypeScript install flow.
- **FR-003**: System MUST generate the project-local scaffold needed by the current install contract.
- **FR-004**: System MUST port doctor reporting and wire `install --validate` to it.
- **FR-005**: System MUST add TypeScript tests for install success, orchestrator requirement, external catalog-root installs, and doctor reporting.

## Success Criteria

- **SC-001**: The TypeScript CLI can install stable agent definitions into `.codex/agents/` without invoking Python.
- **SC-002**: The TypeScript CLI can validate those installed definitions and surface errors with the same high-level behavior as the Python stable core.
