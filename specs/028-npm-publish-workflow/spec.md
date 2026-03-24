# Feature Specification: npm Publish Workflow

**Feature**: `028-npm-publish-workflow`  
**Created**: 2026-03-24  
**Status**: Implemented  
**Input**: User description: "이제 다음 작업으로 npm publish workflow를 추가한다."

## User Scenarios & Testing

### User Story 1 - Maintainers can publish the TypeScript package from a GitHub release (Priority: P1)

유지보수자는 `main`에서 생성된 semver GitHub Release를 기준으로 `codex-subagent-kit` npm package를 publish하고 싶다.

**Independent Test**: publish workflow가 semver release tag를 읽고, package version을 동기화한 뒤 test/typecheck/build/pack을 거쳐 npm publish를 수행하면 된다.

### User Story 2 - Package version stays aligned with the release tag at publish time (Priority: P1)

유지보수자는 repository에 저장된 workspace version과 무관하게, publish 시점의 package version이 release tag와 일치하길 원한다.

**Independent Test**: workflow가 `npm version --workspace codex-subagent-kit --no-git-tag-version <tag>`를 수행하면 된다.

## Requirements

- **FR-001**: System MUST add a GitHub Actions workflow that publishes the TypeScript package to npm from a published GitHub release.
- **FR-002**: System MUST validate that the release tag is plain semver before publishing.
- **FR-003**: System MUST sync the workspace package version to the release tag before pack/publish.
- **FR-004**: System MUST run TypeScript test, typecheck, build, and dry-run packaging before npm publish.
- **FR-005**: System MUST document the required npm secret and the release-to-publish sequence.

## Success Criteria

- **SC-001**: Maintainers can publish the npm package from the repository release flow without manual package-version edits in the workspace.
- **SC-002**: The remaining path to first npm release is reduced to repository secret setup and a final manual publish decision.
