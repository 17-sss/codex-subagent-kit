# Feature Specification: Orchestrator Scaffold Generation

**Feature Branch**: `001-orchestrator-scaffold`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description: "install 이후 .codex/subagent-kit scaffold를 생성하고 tmux/cmux control-plane 연결의 기반을 만든다. agent TOML은 VoltAgent가 쓰는 Codex-compatible 구조를 참고해 canonical format으로 맞추고, 최상단에는 root orchestrator가 있는 control panel topology를 유지한다."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Project install creates orchestrator scaffold (Priority: P1)

프로젝트에서 subagent를 설치하는 개발자는 `.codex/agents/*.toml`만 받는 데서 끝나지 않고, 이후 control-plane 기능을 붙일 수 있는 `.codex/subagent-kit` 기본 scaffold도 즉시 받아야 한다.

**Why this priority**: 현재 제품의 다음 핵심 단계는 install 결과를 control-plane 확장 가능한 구조로 이어 주는 것이다. 이 흐름이 없으면 설치 결과가 고립되고, 이후 queue/dispatch/bootstrap 작업을 안정적으로 쌓기 어렵다.

**Independent Test**: 빈 프로젝트 디렉터리에서 project-scope install을 실행했을 때 `.codex/agents/*.toml`과 `.codex/subagent-kit` 기본 파일/디렉터리가 함께 생성되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 사용자가 비어 있는 프로젝트 루트에서 `install --scope project`를 실행했고 하나 이상의 agent를 선택했을 때, **When** 설치가 완료되면, **Then** 시스템은 `.codex/agents/*.toml`과 `.codex/subagent-kit` scaffold를 함께 생성한다.
2. **Given** 사용자가 scaffold 생성 결과를 확인할 때, **When** `.codex/subagent-kit` 내부를 열어 보면, **Then** 팀 구성, runtime state 위치, 다음 실행 단계가 드러나는 기본 파일과 디렉터리가 존재한다.
3. **Given** 사용자가 control-plane seed를 열어 볼 때, **When** team manifest를 확인하면, **Then** 하나의 root orchestrator와 그 아래 subagent들이 표현되는 기본 topology가 드러나야 한다.

---

### User Story 2 - Re-running install is safe and predictable (Priority: P2)

이미 scaffold가 있는 프로젝트에서 개발자는 install을 다시 실행해도 수동 편집한 orchestrator 자산이 예고 없이 덮어써지지 않아야 한다.

**Why this priority**: 생성기는 반복 실행되는 도구다. 재실행 안전성이 없으면 실제 프로젝트에 적용하기 어렵고, 한번 생성한 뒤 수정하는 운영 흐름과 충돌한다.

**Independent Test**: project-scope install을 두 번 실행하고, 두 번째 실행 전에 scaffold 파일 일부를 수정한 뒤 재실행했을 때 덮어쓰기 정책이 명확하게 적용되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** `.codex/subagent-kit`가 이미 존재하고 사용자가 일부 파일을 수정한 상태에서, **When** 사용자가 install을 다시 실행하면, **Then** 시스템은 기존 파일을 무조건 덮어쓰지 않고 안전한 재실행 규칙에 따라 동작한다.
2. **Given** 재실행 중 이미 존재하는 scaffold 자산을 만났을 때, **When** 생성기 판단이 끝나면, **Then** 시스템은 어떤 파일을 유지했고 어떤 파일을 새로 만들었는지 사용자가 이해할 수 있게 결과를 알려준다.

---

### User Story 3 - Generated scaffold is generic and ready for future control-plane work (Priority: P3)

제품 개발자는 생성된 scaffold가 특정 회사나 워크스페이스 예시에 묶이지 않으면서도, 앞으로 `tmux`/`cmux` launcher와 queue/dispatch 기능을 붙일 수 있는 중립적인 기본 구조이길 원한다.

**Why this priority**: PRD의 핵심 원칙이 Codex-native, local-first, vendor-neutral이기 때문이다. reference asset을 그대로 복사하면 legacy 제약이 새 제품에 스며든다.

**Independent Test**: 생성된 scaffold 파일을 검사했을 때 특정 조직명, 특정 워크스페이스 경로, legacy `.env` manifest 의존성이 없고, 후속 control-plane 구현에 필요한 자리표시 구조가 보이면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 사용자가 새로 생성된 scaffold 파일을 열어 봤을 때, **When** manifest와 관련 문서를 검토하면, **Then** 특정 회사명이나 고정 워크스페이스 예시 없이 일반적인 프로젝트 기준 내용만 포함한다.
2. **Given** 추후 `tmux` 또는 `cmux` launcher를 추가 구현하려는 개발자가 있을 때, **When** 생성된 scaffold를 기준점으로 사용하면, **Then** runtime state, team manifest, launcher 연결 지점을 추론할 수 있다.

---

### User Story 4 - Agent definitions stay externally compatible and extensible (Priority: P3)

제품 개발자는 built-in catalog만이 아니라, 나중에 직접 만든 `.toml` agent 파일이나 외부 curated repo의 `.toml`을 추가해 같은 시스템 안에서 다루고 싶다.

**Why this priority**: 이 제품이 단순 설치기보다 team builder/control-plane이 되려면, agent 정의 포맷이 특정 내부 구조에 갇히지 않고 Codex-compatible TOML 생태계와 맞물려야 한다.

**Independent Test**: built-in agent와 사용자 제공 `.toml` agent가 같은 canonical shape로 인식되고, catalog 또는 후속 team 구성 단계에서 함께 다뤄질 수 있음을 문서/구조로 확인하면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 제품이 built-in agent를 생성할 때, **When** `.toml` 파일을 쓰면, **Then** VoltAgent가 사용하는 Codex-compatible TOML 구조와 충돌하지 않는 canonical shape를 따라야 한다.
2. **Given** 사용자가 나중에 별도로 만든 `.toml` agent 파일을 프로젝트 또는 글로벌 디렉터리에 추가할 때, **When** 시스템이 agent 정의를 읽는 구조로 확장되면, **Then** built-in agent와 동일한 생태계 안에서 취급할 수 있어야 한다.

### Edge Cases

- 사용자가 `--scope global`로 설치할 때는 project-local `.codex/subagent-kit` scaffold를 만들지 않고, 그 이유를 출력해야 한다.
- 일부 scaffold 파일은 이미 존재하지만 나머지는 없는 반쯤 생성된 상태에서도 install 재실행이 실패 없이 복구 가능해야 한다.
- 사용자가 agent 설치 없이 scaffold만 기대하는 호출을 할 경우 현재 CLI 계약상 허용 범위를 명확히 안내해야 한다.
- legacy reference 자산에 있는 shell 개념을 참고하되, 생성 결과가 legacy `.env` 파일 구조를 직접 요구하면 안 된다.
- built-in catalog와 외부 `.toml` source가 섞일 때 key 충돌이나 precedence 규칙을 명확히 정의해야 한다.
- root orchestrator가 누락된 팀 구성은 control panel seed로 허용하지 않아야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extend project-scope install so that successful agent installation also prepares a `.codex/subagent-kit` scaffold in the selected project root.
- **FR-002**: System MUST keep `.codex/agents` as the location for static subagent definitions and `.codex/subagent-kit` as the location for orchestration-specific scaffold assets.
- **FR-003**: System MUST generate a team manifest seed in `.codex/subagent-kit` using the product's chosen canonical format for this feature, with one explicit root orchestrator and zero or more worker subagents.
- **FR-004**: System MUST generate the minimum directory and file structure required to support future runtime state, queue/dispatch ledger, bootstrap/recovery, and launcher integration.
- **FR-005**: System MUST treat migrated shell control-plane assets under `reference/legacy_shell_control_plane/` as reference material only and MUST NOT make them the runtime entrypoint of the product.
- **FR-006**: System MUST avoid generating company-specific names, workspace-specific absolute paths, or session-specific runtime data in the scaffold output.
- **FR-007**: System MUST define deterministic re-run behavior for existing scaffold assets so the install command is safe to execute more than once.
- **FR-008**: System MUST report scaffold generation results to the caller alongside agent installation results, including created, skipped, or preserved paths as applicable.
- **FR-009**: System MUST NOT create project-local orchestrator scaffold when install scope is `global`.
- **FR-010**: System MUST preserve the current working `catalog`, `install`, and `tui` flows while adding scaffold generation behavior.
- **FR-011**: System MUST document or embed enough next-step guidance in the generated scaffold so a developer can understand where future control-plane integration belongs.
- **FR-012**: System MUST adopt a canonical subagent TOML format that is Codex-compatible and closely aligned with the VoltAgent-style structure so built-in agents and externally added `.toml` agents can coexist.
- **FR-013**: System MUST treat agent definitions as portable artifacts that may originate from built-in catalog entries or user-supplied `.toml` files in project/global agent directories.
- **FR-014**: System MUST preserve the product identity as an orchestrated team builder/control-plane, not only a subagent file generator, by reserving an explicit orchestrator role in team topology and generated scaffold.
- **FR-015**: System MUST ensure future terminal control panel views can represent the hierarchy `operator/user -> orchestrator -> subagents` from generated team metadata.

### Key Entities *(include if feature involves data)*

- **Orchestrator Scaffold**: `.codex/subagent-kit` 아래 생성되는 기본 디렉터리와 seed 파일 집합. 정적 정의와 runtime state를 분리하는 제품 구조를 반영한다.
- **Team Manifest Seed**: 향후 오케스트레이션 팀 구성을 정의하기 위한 초기 manifest 파일. 하나의 root orchestrator와 그 하위 worker agent 구조를 표현한다.
- **Canonical Agent TOML**: built-in 생성 자산과 외부 curated/user-provided agent 파일이 함께 공존할 수 있도록 정한 Codex-compatible TOML shape.
- **Operator**: 실제 업무 지시를 내리는 사용자 또는 대표 역할. control panel 상에서 orchestrator의 상위 개념이다.
- **Orchestrator Node**: 사용자의 명령을 받아 팀 작업을 조율하는 단일 루트 에이전트.
- **Worker Subagent**: orchestrator가 역할별로 위임하는 하위 에이전트.
- **Scaffold Generation Result**: install 실행 중 agent 파일 생성 결과와 별도로, scaffold의 생성/유지/건너뜀 상태를 설명하는 결과 정보.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 개발자는 project-scope install 1회 실행만으로 `.codex/agents/*.toml`과 `.codex/subagent-kit` scaffold를 모두 받을 수 있다.
- **SC-002**: 동일한 프로젝트에서 install을 재실행해도 기존 scaffold 편집본이 예고 없이 손실되지 않는다.
- **SC-003**: 생성된 scaffold를 검사했을 때 특정 회사명, 특정 워크스페이스 경로, 세션성 runtime state가 포함되지 않는다.
- **SC-004**: 구현 검증 시 최소한 `catalog`, project-scope `install`, 그리고 scaffold 생성 결과 확인이 성공해야 한다.
- **SC-005**: canonical agent format 결정 후 built-in agent와 외부 `.toml` agent가 같은 생태계 안에 들어올 수 있는 방향이 문서와 scaffold에 반영된다.
- **SC-006**: generated team metadata를 기준으로 미래 control panel이 `operator/user -> orchestrator -> subagents` 구조를 표현할 수 있다.
