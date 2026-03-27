# Feature Specification: TypeScript-Only Product Boundary

**Feature**: `033-typescript-only-product`  
**Created**: 2026-03-27  
**Status**: Completed  
**Input**: User description: "파이썬 레거시 그냥 지우는게 낫지않을까? 지우면서 관련 내용도 없애고말야. 우린 npm/TS 고정할거라 이제"

## User Scenarios & Testing

### User Story 1 - Repo no longer presents Python as a supported product surface (Priority: P1)

사용자는 `codex-subagent-kit`를 npm/TypeScript 제품으로 이해해야 하고, README와 릴리즈 문서에서 Python fallback이나 legacy 설치 흐름을 보지 않아야 한다.

**Independent Test**: README, package README, TESTING, RELEASING 문서에 Python 설치/실행 경로가 남아 있지 않으면 된다.

### User Story 2 - Stable validation runs through one TS-only gate (Priority: P1)

사용자는 저장소의 기본 검증 명령이 TypeScript 기준으로 일관되게 동작하길 원한다.

**Independent Test**: `./scripts/test.sh`가 TS test, typecheck, build, pack, consumer smoke를 모두 통과하면 된다.

### User Story 3 - Installing agents no longer seeds dead experimental runtime assets (Priority: P1)

사용자는 TS 제품이 실제로 지원하지 않는 scaffold/launcher 파일을 설치 결과로 받지 않아야 한다.

**Independent Test**: `install --scope project --agents reviewer,code-mapper --validate`가 `.codex/agents/*.toml`만 생성하고 validation까지 통과하면 된다.

## Requirements

- **FR-001**: System MUST treat the TypeScript package as the only supported product surface.
- **FR-002**: System MUST remove repository-level Python source, tests, and install flows from the active product path.
- **FR-003**: System MUST keep the stable install flow focused on agent TOML generation, catalog management, validation, and usage guidance.
- **FR-004**: System MUST stop generating experimental runtime scaffold assets during stable installs.
- **FR-005**: System MUST keep release, CI, and smoke validation aligned to the TypeScript package only.

## Success Criteria

- **SC-001**: A new user can read README and understand the product as an npm/TypeScript CLI without seeing Python fallback guidance.
- **SC-002**: The repository passes its default validation gate using only TypeScript tooling.
- **SC-003**: Stable install output contains only supported TS product artifacts and no dead experimental scaffold.
