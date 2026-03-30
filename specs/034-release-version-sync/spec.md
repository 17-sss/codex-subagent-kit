# Feature Specification: Release Version Sync

**Feature**: `034-release-version-sync`  
**Created**: 2026-03-30  
**Status**: Implemented  
**Input**: User description: "PR이 main에 반영되면 모든 명시된 버전의 싱크가 맞춰지면 좋겠다."

## User Scenarios & Testing

### User Story 1 - Maintainers see the released version reflected in the repository after merge (Priority: P1)

유지보수자는 `main`에 PR이 머지된 뒤 생성되는 릴리즈 버전이 `packages/codex-subagent-kit/package.json`과 `package-lock.json`에도 반영되길 원한다.

**Independent Test**: release workflow가 semver 버전을 계산한 뒤 workspace version file을 commit/push하고, 그 commit에 tag를 생성하면 된다.

### User Story 2 - Release automation avoids infinite loops (Priority: P1)

유지보수자는 release workflow가 version sync commit을 다시 감지해서 중복 릴리즈를 만들지 않길 원한다.

**Independent Test**: workflow가 `[skip release]` marker가 있는 자동 sync commit에서는 job을 건너뛰면 된다.

## Requirements

- **FR-001**: System MUST sync `packages/codex-subagent-kit/package.json` and `package-lock.json` to the computed release version before creating the git tag.
- **FR-002**: System MUST push the version sync commit back to `main` when those files changed.
- **FR-003**: System MUST create the release tag and GitHub Release from the synced commit SHA instead of the pre-sync merge commit SHA.
- **FR-004**: System MUST avoid triggering duplicate releases from the version sync commit.
- **FR-005**: System MUST document that repository-visible package versions now stay aligned automatically after release.

## Success Criteria

- **SC-001**: After a `main` release, maintainers can inspect `main` and see the released version in workspace version files without manual follow-up commits.
- **SC-002**: The release workflow does not loop on its own version sync commit.
