# Feature Specification: TypeScript Catalog Import Port

**Feature**: `022-typescript-catalog-import-port`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 마이그레이션 다음 단계로 external categories를 project/global catalog에 주입하는 catalog import를 포팅한다."

## User Scenarios & Testing

### User Story 1 - Contributors can persist selected external templates from the TypeScript CLI (Priority: P1)

기여자는 외부 `categories/` 트리에서 선택한 agent나 category를 TS CLI만으로 project/global catalog injection path에 가져오고 싶다.

**Independent Test**: TS CLI와 라이브러리가 선택한 agent 또는 category를 target catalog에 복사하면 된다.

### User Story 2 - Import behavior stays aligned with the current Python workflow (Priority: P1)

기여자는 기존 Python workflow처럼 overwrite 없이 preserve되고, unknown key는 에러가 나길 원한다.

**Independent Test**: TS 테스트가 preserve-without-overwrite와 unknown-agent rejection을 검증하면 된다.

## Requirements

- **FR-001**: System MUST port external catalog scanning and import planning to TypeScript.
- **FR-002**: System MUST support both project and global catalog import targets.
- **FR-003**: System MUST wire the `catalog import` CLI command to the new TypeScript implementation.
- **FR-004**: System MUST add TypeScript tests for selected-agent import, full-category import, preserve-without-overwrite, and missing-agent rejection.

## Success Criteria

- **SC-001**: The TypeScript CLI can persist external catalog entries without invoking the Python runtime.
- **SC-002**: Contributors can use the TypeScript stable core for the full catalog extension workflow before TUI parity is complete.
