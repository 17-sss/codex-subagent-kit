# Feature Specification: TUI Validation

**Feature**: `013-tui-validation`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "TUI install 완료 후에도 같은 validation 흐름을 자연스럽게 붙인다."

## User Scenarios & Testing

### User Story 1 - TUI install shows validation status (Priority: P1)

사용자는 TUI로 설치한 뒤 별도 명령 없이 validation 결과까지 바로 보고 싶다.

**Independent Test**: TUI install이 성공한 뒤 result screen에 validation status가 함께 전달되면 된다.

### User Story 2 - TUI exits non-zero when validation fails (Priority: P1)

사용자는 TUI install 이후 malformed file 같은 문제가 있으면 종료 코드로도 알 수 있어야 한다.

**Independent Test**: TUI install 뒤 validation report가 issues를 포함하면 `run_tui(...)`가 non-zero를 반환하면 된다.

## Requirements

- **FR-001**: System MUST run the same `doctor` validation after a successful TUI install.
- **FR-002**: System MUST surface validation status in the TUI result screen.
- **FR-003**: System MUST return a non-zero exit code when post-install TUI validation detects issues.

## Success Criteria

- **SC-001**: TUI and CLI install flows provide a consistent validation story.
- **SC-002**: Validation issues discovered after TUI install are not hidden behind a success-only UI.
