# Feature Specification: VoltAgent Catalog Sync

**Feature**: `031-voltagent-catalog-sync`  
**Created**: 2026-03-27  
**Status**: Completed  
**Input**: User description: "내장한 임의 TOML은 제거하고 VoltAgent awesome-codex-subagents categories를 기본 catalog로 삼는다. 주기적으로 upstream을 참고하고 업데이트할 수 있는 명령을 추가하고, 사용자가 직접 TOML을 넣는 것도 가능해야 한다."

## User Scenarios & Testing

### User Story 1 - Default catalog comes from VoltAgent categories (Priority: P1)

사용자는 앱이 우리 임의 템플릿이 아니라 VoltAgent `awesome-codex-subagents/categories` snapshot을 기본 catalog로 제공하길 원한다.

**Independent Test**: fresh install 이후 별도 `--catalog-root` 없이 `catalog`를 실행했을 때 VoltAgent category/agent가 보이고, 기존 app-owned custom-only built-ins는 제거되어 있으면 된다.

### User Story 2 - Maintainers can refresh from upstream (Priority: P1)

유지보수자는 VoltAgent upstream `categories/`를 주기적으로 다시 받아와 project/global source root를 갱신하고 싶다.

**Independent Test**: `catalog sync --scope global` 또는 `catalog sync --scope project`가 VoltAgent source를 받아와 자동 발견되는 source root를 갱신하면 된다.

### User Story 3 - Users can still add their own TOML files (Priority: P1)

사용자는 upstream snapshot과 별개로 직접 만든 category/agent TOML을 계속 추가하고 싶다.

**Independent Test**: `.codex/subagent-kit/catalog/categories/` 또는 `~/.codex/subagent-kit/catalog/categories/`에 직접 만든 TOML을 넣었을 때 `catalog`, `install`, `doctor`가 그 정의를 함께 인식하면 된다.

## Requirements

- **FR-001**: System MUST replace the current app-authored built-in templates with a VoltAgent `categories/` snapshot.
- **FR-002**: System MUST preserve support for user-authored awesome-style `categories/<NN-name>/*.toml` trees.
- **FR-003**: System MUST auto-discover synced upstream source roots separately from user-authored catalog injection roots.
- **FR-004**: System MUST provide a stable `catalog sync` command that can refresh VoltAgent categories into project or global source roots.
- **FR-005**: System MUST keep generated `.codex/agents/*.toml` output Codex-compatible even when upstream source TOML shape evolves.
- **FR-006**: System MUST update documentation and examples to reference the VoltAgent-backed catalog and current root orchestrator choice.

## Success Criteria

- **SC-001**: Fresh users see a useful VoltAgent-backed default catalog without needing a manual local clone.
- **SC-002**: Maintainers can refresh upstream catalog content with one command and verify the result through `catalog` and `doctor`.
- **SC-003**: User-authored TOML files continue to coexist with upstream-backed catalog content without losing precedence clarity.
