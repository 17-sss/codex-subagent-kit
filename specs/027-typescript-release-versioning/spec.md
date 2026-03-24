# Feature Specification: TypeScript Release Versioning

**Feature**: `027-typescript-release-versioning`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "TypeScript 전환 흐름에 맞춰 release/versioning 경로에서 Python 의존을 제거한다."

## User Scenarios & Testing

### User Story 1 - Maintainers can compute release versions without the Python runtime (Priority: P1)

유지보수자는 GitHub release workflow가 Python helper와 `pyproject.toml`에 의존하지 않고 TypeScript package 기준으로 버전을 계산하길 원한다.

**Independent Test**: release workflow가 `packages/codex-subagent-kit/package.json`과 TypeScript semver helper를 사용해 버전을 계산하면 된다.

### User Story 2 - Contributors can validate semver bump rules from the TypeScript package (Priority: P1)

기여자는 major/minor/patch 규칙이 TS 테스트에서 그대로 검증되길 원한다.

**Independent Test**: TS 테스트가 semver parse/bump/classify/compute 경로를 검증하면 된다.

## Requirements

- **FR-001**: System MUST port release semver helpers to the TypeScript package.
- **FR-002**: System MUST add TypeScript tests for semver parsing, bump classification, and next-version computation.
- **FR-003**: System MUST update the GitHub release workflow to use the TypeScript package version as the initial release source.
- **FR-004**: System MUST remove Python-based version computation from the GitHub release workflow.

## Success Criteria

- **SC-001**: The GitHub release path no longer depends on the Python runtime to classify semver bumps.
- **SC-002**: Moving off Python becomes a matter of product-scope decisions rather than release-infrastructure blockers.
