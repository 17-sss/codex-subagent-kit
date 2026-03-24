# Feature Specification: Python Legacy Track

**Feature**: `029-python-legacy-track`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "Python 관련 자산은 복구하고, Python으로 만든 앱은 legacy implementation으로 남겨둔다."

## User Scenarios & Testing

### User Story 1 - Contributors can still access the Python app as a legacy implementation (Priority: P1)

기여자는 TypeScript/npm 전환이 진행되더라도 기존 Python 앱이 legacy implementation으로 저장소 안에 남아 있길 원한다.

**Independent Test**: Python entrypoint와 legacy install flow가 별도 이름으로 문서화되고 실행 가능하면 된다.

### User Story 2 - Contributors understand which track is current and which is legacy (Priority: P1)

기여자는 TypeScript package가 현재 release target이고, Python 앱은 legacy track이라는 점을 README와 관련 문서에서 명확히 보고 싶다.

**Independent Test**: README, testing docs, and TypeScript port docs가 TypeScript current track과 Python legacy track을 구분하면 된다.

## Requirements

- **FR-001**: System MUST preserve the Python app in the repository as a legacy implementation.
- **FR-002**: System MUST expose the legacy Python app through a distinct legacy command name.
- **FR-003**: System MUST document the legacy-Python boundary and its relationship to the TypeScript package.
- **FR-004**: System MUST update CI and testing docs to refer to the Python app as a legacy track rather than the primary release target.

## Success Criteria

- **SC-001**: Contributors can continue using the Python app without confusing it with the npm-first TypeScript package.
- **SC-002**: The repository no longer treats Python removal as an immediate migration requirement.
