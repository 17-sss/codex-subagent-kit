# Feature Specification: npm Publish Workflow

**Feature**: `028-npm-publish-workflow`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "이제 다음 작업으로 npm publish workflow를 추가한다."

## User Scenarios & Testing

### User Story 1 - Maintainers can publish the TypeScript package from the main release workflow (Priority: P1)

유지보수자는 `main` 릴리즈 workflow가 끝날 때 `codex-subagent-kit` npm package도 함께 publish되길 원한다.

**Independent Test**: release workflow가 계산된 semver 버전을 package version에 반영하고 test/typecheck/build/pack 뒤 npm publish를 수행하면 된다.

### User Story 2 - Maintainers can recover npm publish manually when needed (Priority: P1)

유지보수자는 GitHub Release 생성 이후 npm publish만 따로 재시도해야 할 때 수동 복구 workflow를 실행하고 싶다.

**Independent Test**: 수동 workflow에 semver `release_tag`를 넣고 실행하면 같은 검증 후 npm publish를 수행하면 된다.

## Requirements

- **FR-001**: System MUST publish the TypeScript package to npm from the main release workflow after tag and GitHub Release creation.
- **FR-002**: System MUST sync the workspace package version to the computed release version before pack/publish.
- **FR-003**: System MUST run TypeScript test, typecheck, build, and dry-run packaging before npm publish.
- **FR-004**: System MUST keep a manual recovery workflow that can publish a specific semver tag on demand.
- **FR-005**: System MUST document the trusted publishing configuration and the release-to-publish sequence.

## Success Criteria

- **SC-001**: A successful `main` release run results in the matching npm package version without requiring a second workflow trigger from the GitHub Release event.
- **SC-002**: Maintainers still have a manual recovery path if npm publish must be retried for an existing semver release.
