# TESTING

영문 기본 문서: [TESTING.md](./TESTING.md)

## 목적

`codex-orchestrator`의 테스트 workflow는 세 가지를 보장한다.

- 현재 동작하는 CLI/TUI 흐름을 새 기능이 깨뜨리지 않을 것
- 생성기 변경이 재실행 가능성과 출력 계약을 유지할 것
- validation 명령이 Codex 실행 전에 malformed TOML을 잡아낼 것
- SDD 문서에서 정의한 독립 검증 방법이 구현 단계까지 이어질 것

## 기본 원칙

- 사용자 경험이나 생성 결과를 바꾸는 작업은 자동 테스트 또는 명시적인 수동 smoke 절차를 반드시 남긴다.
- 가능한 경우 `tests/` 아래 `unittest`로 자동화한다.
- `curses` TUI처럼 완전 자동화가 까다로운 변경은 자동 검증과 수동 PTY smoke를 함께 남긴다.
- 버그 수정이나 회귀 대응은 재현 테스트를 먼저 추가하거나, 자동화가 불가능하면 이유와 수동 검증 절차를 문서화한다.

## SDD 안에서의 테스트 workflow

### 1. Spec

- 각 user story에 `Independent Test`를 적는다.
- edge case와 실패 조건을 `spec.md`에 포함한다.

### 2. Plan

- `plan.md`의 `Testing` 섹션에 사용할 명령을 구체적으로 적는다.
- 어떤 검증이 자동이고 어떤 검증이 수동인지 구분한다.

### 3. Tasks

- 기능 변경이 있으면 테스트 작업을 구현 작업과 같은 story 아래에 둔다.
- 자동화 가능한 경우 테스트를 먼저 추가하고, 실패를 확인한 뒤 구현한다.

### 4. Implementation

- 순수 로직과 생성기 동작은 `tests/` 아래 `unittest`로 검증한다.
- CLI는 stdout/stderr와 생성 결과를 포함해 검증한다.
- TUI 변경은 가능한 순수 함수/로직을 자동 테스트하고, 마지막은 PTY smoke로 확인한다.

### 5. Validation

기본 게이트:

```bash
python3 -m compileall src
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

통합 smoke:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --project-root .tmp-smoke \
  --agents cto-coordinator,reviewer
PYTHONPATH=src python3 -m codex_orchestrator.cli doctor \
  --scope project \
  --project-root .tmp-smoke
```

TUI 변경 시 추가:

- PTY 환경에서 `PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root <tmp-dir>` 실행
- 실제 키 입력으로 agent 파일 생성 완료까지 확인

## 현재 자동 테스트 범위

- catalog 구조와 key 일관성
- generator의 파일 생성, 중복 방지, 오류 처리
- doctor validation의 healthy install / malformed file / missing explicit catalog root 처리
- CLI의 `catalog`, `install`, `doctor` 기본 흐름과 오류 반환

## 현재 한계

- TUI 전체 플로우는 아직 완전 자동화하지 않는다.
- 향후 `.codex/orchestrator` scaffold, queue/dispatch, launcher가 추가되면 해당 계약을 위한 테스트 레이어를 늘린다.
