# Feature Specification: Catalog Injection

**Feature**: `006-catalog-injection`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "앱 안에는 기본 TOML 템플릿이 존재해야 하고, 사용자는 awesome-codex-subagents의 `categories/` 폴더 형식 또는 직접 만든 같은 형식의 폴더를 외부에서 주입해 catalog를 확장할 수 있어야 한다."

## User Scenarios & Testing

### User Story 1 - Built-in templates remain app-owned (Priority: P1)

사용자는 앱을 설치한 직후에도 최소한의 기본 subagent 템플릿을 바로 볼 수 있어야 한다.

**Independent Test**: 별도 외부 catalog root 없이 `catalog`를 실행했을 때 app-owned built-in categories와 agent가 보이면 된다.

### User Story 2 - External category trees can extend the catalog (Priority: P1)

사용자는 `awesome-codex-subagents/categories`와 같은 구조의 외부 폴더를 catalog source로 주입해 더 많은 subagent를 설치 대상으로 사용할 수 있어야 한다.

**Independent Test**: 임시 `categories/<NN-name>/*.toml` 디렉터리를 만든 뒤 `catalog --catalog-root <path>`와 `install --catalog-root <path>`가 그 agent를 인식하면 된다.

### User Story 3 - Installed agents and external templates coexist safely (Priority: P2)

사용자는 built-in templates, external catalog templates, 이미 설치된 `.codex/agents/*.toml`이 함께 있어도 precedence와 category가 예측 가능하길 원한다.

**Independent Test**: 같은 key를 가진 built-in, injected catalog, installed agent를 섞었을 때 최종 표시와 install 동작이 일관되면 된다.

## Requirements

- **FR-001**: System MUST ship app-owned built-in template TOML files inside the package.
- **FR-002**: System MUST support external catalog roots that follow the `categories/<NN-name>/*.toml` structure.
- **FR-003**: System MUST support explicit external catalog injection through CLI input.
- **FR-004**: System MUST auto-discover project and global catalog injection directories.
- **FR-005**: System MUST keep installed `.codex/agents/*.toml` support while separating catalog templates from installed agent definitions.
- **FR-006**: System MUST NOT vendor the full `awesome-codex-subagents` repository as built-in product content.
- **FR-007**: System MUST keep Codex-compatible TOML parsing compatible with `developer_instructions`, flat `instructions`, and legacy `[instructions].text`.
- **FR-008**: System MUST create a project-local catalog injection path during project scaffold generation so users can add custom category trees after install.

## Success Criteria

- **SC-001**: Built-in catalog still works with no external input.
- **SC-002**: `catalog --catalog-root <path>` lists agents from an awesome-style `categories` tree.
- **SC-003**: `install --catalog-root <path> --agents ...` can install an injected agent into `.codex/agents`.
- **SC-004**: Project scaffold exposes a category injection directory for future user-added templates.
