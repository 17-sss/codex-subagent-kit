# HANDOFF

## Metadata

- Project: codex-orchestrator
- Project ID: codex-orchestrator
- Repo Root: /Users/hoyoungson/Code/Project/Personal/codex-orchestrator
- Branch: unknown
- Last Updated: 2026-03-20T11:19:00+09:00
- Updated By: hoyoungson

## TL;DR

- `codex-orchestrator`는 새 standalone 프로젝트로 분리됐고, 현재는 `.codex/agents/*.toml` 생성용 TUI/CLI MVP가 동작한다.
- 기존 `__codex_agents`에서 재사용 가능한 자산은 `reference/legacy_shell_control_plane/`로 이관했고, 특정 workspace에 묶인 예시는 제거했다.
- 다음 큰 단계는 installer가 끝난 뒤 `.codex/orchestrator` scaffold와 `tmux`/`cmux` control panel 생성 흐름을 붙이는 것이다.

## Current Objective

- install 결과를 바탕으로 `.codex/orchestrator` scaffold를 생성하고, 이후 `tmux` / `cmux` control panel과 queue/dispatch control-plane을 Python-native 방향으로 연결한다.

## Current State

Done
- `src/codex_orchestrator/` 아래에 built-in subagent catalog, installer, curses TUI를 구현했다.
- `Project` / `Global` scope 선택 후 `.codex/agents/*.toml`을 생성할 수 있다.
- `__codex_agents`에서 generic shell control-plane docs/scripts를 `reference/legacy_shell_control_plane/`로 이관했다.
- catalog와 문서에서 특정 workspace에 묶인 고정 예시를 제거했다.
- smoke 산출물과 `__pycache__`는 정리했다.
In progress
- Python-native orchestrator scaffold 설계
- install 이후 control panel 연결 방식 정리
To confirm
- team manifest 최종 포맷을 `toml`로 확정할지
- control panel 생성을 installer 완료 직후 바로 붙일지, 별도 subcommand로 둘지
- `tmux` / `cmux` launcher를 shell asset 재사용으로 갈지 Python 생성기로 갈지

## Recent Changes

Changes
- `codex-orchestrator/` 프로젝트 생성
- TUI/CLI MVP 구현
- `__codex_agents` 자산 이관
- PRD 및 migration 문서 작성
Validation run
- `python3 -m compileall src`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --project-root .tmp-smoke --agents cto-coordinator,reviewer,code-mapper`
- PTY 환경에서 `PYTHONPATH=src python3 -m codex_orchestrator.cli tui --project-root .tmp-tui`를 키 입력으로 통과시켜 `.codex/agents/*.toml` 생성 확인
Impact
- 이제 새 repo 기준점은 `codex-orchestrator/`이고, `__codex_agents` 없이도 범용 설계 자산을 이 프로젝트에서 참조할 수 있다.

## Known Issues / Watch List

Issue
- 현재 TUI는 curses 기반이라 터미널/PTY 호환성이 완전히 동일하진 않다.
Risk
- shell reference asset은 아직 `__codex_agents` 시대의 `.env` manifest와 경로 가정이 남아 있다.
- 현재 reference 폴더는 “실행 엔트리포인트”가 아니라 “구현 seed”다.
Workaround
- 실제 제품 로직은 `src/codex_orchestrator/`를 source of truth로 본다.
- control panel 구현 시 reference shell asset을 그대로 재사용하지 말고, Python scaffold 기준으로 재생성하는 방향을 우선 검토한다.

## Quick Reference

Key files
- `src/codex_orchestrator/cli.py`
- `src/codex_orchestrator/tui.py`
- `src/codex_orchestrator/catalog.py`
- `docs/PRD.ko.md`
- `docs/MIGRATION_FROM__CODEX_AGENTS.ko.md`
- `reference/legacy_shell_control_plane/README.md`
Commands
- `cd codex-orchestrator`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli tui`
- `PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents reviewer`
Links / dashboards
- 아직 없음. control panel은 다음 단계 구현 대상이다.

## Validation

Checks run
- `compileall`
- catalog 출력
- project-scope install
- curses TUI smoke flow
Results
- 모두 통과
- `.toml` output 포맷은 VoltAgent 스타일을 참고한 최소 필드로 정상 생성됨
Not run yet
- git repo 초기화 후 lint/test 체계
- `.codex/orchestrator` scaffold 생성
- `tmux` / `cmux` control panel 생성 흐름

## Next Actions

1. `install` 완료 직후 `.codex/orchestrator` 기본 scaffold를 생성하는 subcommand 또는 generator를 구현한다.
2. team manifest를 `toml` 기준으로 정의하고, `tmux` / `cmux` control panel 생성 흐름을 installer와 연결한다.

## Resume Checklist

- `README.md`, `docs/PRD.ko.md`, `docs/MIGRATION_FROM__CODEX_AGENTS.ko.md`, `docs/HANDOFF.md`를 먼저 읽는다.
- `PYTHONPATH=src python3 -m codex_orchestrator.cli catalog` 또는 `tui`를 한 번 실행해 현재 상태를 확인한다.
- `reference/legacy_shell_control_plane/`를 보고 어떤 자산을 scaffold 생성기로 끌어올지 결정한다.

## Resume Prompt

Continue this project from `docs/HANDOFF.md`. First verify the repo still matches the notes, then implement the first unfinished next action: generate a `.codex/orchestrator` scaffold after install, using the migrated legacy control-plane assets only as reference, not as the primary runtime.
