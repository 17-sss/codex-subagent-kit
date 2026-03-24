# Feature Specification: TypeScript Package CI

**Feature**: `026-typescript-package-ci`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "남은 완료 단계 중 하나로 PR CI에서 TypeScript package도 자동 검증되게 한다."

## User Scenarios & Testing

### User Story 1 - Contributors get TypeScript package feedback before merge (Priority: P1)

기여자는 PR 단계에서 Python 게이트뿐 아니라 TypeScript package의 test/typecheck/build/package 상태도 함께 확인하고 싶다.

**Independent Test**: PR CI workflow가 TypeScript job에서 `npm ci`, `npm run test:ts`, `npm run typecheck:ts`, `npm run build:ts`, `npm run pack:ts`를 실행하면 된다.

## Requirements

- **FR-001**: System MUST extend PR CI so the TypeScript package is validated on `pull_request` to `main`.
- **FR-002**: System MUST keep the existing Python test gate in the same workflow.
- **FR-003**: System MUST validate package install, test, typecheck, build, and `npm pack --dry-run` in CI.
- **FR-004**: System MUST document that the PR gate now covers both Python and TypeScript surfaces.

## Success Criteria

- **SC-001**: Contributors can catch TypeScript package regressions before merge instead of waiting for local reproduction or release preparation.
- **SC-002**: The remaining path to npm publication narrows to release automation and final manual verification.
