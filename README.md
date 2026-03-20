# codex-orchestrator

`codex-orchestrator`는 프로젝트 로컬 `.codex`를 기준으로 subagent를 쉽게 설치하고, 이후 control-plane과 dashboard까지 확장하기 위한 새 프로젝트다.

현재 MVP 범위:

- `Project` 또는 `Global` 설치 위치 선택
- 카테고리별 subagent catalog 제공
- 다중 선택으로 `.codex/agents/*.toml` 생성
- project-scope install 시 `.codex/orchestrator` scaffold와 `team.toml` seed 생성
- project-scope install 시 runtime / queue / dispatch ledger seed 생성
- curses 기반 TUI 제공
- 비대화형 설치 CLI 제공
- `__codex_agents`에서 이관한 control-plane reference asset 보관

후속 범위:

- queue / dispatch ledger 확장
- recovery / bootstrap 고도화
- `tmux` / `cmux` control panel

## 실행

프로젝트 루트에서:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog --project-root . --scope project
PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .
PYTHONPATH=src python3 -m codex_orchestrator.cli enqueue --project-root . --summary "Investigate the failing review flow"
PYTHONPATH=src python3 -m codex_orchestrator.cli tui
```

비대화형 설치:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --agents cto-coordinator,reviewer,code-mapper
```

## 테스트 / 검증

이 저장소의 기본 자동 검증 명령:

```bash
./scripts/test.sh
```

개별 명령으로 실행하려면:

```bash
python3 -m compileall src
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

수동 smoke 검증:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli install \
  --scope project \
  --project-root .tmp-smoke \
  --agents cto-coordinator,reviewer
```

`curses` 기반 TUI를 수정한 경우에는 자동 테스트 외에 PTY 환경에서 수동 smoke도 함께 수행한다.

## 현재 install 동작

- `project` scope는 최소 1개의 meta-orchestration agent가 필요하다.
- `project` scope는 `.codex/agents`와 `.codex/orchestrator`를 함께 만든다.
- `global` scope는 `~/.codex/agents`만 다루고 project-local scaffold는 만들지 않는다.

## 현재 discovery 동작

- `catalog --scope project`는 built-in + global + project `.toml` agent를 함께 보여준다.
- `catalog --scope global`는 built-in + global `.toml` agent를 보여준다.
- 같은 key가 겹치면 `project > global > built-in` precedence를 따른다.
- 외부 `.toml`이 built-in key를 override하면 기존 category를 유지하고, 새 key면 `Imported & External` category로 분류한다.

## 현재 panel 동작

- `panel --project-root <path>`는 `.codex/orchestrator/team.toml`과 seed state를 읽어 `operator -> orchestrator -> workers` topology를 텍스트 트리로 렌더링한다.
- orchestrator / worker 상태는 `runtime/agents.toml` 기준으로 표시한다.
- queue 요약은 `queue/commands.toml`, dispatch 요약은 `ledger/dispatches.toml` 기준으로 표시한다.
- `enqueue --summary ...`는 operator command를 project queue에 넣고, 기본 target은 root orchestrator다.
- 아직 live queue drain, `spawn_agent` / `send_input` / `wait_agent` 연결, `tmux` / `cmux` pane 제어는 없다.

## 현재 생성 포맷

생성되는 subagent 파일은 VoltAgent가 사용하는 `.toml` 스타일을 참고해 아래 필드를 쓴다.

- `name`
- `description`
- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `[instructions].text`

## 참고

- 제품 방향 문서: [docs/PRD.ko.md](./docs/PRD.ko.md)
- 이관 메모: [docs/MIGRATION_FROM__CODEX_AGENTS.ko.md](./docs/MIGRATION_FROM__CODEX_AGENTS.ko.md)
- 테스트 workflow: [docs/TESTING.ko.md](./docs/TESTING.ko.md)
- shell control-plane 참고 자산: [reference/legacy_shell_control_plane/README.md](./reference/legacy_shell_control_plane/README.md)
- 이 저장소는 특정 회사/제품명을 전제로 한 예시 자산을 포함하지 않는다.
