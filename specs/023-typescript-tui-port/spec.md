# Feature Specification: TypeScript TUI Port

**Feature**: `023-typescript-tui-port`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 마이그레이션 다음 단계로 bare command와 install-first TUI를 실제로 사용할 수 있게 포팅한다."

> Historical note: the original root-orchestrator guardrail in this feature was superseded by [`032-optional-orchestrator`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/specs/032-optional-orchestrator/spec.md). The current stable TUI keeps orchestrators optional and only seeds experimental scaffolds when one is selected.

## User Scenarios & Testing

### User Story 1 - Contributors can open the install-first flow from the TypeScript CLI (Priority: P1)

기여자는 TS CLI를 직접 실행했을 때 Python 버전처럼 바로 interactive install flow가 열리길 원한다.

**Independent Test**: TS CLI 라이브러리 계층이 bare command와 `tui` command 모두에서 동일한 interactive flow를 호출하면 된다.

### User Story 2 - Project installs stay lightweight by default (Priority: P1)

기여자는 project install에서 orchestrator가 없는 specialist-only 조합도 자연스럽게 진행되길 원한다.

**Independent Test**: TS 테스트가 기본 선택이 비어 있고, project-scope validation이 최소 1개 agent만 요구하는지 검증하면 된다.

### User Story 3 - TUI completion reflects validation status (Priority: P2)

기여자는 interactive install 직후 `doctor` 결과까지 보고 성공/실패 exit code를 받길 원한다.

**Independent Test**: TS 테스트가 clean report는 `0`, issue report는 `1`, prompt exit는 `130`을 반환하는지 검증하면 된다.

## Requirements

- **FR-001**: System MUST port an install-first interactive TUI flow to TypeScript.
- **FR-002**: System MUST wire the bare command entrypoint and the explicit `tui` command to the same TypeScript implementation.
- **FR-003**: System MUST keep the interactive flow compatible with orchestrator-optional project installs.
- **FR-004**: System MUST run validation after the interactive install and return a non-zero exit code when validation reports issues.
- **FR-005**: System MUST add TypeScript tests for default selection, project/global validation behavior, success/failure exit codes, and prompt exit handling.

## Success Criteria

- **SC-001**: Contributors can run the built TypeScript CLI without a subcommand and reach an interactive install-first flow.
- **SC-002**: The remaining stable-core gap between Python and TypeScript is reduced to parity hardening and npm release work rather than missing end-user command surfaces.
