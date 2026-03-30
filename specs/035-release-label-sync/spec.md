# Feature Specification: Release Label Sync

**Feature**: `035-release-label-sync`  
**Created**: 2026-03-30  
**Status**: Implemented  
**Input**: User description: "PR label 기준 release를 쓸 거라면 label들을 자동 생성하는 GitHub Action도 필요하다."

## User Scenarios & Testing

### User Story 1 - Maintainers can keep release labels consistent from the repository (Priority: P1)

유지보수자는 release workflow가 기대하는 PR label들을 GitHub UI에서 수동으로 만들지 않고, 저장소 안의 선언 파일로 관리하고 싶다.

**Independent Test**: `.github/labels.yml`을 수정한 뒤 labels sync workflow를 실행하면 release label들이 repository에 생성되거나 갱신되면 된다.

## Requirements

- **FR-001**: System MUST define the release labels in a repository-tracked YAML file.
- **FR-002**: System MUST add a GitHub Actions workflow that syncs those labels on manual dispatch and on changes to the labels config file.
- **FR-003**: System MUST include the four supported release labels: `release:major`, `release:minor`, `release:patch`, and `release:none`.
- **FR-004**: System MUST document that these labels are the source of truth for PR-driven release bumping.

## Success Criteria

- **SC-001**: Maintainers can recreate the repository release labels from source control with one workflow run.
- **SC-002**: Release label names in docs, workflow logic, and repository settings remain consistent.
