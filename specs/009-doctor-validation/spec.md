# Feature Specification: Doctor Validation

**Feature**: `009-doctor-validation`  
**Created**: 2026-03-23  
**Status**: Implemented  
**Input**: User description: "파이썬 버전에서 다듬을 수 있는 거 다듬고, stable core를 더 단단하게 만든다."

## User Scenarios & Testing

### User Story 1 - Installed agent definitions can be validated quickly (Priority: P1)

사용자는 install 이후 현재 작업공간의 agent TOML이 정상 형식인지 한 번에 확인하고 싶다.

**Independent Test**: `doctor --scope project --project-root <path>` 실행 시 정상 install 산출물에 대해 성공 요약이 출력되면 된다.

### User Story 2 - Malformed files are surfaced with actionable paths (Priority: P1)

사용자는 잘못된 TOML 파일이 있으면 어떤 파일이 왜 잘못됐는지 바로 알고 싶다.

**Independent Test**: 깨진 `.codex/agents/*.toml`이 있을 때 `doctor`가 해당 경로와 원인을 포함한 이슈를 출력하고 non-zero로 종료하면 된다.

### User Story 3 - External catalog injection roots can be sanity-checked (Priority: P2)

사용자는 explicit `--catalog-root`가 실제로 유효한 awesome-style source인지 확인하고 싶다.

**Independent Test**: 존재하지 않는 `--catalog-root`를 넘기면 `doctor`가 해당 루트를 이슈로 보고하면 된다.

## Requirements

- **FR-001**: System MUST provide a stable `doctor` CLI command for validating installed agent definitions.
- **FR-002**: System MUST validate required Codex-compatible TOML fields and report malformed files with their paths.
- **FR-003**: System MUST check built-in, injected catalog roots, and installed agent directories relevant to the chosen scope.
- **FR-004**: System MUST return a non-zero exit code when validation issues are found.
- **FR-005**: System MUST keep the output concise enough for terminal-first use while remaining actionable.

## Success Criteria

- **SC-001**: A user can verify a fresh project install with a single `doctor` command.
- **SC-002**: A malformed agent file can be identified and fixed without opening the source code.
- **SC-003**: A broken or missing injected catalog root is surfaced before install confusion spreads further.
