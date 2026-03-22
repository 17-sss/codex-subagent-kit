# codex-orchestrator

`codex-orchestrator`는 프로젝트 로컬 `.codex`를 기준으로 subagent를 쉽게 설치하고, 이후 control-plane과 dashboard까지 확장하기 위한 새 프로젝트다.

현재 MVP 범위:

- `Project` 또는 `Global` 설치 위치 선택
- 카테고리별 subagent catalog 제공
- 다중 선택으로 `.codex/agents/*.toml` 생성
- project-scope install 시 `.codex/orchestrator` scaffold와 `team.toml` seed 생성
- project-scope install 시 runtime / queue / dispatch ledger seed 생성
- role-specific terminal board 제공
- project-scope install 시 board/monitor/`tmux`/`cmux` launcher seed 생성
- first-class `launch` CLI 제공
- curses 기반 TUI 제공
- 비대화형 설치 CLI 제공
- `__codex_agents`에서 이관한 control-plane reference asset 보관

후속 범위:

- recovery / bootstrap 고도화
- live pane/session status sync
- live agent integration

## 실행

개발 중에는 프로젝트 루트에서 아래처럼 실행한다.

`pip install -e .`로 설치하면 같은 명령을 `codex-orchestrator ...`로 사용할 수 있다.

프로젝트 루트 기준 예시:

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog --project-root . --scope project
PYTHONPATH=src python3 -m codex_orchestrator.cli panel --project-root .
PYTHONPATH=src python3 -m codex_orchestrator.cli board --project-root . --role cto-coordinator
PYTHONPATH=src python3 -m codex_orchestrator.cli launch --project-root . --backend tmux --dry-run
PYTHONPATH=src python3 -m codex_orchestrator.cli enqueue --project-root . --summary "Investigate the failing review flow"
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-open --project-root .
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-prepare --project-root . --dispatch-id dispatch-001
PYTHONPATH=src python3 -m codex_orchestrator.cli dispatch-begin --project-root . --dispatch-id dispatch-001
PYTHONPATH=src python3 -m codex_orchestrator.cli apply-result --project-root . --dispatch-id dispatch-001 --outcome completed --summary "Done"
PYTHONPATH=src python3 -m codex_orchestrator.cli tui
```

## 개발용 설치 / 제거

개발용으로는 repo-local editable install을 바로 쓸 수 있다.

```bash
./scripts/install.sh
codex-orchestrator --help
./scripts/uninstall.sh
```

기본 동작:

- `install.sh`는 repo 루트에 `.venv/`를 만들고 `pip install -e .`를 수행한다.
- 기본적으로 `~/.local/bin/codex-orchestrator` symlink 생성을 시도한다.
- `~/.local/bin`이 현재 `PATH`에 없으면 `source .venv/bin/activate` 또는 `.venv/bin/codex-orchestrator`로 실행하면 된다.
- `install.sh --dry-run`, `install.sh --no-link`, `uninstall.sh --keep-venv` 같은 옵션이 있다.

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
- `project` scope는 `.codex/orchestrator/launchers/` 아래 board/monitor/backend launcher seed도 함께 만든다.
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
- `dispatch-open`은 다음 `pending` queue command를 `ready` dispatch ticket으로 올리고 queue status를 `claimed`로 바꾼다.
- `dispatch-prepare --dispatch-id ...`는 ready dispatch의 brief와 suggested send_input payload를 렌더링한다.
- `dispatch-begin --dispatch-id ...`는 실제 send 직후 queue/ledger/runtime를 `dispatched` in-flight 상태로 전환한다.
- `apply-result`는 `completed`, `failed`, `cancelled` 중 하나의 결과를 반영해 queue, ledger, runtime state를 함께 갱신한다.
- `dispatch-open`과 `dispatch-begin` 중 target role은 `busy`, `apply-result` 이후에는 `idle` 또는 `blocked`로 정리된다.
- 실제 `send_input` / `wait_agent` 호출은 아직 main Codex conversation 바깥 단계로 남아 있다.

## 현재 board / launcher 동작

- `board --role <role>`는 특정 orchestrator 또는 worker role의 read-only terminal board를 렌더링한다.
- project install은 `.codex/orchestrator/launchers/run-board.sh`, `run-monitor.sh`, `launch-tmux.sh`, `launch-cmux.sh` seed를 생성한다.
- `launch --backend tmux|cmux`는 generated launcher seed를 직접 실행하는 first-class entrypoint다.
- `launch --dry-run`은 backend, launcher path, 최종 command를 실행 없이 출력한다.
- `--no-attach`는 현재 `tmux` backend에만 지원된다.
- generated `tmux` / `cmux` launcher는 backend가 없으면 `SKIP`으로 soft-fail 하도록 생성된다.
- 아직 live queue drain, `spawn_agent` / `send_input` / `wait_agent` 연결은 없다.

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
