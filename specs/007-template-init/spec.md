# Feature Specification: Template Init

**Feature**: `007-template-init`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "template init류의 명령으로 사용자용 새 category/TOML 골격을 자동 생성한다."

## User Scenarios & Testing

### User Story 1 - Project-local template scaffolding (Priority: P1)

사용자는 project-local catalog injection 경로 아래에 새 category와 agent template 골격을 빠르게 만들고 싶다.

**Independent Test**: `template init --scope project ...` 실행 시 `.codex/subagent-kit/catalog/categories/...` 아래에 category README와 agent TOML이 생성되면 된다.

### User Story 2 - Explicit external catalog roots are scaffoldable (Priority: P1)

사용자는 awesome-style 외부 catalog root를 직접 지정해 그 안에 새 category와 agent template를 추가하고 싶다.

**Independent Test**: `template init --catalog-root <path> ...` 실행 시 지정한 `categories/` 트리 아래에 템플릿이 생성되면 된다.

### User Story 3 - Orchestrator-capable templates can be initialized cleanly (Priority: P2)

사용자는 디렉터리 category와 별개로 특정 agent template를 root orchestrator 후보로 만들고 싶다.

**Independent Test**: `template init ... --orchestrator`로 생성한 TOML이 `codex_subagent_kit_category = "meta-orchestration"`를 포함하면 된다.

## Requirements

- **FR-001**: System MUST provide a first-class CLI command for scaffolding a category README and agent TOML template.
- **FR-002**: System MUST support project-local and global catalog injection targets without requiring the user to manually create the directory tree first.
- **FR-003**: System MUST support an explicit external catalog root path as an override target.
- **FR-004**: System MUST preserve existing files by default and only overwrite them when explicitly requested.
- **FR-005**: System MUST generate Codex-compatible TOML using `developer_instructions`.
- **FR-006**: System MUST allow an initialized agent template to opt into `meta-orchestration` even when its directory category differs.

## Success Criteria

- **SC-001**: A user can create a new project-local category/agent scaffold with one command.
- **SC-002**: A user can scaffold directly into an arbitrary awesome-style `categories/` tree with one command.
- **SC-003**: A user can generate an orchestrator-capable template that the install flow later recognizes as a valid root orchestrator candidate.
