# Sub-Agent Dashboard 모드

이 문서는 `launch-subagent-dashboard-tmux.sh`와 `launch-subagent-dashboard-cmux.sh`가 무엇을 하는지 설명한다.

## 이 모드의 목적

이 모드는 pane마다 별도 `codex` 세션을 띄우는 것이 아니다.

대신 아래 구조를 전제로 한다.

- 메인 Codex 대화가 `cto` 역할을 맡는다.
- 실제 `frontend`, `backend`, `core`, `api` sub-agent는 메인 Codex 대화에서 `spawn_agent`로 생성한다.
- `tmux` 또는 `cmux`는 이 팀의 shared 상태를 보는 dashboard로만 사용한다.
- dashboard는 `runtime/teams/<team-id>/subagents/*.env`를 읽어 실제 spawned agent id와 상태를 보여준다.

즉, 이 모드는 "진짜 sub-agent 팀 + 외부 상태판" 버전이다.

## 왜 기존 런처와 다른가

기존 `launch-agent-team-*` 스크립트는 pane마다 `codex`를 띄우므로, 눈에 보이는 건 역할 분리지만 실제로는 서로 독립된 top-level 세션이다.

반면 `launch-subagent-dashboard-*` 스크립트는 pane마다 아래만 보여준다.

- 역할
- repo ownership
- handoff 경로
- 현재 git 상태
- 최근 커밋
- sync 규칙

실제 sub-agent의 생성과 통솔은 main Codex thread가 한다.

## 제공되는 스크립트

- `launch-subagent-dashboard-tmux.sh`
- `launch-subagent-dashboard-cmux.sh`
- `run-subagent-board.sh`
- `run-subagent-monitor.sh`
- `update-subagent-state.sh`
- `enqueue-subagent-command.sh`
- `list-subagent-commands.sh`
- `update-subagent-command.sh`
- `append-subagent-event.sh`

## pane 구성

- `cto`
  - 이 pane은 "실제 sub-agent는 main Codex thread에 있다"는 점과 sync 순서를 지속적으로 보여준다.
- `frontend`
  - React/admin ownership, handoff, repo 상태를 보여준다.
- `backend`
  - NestJS API ownership, handoff, repo 상태를 보여준다.
- `core`
  - Prisma/schema ownership, handoff, repo 상태를 보여준다.
- `api`
  - FastAPI/virtual-resource ownership, handoff, repo 상태를 보여준다.
- `monitor`
  - workspace handoff와 네 repo의 최신 상태를 요약해서 보여준다.

## 사용 방법

tmux:

```bash
./reference/legacy_shell_control_plane/scripts/team-launch-dashboard-tmux.sh example-team
```

cmux:

```bash
./reference/legacy_shell_control_plane/scripts/team-launch-dashboard-cmux.sh example-team
```

이후 실제 운영은 main Codex 대화에서 한다.

1. main Codex가 handoff를 읽는다.
2. main Codex가 `spawn_agent`로 `frontend`, `backend`, `core`, `api` sub-agent를 만든다.
3. 각 sub-agent는 자기 repo ownership만 수행한다.
4. main Codex는 spawned agent 상태를 `runtime/teams/<team-id>/subagents/*.env`에 반영한다.
5. pane이나 shell에서 queue 스크립트로 명령을 넣는다.
6. main Codex는 queue를 읽고 적절한 sub-agent에 `send_input`으로 배분한다.
7. dispatch/completion 결과를 command status와 event log에 반영한다.
8. dashboard pane으로 repo 상태와 handoff freshness를 본다.
9. main Codex가 최종 조정과 통합을 맡는다.

## 한계

- 이 dashboard는 sub-agent의 내부 대화 내용을 pane에 직접 표시하지 않는다.
- 이유는 `spawn_agent`가 shell process가 아니라 Codex 런타임 내부 개체이기 때문이다.
- 따라서 pane에는 실제 sub-agent terminal 대신 shared state, queue, event log, repo 상태만 표시한다.

## Optional 도구 정책

- `tmux` 또는 `cmux`가 없으면 해당 launcher는 `SKIP`으로 종료한다.
- 이것은 실패가 아니라 optional 단계다.
