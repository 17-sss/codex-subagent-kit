# Feature Specification: Launcher Flow

**Feature**: `003-launcher-flow`  
**Created**: 2026-03-20  
**Status**: Draft  
**Input**: User description: "queue / dispatch / runtime lifecycle 위에 terminal control-panel 경로를 실제로 연결한다. `tmux` / `cmux`는 shared state를 보는 dashboard 역할이어야 하고, 메인 Codex가 orchestrator인 구조는 유지한다."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Render role-specific terminal boards (Priority: P1)

operator나 개발자는 전체 panel뿐 아니라 특정 orchestrator 또는 worker role의 현재 상태를 개별 터미널 보드로 볼 수 있어야 한다.

**Why this priority**: launcher가 여러 pane/window를 띄우려면, 각 pane이 무엇을 보여줄지 먼저 정해져 있어야 한다. role board가 없으면 launcher는 같은 panel만 여러 번 띄우는 수준에 머문다.

**Independent Test**: project scaffold에 queue/dispatch/runtime 상태를 만든 뒤 특정 role board를 렌더링했을 때 역할 상태, 관련 queue 항목, 관련 dispatch 항목이 보이면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** project-local team scaffold와 runtime state가 있을 때, **When** 사용자가 특정 role board를 렌더링하면, **Then** 시스템은 그 role의 상태와 관련된 queue/dispatch 요약을 보여준다.
2. **Given** orchestrator role을 대상으로 board를 렌더링할 때, **When** 출력을 확인하면, **Then** root orchestrator가 팀 상단 역할이라는 점이 드러나야 한다.

---

### User Story 2 - Generate launcher scripts from project metadata (Priority: P1)

project를 설치한 개발자는 `.codex/subagent-kit/launchers/`에 팀 구성을 반영한 launcher script를 받아서, optional terminal dashboard를 띄울 준비가 되어 있길 원한다.

**Why this priority**: control-plane이 파일 기반 상태만 가지고 끝나지 않으려면, 그 상태를 읽는 terminal entrypoint가 실제로 생성돼야 한다.

**Independent Test**: project install 또는 scaffold refresh 후 launchers 디렉터리에 board/monitor/tmux/cmux script가 생성되고, script 내용이 현재 team topology를 반영하면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** project-scope install이 성공했을 때, **When** launchers 디렉터리를 보면, **Then** board/monitor/tmux/cmux script seed가 존재해야 한다.
2. **Given** worker 구성이 있는 팀에서 launcher script를 열어 볼 때, **When** script 내용을 확인하면, **Then** orchestrator와 workers를 반영한 board 실행 경로가 보여야 한다.
3. **Given** install을 다시 실행했을 때 일부 launcher script가 비어 있거나 누락되어 있으면, **When** scaffold backfill이 동작하면, **Then** 필요한 launcher seed가 다시 생성되어야 한다.

---

### User Story 3 - Optional backends fail softly (Priority: P2)

사용자 머신에 `tmux` 또는 `cmux`가 없어도 control-plane의 핵심 기능은 계속 쓸 수 있어야 하고, launcher는 optional 단계로 동작해야 한다.

**Why this priority**: legacy 문서에서도 backend launcher는 optional이다. 핵심 state flow와 별개로 dashboard backend는 있으면 쓰고 없으면 건너뛰는 편이 제품 방향과 맞다.

**Independent Test**: launcher script 또는 plan이 backend 부재 시 명확한 `SKIP` 또는 안내를 출력하도록 생성되면 이 스토리는 독립적으로 검증된다.

**Acceptance Scenarios**:

1. **Given** 사용자가 `tmux`가 없는 환경에서 tmux launcher를 실행할 때, **When** 스크립트가 시작되면, **Then** 시스템은 hard failure 대신 optional backend 부재를 명확히 안내해야 한다.
2. **Given** 사용자가 `cmux`가 없는 환경에서 cmux launcher를 실행할 때, **When** 스크립트가 시작되면, **Then** 동일하게 soft-fail 해야 한다.

## Edge Cases

- team에 worker가 하나도 없어도 orchestrator + monitor 기준 launcher는 생성 가능해야 한다.
- launcher script가 이미 존재하고 사용자가 수정한 경우 재실행 시 무조건 덮어쓰지 않아야 한다.
- role board는 존재하지 않는 role에 대해 명확한 오류를 반환해야 한다.
- generated launcher script는 특정 회사명이나 특정 workspace 예시에 묶이지 않아야 한다.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST render a role-specific read-only terminal board for the root orchestrator or any worker in the current team manifest.
- **FR-002**: System MUST keep the existing `panel` command as the team-wide monitor view while adding role-specific board rendering.
- **FR-003**: System MUST generate project-local launcher script seeds under `.codex/subagent-kit/launchers/` for board and monitor rendering.
- **FR-004**: System MUST generate optional backend launcher scripts for `tmux` and `cmux` using current team metadata.
- **FR-005**: System MUST keep generated launcher scripts vendor-neutral and rooted in the current project metadata rather than legacy shell manifests.
- **FR-006**: System MUST preserve existing launcher scripts on rerun unless they are missing and need backfill.
- **FR-007**: System MUST expose any new board rendering through CLI commands usable without the TUI.
- **FR-008**: System MUST treat `tmux` and `cmux` as optional backends and fail softly when they are unavailable.

### Key Entities *(include if feature involves data)*

- **Role Board**: orchestrator 또는 특정 worker role의 상태, queue, dispatch를 보여주는 read-only terminal view.
- **Monitor View**: 팀 전체 topology와 summary를 보여주는 기존 `panel` 기반 뷰.
- **Launcher Script Seed**: `.codex/subagent-kit/launchers/` 아래 생성되는 backend 실행 스크립트.
- **Backend Launcher**: `tmux` 또는 `cmux`에서 board/monitor view를 띄우는 optional dashboard entrypoint.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 사용자는 CLI로 특정 role board를 렌더링할 수 있다.
- **SC-002**: project install 후 launchers 디렉터리에서 board/monitor/backend script seed를 확인할 수 있다.
- **SC-003**: 검증 시 최소한 automated tests와 `install -> board -> panel` smoke가 성공해야 한다.
- **SC-004**: generated launcher script는 optional backend 부재를 soft-fail 하도록 안내한다.
