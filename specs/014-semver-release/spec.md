# Feature Specification: SemVer Release Automation

**Feature**: `014-semver-release`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "main 브랜치에만 push 될 때 tag하는 방식의 시멘틱 버저닝 릴리즈 워크플로를 만든다."

## User Scenarios & Testing

### User Story 1 - Main pushes create a semantic release tag automatically (Priority: P1)

사용자는 `main` 브랜치에 push 했을 때 시멘틱 버전 태그와 GitHub Release가 자동으로 생성되길 원한다.

**Independent Test**: workflow가 `main` push에서 semver tag를 계산하고, 없으면 새 tag와 GitHub Release를 만든다.

### User Story 2 - Version bump rules are predictable and testable (Priority: P1)

사용자는 어떤 커밋이 major/minor/patch를 올리는지 명확하게 알고 싶다.

**Independent Test**: pure versioning helper tests가 breaking change, `feat`, 그 외 변경에 대해 각각 major, minor, patch를 반환하면 된다.

## Requirements

- **FR-001**: System MUST provide a GitHub Actions workflow that runs on `push` to `main` and on manual dispatch.
- **FR-002**: System MUST compute semantic versions from existing semver tags and commit messages since the latest tag.
- **FR-003**: System MUST treat `BREAKING CHANGE` and conventional-commit `!` markers as major bumps.
- **FR-004**: System MUST treat `feat` commits as minor bumps when no major bump is present.
- **FR-005**: System MUST treat all other release-triggering pushes as patch bumps.
- **FR-006**: System MUST skip tag creation when the current commit already has a semver tag.

## Success Criteria

- **SC-001**: A push to `main` can produce a semver tag and GitHub Release without manual tag calculation.
- **SC-002**: The version bump policy is captured in tests and release documentation.
