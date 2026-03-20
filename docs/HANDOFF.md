# HANDOFF

## Metadata

- Project: codex-orchestrator
- Project ID: codex-orchestrator
- Repo Root: /Users/hoyoungson/Code/Project/Personal/codex-orchestrator
- Branch: 001-orchestrator-scaffold
- Last Updated: 2026-03-20T14:02:00+09:00
- Updated By: hoyoungson

## TL;DR

- `codex-orchestrator`는 standalone 프로젝트로 분리됐고, 현재는 project/global 설치, built-in catalog, canonical TOML agent 생성, project-scope orchestrator scaffold seed까지 동작한다.
- built-in agent 출력은 VoltAgent-style Codex-compatible TOML의 `[instructions].text` 구조로 정렬됐다.
- project-scope install은 이제 `.codex/agents/*.toml`과 함께 `.codex/orchestrator/team.toml` seed 및 control-plane scaffold 디렉터리를 만든다.
- `catalog`와 선택 로직은 이제 project/global `.toml` source를 함께 발견하고 precedence를 적용한다.
- 다음 큰 단계는 실제 terminal control panel 렌더링이다.

## Current Objective

- generated team metadata를 terminal control panel 및 `tmux` / `cmux` 흐름에 연결하고, 루트 orchestrator topology를 실제 런타임 시각화로 이어 준다.

## Current State

Done
- `src/codex_orchestrator/` 아래에 built-in subagent catalog, installer, curses TUI를 구현했다.
- `Project` / `Global` scope 선택 후 `.codex/agents/*.toml`을 생성할 수 있다.
- built-in agent TOML 출력은 VoltAgent-style Codex-compatible 구조로 정렬됐다.
- project-scope install 시 root orchestrator가 있는 `.codex/orchestrator` scaffold와 `team.toml` seed를 생성한다.
- project install은 rerun 시 기존 agent/scaffold seed를 preserve하고 결과를 출력한다.
- project/global `.toml` agent source discovery와 precedence(`project > global > built-in`)가 동작한다.
- `__codex_agents`에서 generic shell control-plane docs/scripts를 `reference/legacy_shell_control_plane/`로 이관했다.
- `specs/001-orchestrator-scaffold/` 아래 spec/plan/tasks/quickstart를 정리했다.
- `.specify/memory/constitution.md`, `docs/TESTING.ko.md`, `scripts/test.sh`, `tests/`로 SDD + testing 기반을 마련했다.
In progress
- generated team metadata를 actual control panel에 연결하는 방식 정리
To confirm
- `tmux` / `cmux` launcher를 shell asset 재사용으로 갈지 Python 생성기로 갈지

## Recent Changes

Changes
- Spec Kit 기반 첫 feature/spec/plan/tasks 정리
- `unittest` 기반 테스트 workflow 및 검증 문서 추가
- canonical agent TOML 정렬
- project install scaffold 및 root orchestrator seed 구현
- external `.toml` source discovery 및 precedence 구현
Validation run
- `python3 -m compileall src`
- `./scripts/test.sh`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- temp project에서 external `.toml`이 `catalog --scope project`에 반영되는지 테스트/검증
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --project-root .tmp-smoke --agents cto-coordinator,reviewer,code-mapper`
- fresh path에서 `.codex/orchestrator/team.toml` seed 생성 확인
- PTY 환경에서 `PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root .tmp-tui`를 키 입력으로 통과시켜 install flow 확인
Impact
- installer가 더 이상 단순 agent 파일 생성기에 머물지 않고 root orchestrator topology를 가진 scaffold seed까지 생성한다.
- 이후 기능 작업은 SDD 문서와 기본 테스트 게이트를 따라 진행할 수 있다.
- built-in agent와 외부 `.toml` agent가 같은 catalog 생태계에서 공존할 수 있게 됐다.

## Known Issues / Watch List

Issue
- 현재 TUI는 curses 기반이라 터미널/PTY 호환성이 완전히 동일하진 않다.
Risk
- shell reference asset은 아직 `__codex_agents` 시대의 `.env` manifest와 경로 가정이 남아 있다.
- 현재 reference 폴더는 “실행 엔트리포인트”가 아니라 “구현 seed”다.
- TUI end-to-end는 아직 완전 자동화되지 않았고 PTY 수동 smoke에 의존한다.
- built-in source는 여전히 Python 데이터 구조에 남아 있고 packaged TOML library로는 아직 옮기지 않았다.
Workaround
- 실제 제품 로직은 `src/codex_orchestrator/`를 source of truth로 본다.
- control panel 구현 시 reference shell asset을 그대로 재사용하지 말고, generated scaffold와 team metadata를 기준으로 재구성하는 방향을 우선 검토한다.

## Quick Reference

Key files
- `src/codex_orchestrator/cli.py`
- `src/codex_orchestrator/tui.py`
- `src/codex_orchestrator/catalog.py`
- `src/codex_orchestrator/generator.py`
- `tests/test_cli.py`
- `tests/test_generator.py`
- `docs/PRD.ko.md`
- `docs/TESTING.ko.md`
- `docs/UNDERSTANDING_AND_WORKFLOW.ko.md`
- `reference/legacy_shell_control_plane/README.md`
Commands
- `cd codex-orchestrator`
- `./scripts/test.sh`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog --project-root . --scope project`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli tui`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer`
Links / dashboards
- 아직 없음. control panel 렌더링은 다음 단계 구현 대상이다.

## Validation

Checks run
- `compileall`
- `unittest` suite via `./scripts/test.sh`
- catalog 출력
- external `.toml` discovery
- project-scope install
- orchestrator scaffold seed 생성
- curses TUI smoke flow
Results
- 모두 통과
- `.toml` output 포맷은 VoltAgent 스타일을 참고한 `[instructions].text` 구조로 정상 생성됨
- project install은 root orchestrator가 있는 `team.toml` seed를 함께 생성함
Not run yet
- terminal control panel 생성 흐름

## Next Actions

1. generated `team.toml`을 실제 terminal control panel 및 `tmux` / `cmux` launcher 흐름과 연결한다.
2. 필요하면 built-in catalog도 portable file-based source로 정리한다.

## Resume Checklist

- `README.md`, `docs/PRD.ko.md`, `docs/UNDERSTANDING_AND_WORKFLOW.ko.md`, `docs/HANDOFF.md`를 먼저 읽는다.
- `./scripts/test.sh`와 `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer`로 현재 상태를 확인한다.
- `reference/legacy_shell_control_plane/`를 보고 어떤 자산을 control panel 생성기로 끌어올지 결정한다.

## Resume Prompt

Continue this project from `docs/HANDOFF.md`. First verify the repo still matches the notes, then implement the next unfinished action: connect the generated `team.toml` topology to an actual terminal control panel and `tmux` / `cmux` launcher flow, using the migrated legacy control-plane assets only as reference, not as the primary runtime.
