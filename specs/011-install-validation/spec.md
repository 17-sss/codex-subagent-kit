# Feature Specification: Install Validation

**Feature**: `011-install-validation`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "install과 doctor를 더 매끄럽게 연결한다."

## User Scenarios & Testing

### User Story 1 - Validate immediately after install (Priority: P1)

사용자는 agent를 설치한 직후 같은 흐름 안에서 검증까지 끝내고 싶다.

**Independent Test**: `install ... --validate` 실행 시 설치 성공 후 `doctor` 결과가 함께 출력되고, 정상 산출물이면 exit code 0이면 된다.

### User Story 2 - Surface existing malformed files during validated install (Priority: P1)

사용자는 설치 자체는 되었더라도, target scope 안에 이미 malformed file이 있으면 바로 알고 싶다.

**Independent Test**: 깨진 기존 `.codex/agents/*.toml`이 있는 상태에서 `install ... --validate`를 실행하면 validation report를 출력하고 non-zero로 종료하면 된다.

## Requirements

- **FR-001**: System MUST support an optional `--validate` flag on the stable `install` command.
- **FR-002**: System MUST run the same `doctor` validation scope immediately after a successful install when `--validate` is enabled.
- **FR-003**: System MUST keep install output visible even when post-install validation fails.
- **FR-004**: System MUST return a non-zero exit code when validated install detects issues.

## Success Criteria

- **SC-001**: A user can finish install and validation in one command.
- **SC-002**: Existing malformed files are surfaced without requiring a separate follow-up command.
