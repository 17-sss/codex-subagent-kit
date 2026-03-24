# Feature Specification: TypeScript Parity Fixtures

**Feature**: `024-typescript-parity-fixtures`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 포트가 Python stable core 계약을 공유 fixture로 검증하도록 parity 테스트를 추가한다."

## User Scenarios & Testing

### User Story 1 - Contributors can verify TypeScript output against the Python golden contract (Priority: P1)

기여자는 TS 포트를 진행하면서 생성 TOML과 stable 출력이 Python 기준선에서 드리프트하지 않는지 확인하고 싶다.

**Independent Test**: TS 테스트가 shared golden fixture와 generated TOML, `usage`, `doctor` 출력을 직접 비교하면 된다.

## Requirements

- **FR-001**: System MUST add TypeScript tests that compare generated reviewer TOML against the shared golden fixture.
- **FR-002**: System MUST add TypeScript tests that compare project-scope `usage` output against the shared golden fixture.
- **FR-003**: System MUST add TypeScript tests that compare project-scope `doctor` output against the shared golden fixture after path normalization.
- **FR-004**: System MUST keep the shared fixture directory under `tests/fixtures/golden` as the single cross-language contract source.

## Success Criteria

- **SC-001**: Contributors can detect TypeScript/Python drift from a single shared fixture suite.
- **SC-002**: The TypeScript port moves from command-surface completeness toward contract-level parity.
