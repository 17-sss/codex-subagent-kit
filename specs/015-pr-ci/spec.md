# Feature Specification: PR CI Workflow

**Feature**: `015-pr-ci`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "main 대상 PR에서 기본 테스트 게이트가 자동으로 돌도록 GitHub Actions CI를 추가한다."

## User Scenarios & Testing

### User Story 1 - Pull requests to main get a visible test signal (Priority: P1)

사용자는 `main`에 머지하기 전에 기본 테스트 게이트 결과를 PR에서 바로 보고 싶다.

**Independent Test**: `main` 대상 `pull_request`에서 workflow가 실행되고 `./scripts/test.sh`를 통과하면 된다.

### User Story 2 - The GitHub gate matches the local gate (Priority: P1)

사용자는 로컬 검증과 GitHub Actions 검증이 서로 다른 ad-hoc 명령으로 드리프트되지 않길 원한다.

**Independent Test**: workflow가 저장소 기본 게이트인 `./scripts/test.sh`를 직접 실행하면 된다.

## Requirements

- **FR-001**: System MUST provide a GitHub Actions workflow that runs on `pull_request` targeting `main`.
- **FR-002**: System MUST support manual execution through `workflow_dispatch`.
- **FR-003**: System MUST execute the repository default test gate script rather than duplicating commands inline.
- **FR-004**: System MUST prevent overlapping duplicate CI runs for the same PR or ref.

## Success Criteria

- **SC-001**: A PR targeting `main` receives an automatic pass/fail signal for the repository test gate.
- **SC-002**: The documented local gate and the GitHub Actions gate stay aligned.
