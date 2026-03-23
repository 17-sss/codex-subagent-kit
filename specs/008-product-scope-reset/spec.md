# Feature Specification: Product Scope Reset

**Feature**: `008-product-scope-reset`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "installer/catalog/template 중심으로 제품 범위를 재정의하고, control-plane 계열은 experimental로 내린다."

## User Scenarios & Testing

### User Story 1 - Stable core is easy to understand (Priority: P1)

사용자는 이 도구의 핵심 가치가 무엇인지 README와 CLI만 보고 빠르게 이해하고 싶다.

**Independent Test**: `README.md`와 `codex-subagent-kit --help`를 보면 stable core가 `catalog`, `install`, `template`, `tui` 중심이라는 점이 분명히 보이면 된다.

### User Story 2 - Experimental control-plane features do not redefine the product (Priority: P1)

사용자는 panel, launch, dispatch 같은 기능이 현재 실험적이라는 점을 명확히 알고 싶다.

**Independent Test**: CLI help와 제품 문서에서 control-plane 관련 명령이 `experimental`로 표시되면 된다.

### User Story 3 - Product docs align with Codex-native workflow (Priority: P2)

사용자는 이 도구가 독립 orchestrator runtime이 아니라 Codex 세션 준비 도구라는 점을 이해하고 싶다.

**Independent Test**: PRD와 workflow 문서가 `.codex/agents/*.toml` 설치와 Codex 세션 사용을 중심 흐름으로 설명하면 된다.

## Requirements

- **FR-001**: System MUST define the stable product core as catalog discovery, agent installation, template scaffolding, and install-first TUI workflow.
- **FR-002**: System MUST describe queue, dispatch, panel, board, and launcher functionality as experimental rather than as the primary product identity.
- **FR-003**: System MUST keep the user-facing documentation aligned with Codex-native subagent usage, where Codex remains the runtime owner of agent threads.
- **FR-004**: System MUST preserve access to existing experimental commands without presenting them as the default value proposition.

## Success Criteria

- **SC-001**: A new user can infer from the README within one minute that the product primarily helps install and manage Codex subagent TOML definitions.
- **SC-002**: A new user can infer from CLI help within one minute which commands are stable and which are experimental.
- **SC-003**: Product docs no longer imply that an external control-plane is the canonical runtime for Codex subagents.
