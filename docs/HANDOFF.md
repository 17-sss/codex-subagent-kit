# HANDOFF

## Metadata

- Project: codex-orchestrator
- Project ID: codex-orchestrator
- Repo Root: /Users/hoyoungson/Code/Project/Personal/codex-orchestrator
- Branch: 001-orchestrator-scaffold
- Last Updated: 2026-03-20T14:56:45+09:00
- Updated By: hoyoungson

## TL;DR

- `codex-orchestrator`는 standalone 프로젝트로 분리됐고, 현재는 project/global 설치, canonical TOML agent 생성, project-scope orchestrator scaffold seed, external `.toml` discovery까지 동작한다.
- built-in agent 출력은 VoltAgent-style Codex-compatible TOML의 `[instructions].text` 구조로 정렬됐다.
- project-scope install은 `.codex/agents/*.toml`과 함께 `.codex/orchestrator/team.toml`, runtime/queue/dispatch seed 및 control-plane scaffold 디렉터리를 만든다.
- `catalog`와 선택 로직은 project/global `.toml` source를 함께 발견하고 precedence(`project > global > built-in`)를 적용한다.
- `panel` 명령은 이제 `team.toml`, `runtime/agents.toml`, `queue/commands.toml`, `ledger/dispatches.toml`을 읽어 seeded runtime summary를 렌더링한다.

## Current Objective

- seeded terminal panel을 launcher flow와 queue/dispatch mutation 흐름으로 이어서, live control-plane 방향으로 한 단계 더 확장한다.

## Current State

Done
- `src/codex_orchestrator/` 아래에 built-in subagent catalog, installer, curses TUI를 구현했다.
- `Project` / `Global` scope 선택 후 `.codex/agents/*.toml`을 생성할 수 있다.
- built-in agent TOML 출력은 VoltAgent-style Codex-compatible 구조로 정렬됐다.
- project-scope install 시 root orchestrator가 있는 `.codex/orchestrator` scaffold와 `team.toml` seed를 생성한다.
- project-scope install 시 `runtime/agents.toml`, `queue/commands.toml`, `ledger/dispatches.toml` seed를 생성한다.
- project install은 rerun 시 기존 agent/scaffold seed를 preserve하고 결과를 출력한다.
- project/global `.toml` agent source discovery와 precedence(`project > global > built-in`)가 동작한다.
- `panel --project-root <path>`는 generated team/state seed를 읽어 topology + queue/dispatch summary를 렌더링한다.
- `__codex_agents`에서 generic shell control-plane docs/scripts를 `reference/legacy_shell_control_plane/`로 이관했다.
- `specs/001-orchestrator-scaffold/` 아래 spec/plan/tasks/quickstart를 정리했다.
- `.specify/memory/constitution.md`, `docs/TESTING.ko.md`, `scripts/test.sh`, `tests/`로 SDD + testing 기반을 마련했다.
In progress
- seeded panel을 live launcher / dispatch workflow로 확장하는 방식 정리
To confirm
- `tmux` / `cmux` launcher를 shell asset 재사용으로 갈지 Python 생성기로 갈지

## Recent Changes

Changes
- Spec Kit 기반 첫 feature/spec/plan/tasks 정리
- `unittest` 기반 테스트 workflow 및 검증 문서 추가
- canonical agent TOML 정렬
- project install scaffold 및 root orchestrator seed 구현
- external `.toml` source discovery 및 precedence 구현
- runtime / queue / dispatch seed 추가
- seeded runtime summary terminal panel renderer 추가
Validation run
- `python3 -m compileall src`
- `./scripts/test.sh`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- temp project에서 external `.toml`이 `catalog --scope project`에 반영되는지 테스트/검증
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --project-root .tmp-smoke --agents cto-coordinator,reviewer,code-mapper`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root <tmp-project>`
- fresh path에서 `.codex/orchestrator/team.toml` seed 생성 확인
- fresh path에서 `runtime/agents.toml`, `queue/commands.toml`, `ledger/dispatches.toml` seed 생성 확인
- PTY 환경에서 `PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root .tmp-tui`를 키 입력으로 통과시켜 install flow 확인
Impact
- installer가 더 이상 단순 agent 파일 생성기에 머물지 않고 root orchestrator topology를 가진 scaffold seed까지 생성한다.
- built-in agent와 외부 `.toml` agent가 같은 catalog 생태계에서 공존할 수 있게 됐다.
- generated scaffold seed를 바로 확인할 수 있는 terminal topology + state summary view가 생겼다.

## Known Issues / Watch List

Issue
- 현재 TUI는 curses 기반이라 터미널/PTY 호환성이 완전히 동일하진 않다.
Risk
- shell reference asset은 아직 `__codex_agents` 시대의 `.env` manifest와 경로 가정이 남아 있다.
- 현재 reference 폴더는 “실행 엔트리포인트”가 아니라 “구현 seed”다.
- TUI end-to-end는 아직 완전 자동화되지 않았고 PTY 수동 smoke에 의존한다.
- built-in source는 여전히 Python 데이터 구조에 남아 있고 packaged TOML library로는 아직 옮기지 않았다.
- current panel은 seed file summary까지는 보여주지만, live queue drain / dispatch mutation / pane 상태는 아직 보여주지 않는다.
Workaround
- 실제 제품 로직은 `src/codex_orchestrator/`를 source of truth로 본다.
- control panel 구현 시 reference shell asset을 그대로 재사용하지 말고, generated scaffold와 team metadata를 기준으로 재구성하는 방향을 우선 검토한다.

## Quick Reference

Key files
- `src/codex_orchestrator/cli.py`
- `src/codex_orchestrator/tui.py`
- `src/codex_orchestrator/catalog.py`
- `src/codex_orchestrator/generator.py`
- `src/codex_orchestrator/panel.py`
- `tests/test_cli.py`
- `tests/test_generator.py`
- `tests/test_panel.py`
- `docs/PRD.ko.md`
- `docs/TESTING.ko.md`
- `docs/UNDERSTANDING_AND_WORKFLOW.ko.md`
- `reference/legacy_shell_control_plane/README.md`
Commands
- `cd codex-orchestrator`
- `./scripts/test.sh`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog --project-root . --scope project`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli tui`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer`
Links / dashboards
- minimal text panel은 있음. runtime-aware control panel은 다음 단계 구현 대상이다.

## Validation

Checks run
- `compileall`
- `unittest` suite via `./scripts/test.sh`
- catalog 출력
- external `.toml` discovery
- project-scope install
- orchestrator scaffold seed 생성
- seeded runtime summary terminal panel renderer
- curses TUI smoke flow
Results
- 모두 통과
- `.toml` output 포맷은 VoltAgent 스타일을 참고한 `[instructions].text` 구조로 정상 생성됨
- project install은 root orchestrator가 있는 `team.toml` seed를 함께 생성함
- project install은 runtime / queue / dispatch seed를 함께 생성함
- `panel` 명령은 `operator -> orchestrator -> workers` topology와 seed 상태 요약을 렌더링함
Not run yet
- `tmux` / `cmux` launcher flow
- live queue / dispatch mutation flow

## Next Actions

1. seeded runtime / queue / ledger를 launcher flow와 연결한다.
2. queue / dispatch mutation CLI 또는 runtime helper 흐름을 설계한다.
3. 필요하면 built-in catalog도 portable file-based source로 정리한다.

## Resume Checklist

- `README.md`, `docs/PRD.ko.md`, `docs/UNDERSTANDING_AND_WORKFLOW.ko.md`, `docs/HANDOFF.md`를 먼저 읽는다.
- `./scripts/test.sh`, `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer`, `PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .`로 현재 상태를 확인한다.
- `reference/legacy_shell_control_plane/`를 보고 launcher / queue / dispatch mutation을 어떤 순서로 붙일지 결정한다.

## Resume Prompt

Continue this project from `docs/HANDOFF.md`. First verify the repo still matches the notes, then implement the next unfinished action: connect the seeded panel/runtime scaffold to a launcher flow and queue/dispatch mutation workflow, using the migrated legacy control-plane assets only as reference, not as the primary runtime.
