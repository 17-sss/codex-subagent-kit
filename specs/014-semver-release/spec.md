# Feature Specification: SemVer Release Automation

**Feature**: `014-semver-release`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "main 브랜치에만 push 될 때 tag하는 방식의 시멘틱 버저닝 릴리즈 워크플로를 만든다."

## User Scenarios & Testing

### User Story 1 - Labeled PR merges create semantic releases automatically (Priority: P1)

사용자는 `main`에 머지된 PR에 release label이 붙어 있을 때만 시멘틱 버전 태그와 GitHub Release가 자동으로 생성되길 원한다.

**Independent Test**: workflow가 merge된 PR의 release label을 읽어 semver tag를 계산하고, 없으면 새 tag와 GitHub Release를 만든다.

### User Story 2 - Version bump rules are predictable and testable (Priority: P1)

사용자는 어떤 PR label이 major/minor/patch를 올리는지, 그리고 label이 없으면 릴리즈가 건너뛰어지는지 명확하게 알고 싶다.

**Independent Test**: pure release-label helper tests가 `release:major`, `release:minor`, `release:patch`, `release:none`, no-label skip을 각각 올바르게 처리하면 된다.

## Requirements

- **FR-001**: System MUST provide a GitHub Actions workflow that runs on `push` to `main` and on manual dispatch.
- **FR-002**: System MUST compute semantic versions from existing semver tags and the merged PR's release labels.
- **FR-003**: System MUST support `release:major`, `release:minor`, `release:patch`, and `release:none` labels.
- **FR-004**: System MUST skip release automation when no supported release label is present on the merged PR.
- **FR-005**: System MUST fail the release workflow when multiple supported release labels are present on the merged PR.
- **FR-006**: System MUST skip tag creation when the current commit already has a semver tag.
- **FR-007**: System MUST allow the first release to use the current package version as-is when no semver tag exists yet.
- **FR-008**: System MUST skip release automation for direct pushes to `main` that are not associated with a merged PR.

## Success Criteria

- **SC-001**: A labeled PR merge to `main` can produce a semver tag and GitHub Release without manual tag calculation.
- **SC-002**: The version bump policy is captured in tests and release documentation.
