# Feature Specification: Catalog Import

**Feature**: `010-catalog-import`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "외부 `categories/` 트리에서 필요한 category나 agent를 project/global injection 경로로 가져오는 stable import 흐름을 만든다."

## User Scenarios & Testing

### User Story 1 - Import selected agents from an external catalog root (Priority: P1)

사용자는 외부 awesome-style `categories/` 트리에서 agent 몇 개만 골라 project-local catalog injection 경로로 가져오고 싶다.

**Independent Test**: `catalog import --catalog-root <path> --agents foo,bar --scope project ...` 실행 시 선택한 agent TOML과 해당 category README가 project-local target에 복사되면 된다.

### User Story 2 - Import a full category into a persistent injection path (Priority: P1)

사용자는 특정 category 전체를 global 또는 project catalog로 가져와 계속 재사용하고 싶다.

**Independent Test**: `catalog import --catalog-root <path> --categories custom-ops ...` 실행 시 해당 category의 README와 TOML들이 target root에 복사되면 된다.

### User Story 3 - Existing imported files remain safe by default (Priority: P2)

사용자는 이미 가져온 파일을 실수로 덮어쓰고 싶지 않다.

**Independent Test**: 동일한 import를 다시 실행했을 때 `--overwrite`가 없으면 기존 파일은 preserved로 보고되고 내용이 유지되면 된다.

## Requirements

- **FR-001**: System MUST provide a stable `catalog import` command.
- **FR-002**: System MUST support importing selected agents and selected categories from one or more explicit `--catalog-root` sources.
- **FR-003**: System MUST copy the category README alongside imported agents when available.
- **FR-004**: System MUST import into the existing project/global injection path rather than requiring manual file copying.
- **FR-005**: System MUST preserve existing files by default and only overwrite them when explicitly requested.
- **FR-006**: System MUST fail clearly when the source root is missing, malformed, or missing the requested agent/category.

## Success Criteria

- **SC-001**: A user can persist selected external agent templates into a project with one command.
- **SC-002**: A user can promote a whole external category into a reusable project/global injection path.
- **SC-003**: Re-running imports does not accidentally clobber existing catalog files.
