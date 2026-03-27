# Feature Specification: npm Consumer Smoke

**Feature**: `030-npm-consumer-smoke`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "npm에 배포하기 전에 실제 소비자 관점에서 package 설치와 실행을 다시 확인한다."

## User Scenarios & Testing

### User Story 1 - Maintainers can verify the packed npm tarball in an isolated install (Priority: P1)

유지보수자는 workspace 소스가 아니라 실제 npm tarball 설치 관점에서 CLI가 실행되는지 확인하고 싶다.

**Independent Test**: packed tarball을 임시 prefix에 설치한 뒤 `codex-subagent-kit --help`, `catalog`, `install --validate`, `doctor`, `usage`가 실행되면 된다.

### User Story 2 - CI catches npm packaging regressions before release (Priority: P1)

유지보수자는 publish 직전이 아니라 PR 단계에서 tarball packaging 문제가 드러나길 원한다.

**Independent Test**: PR CI와 npm publish workflow가 동일한 consumer smoke를 실행하면 된다.

## Requirements

- **FR-001**: System MUST provide a repeatable npm consumer smoke command from the repository root.
- **FR-002**: System MUST validate the packed TypeScript package through an isolated install, not only workspace execution.
- **FR-003**: System MUST run the consumer smoke in CI before npm publishing.

## Success Criteria

- **SC-001**: Maintainers can validate the packaged CLI locally with one command.
- **SC-002**: Packaging regressions surface before or during release automation rather than after publishing.
