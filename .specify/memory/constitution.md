# codex-orchestrator Constitution

## Core Principles

### I. Codex-Native First

이 프로젝트의 1차 산출물은 Codex가 직접 이해하고 사용할 수 있는 로컬 자산이어야 한다. 새로운 기능은 가능하면 `.codex/agents`와 `.codex/orchestrator`를 중심으로 설계하며, 외부 shell 자산은 참고 자료일 뿐 제품의 주 실행면이 되어서는 안 된다.

### II. Local-Over-Global Defaults

기본 경험은 프로젝트 로컬 설치를 우선한다. 전역 설치는 보조 기능이며, 프로젝트별 맥락이 필요한 orchestrator scaffold나 runtime state는 프로젝트 루트 기준으로 생성한다.

### III. Static Definition and Runtime State Separation

정적 agent 정의와 실행 중 상태를 섞지 않는다. `.codex/agents`에는 반복 가능하고 버전 관리 가능한 정의만 두고, `.codex/orchestrator`에는 team manifest, runtime state, queue/dispatch, bootstrap/recovery처럼 orchestration 관련 구조를 둔다.

### IV. Reference Assets Are Seeds, Not Runtime

`reference/legacy_shell_control_plane/`의 자산은 설계 seed로만 사용한다. legacy `.env` manifest, 특정 워크스페이스 경로, 세션 스냅샷 같은 과거 전제를 새 제품의 source of truth로 승격하지 않는다.

### V. Re-runnable Generation and Clear Output

생성기는 반복 실행 가능한 도구여야 한다. install이나 scaffold 생성은 재실행 시 예측 가능하게 동작해야 하며, 무엇이 생성되었고 무엇이 유지되었는지 사용자가 바로 이해할 수 있게 출력해야 한다.

### VI. Testable Changes and Explicit Validation

동작을 바꾸는 변경은 검증 가능해야 한다. 자동화 가능한 변경은 `tests/` 아래 테스트를 추가하거나 갱신하고, 자동화가 어려운 변경은 재현 가능한 수동 smoke 절차를 남긴다. 기능 완료 보고에는 실행한 검증 명령과 미실행 검증을 함께 적는다.

## Product and Engineering Constraints

- 구현 언어와 주 실행면은 Python 3.11+ 및 `src/codex_orchestrator/`다.
- 기본 사용자 흐름은 CLI와 TUI 둘 다 유지한다.
- 생성 자산에는 특정 회사명, 특정 제품명, 절대 워크스페이스 경로를 기본값으로 넣지 않는다.
- control-plane 기능은 점진적으로 추가하되, 현재 동작하는 install/catalog/TUI 흐름을 깨지 않는다.
- 기본 자동 검증 명령은 `python3 -m compileall src`와 `PYTHONPATH=src python3 -m unittest discover -s tests -v`다.
- `curses` TUI 변경은 자동 검증 외에 PTY 수동 smoke를 추가로 요구한다.

## Development Workflow and Quality Gates

- 모든 기능 작업은 `specs/###-feature-name/` 아래 `spec.md`로 시작한다.
- spec이 정리되면 `plan.md`, `tasks.md` 순으로 구체화한 뒤 구현한다.
- user story에는 `Independent Test`를 명시하고, `plan.md`에는 실제 검증 명령을 적는다.
- 사용자 경험이나 생성 결과를 바꾸는 기능은 테스트 추가 또는 명시적인 smoke 절차를 남긴다.
- legacy 자산을 참고해 구현할 때는 어떤 개념만 가져오고 어떤 legacy 제약은 버리는지 문서화한다.
- 핸드오프와 README, PRD 간 드리프트가 생기면 구현과 함께 문서를 갱신한다.

## Governance

이 헌법은 이 저장소의 SDD 기준 문서다. spec, plan, tasks, 구현, 리뷰는 이 원칙을 우선한다. 원칙 변경이 필요하면 관련 PRD/HANDOFF와 함께 수정하고, 새 규칙이 기존 흐름에 주는 영향을 명시해야 한다.

**Version**: 1.1.0 | **Ratified**: 2026-03-20 | **Last Amended**: 2026-03-20
