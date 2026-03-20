# Team Manifest 런타임

이 문서는 `team manifest` 기반 범용 팀 오케스트레이션 구조를 설명한다.

## 목적

기존 특정 workspace 전용 스크립트는 빠르게 시작하기엔 좋지만, 프로젝트가 바뀔 때마다 경로와 역할을 다시 하드코딩해야 한다.

그래서 범용 구조는 다음 원칙을 따른다.

- 프로젝트별 차이는 `teams/<team>/team.env`, `teams/<team>/roles/*.env`에만 둔다.
- dashboard, queue, event log, runtime state는 generic script가 처리한다.
- main Codex conversation만 실제 `spawn_agent`를 호출한다.
- role onboarding prompt도 manifest에서 조합한다.

## 핵심 스크립트

- `team-launch-dashboard-cmux.sh <team>`
- `team-launch-dashboard-tmux.sh <team>`
- `team-run-board.sh <team> <role>`
- `team-run-monitor.sh <team>`
- `team-render-role-prompt.sh <team> <role>`
- `team-update-agent-state.sh <team> <role>`
- `team-enqueue-command.sh <team> <role> "<command>"`
- `team-list-commands.sh <team> [role]`
- `team-pick-command.sh <team> [role]`
- `team-claim-command.sh <team> <command-id>`
- `team-open-dispatch.sh <team> [role]`
- `team-list-dispatches.sh <team> [state] [role]`
- `team-update-dispatch.sh <team> <dispatch-id> <state>`
- `team-render-dispatch-brief.sh <team> <command-id>`
- `team-render-dispatch-message.sh <team> <dispatch-id>`
- `team-prepare-dispatch.sh <team> [role]`
- `team-begin-dispatch.sh <team> <dispatch-id>`
- `team-apply-agent-result.sh <team> <dispatch-id> <outcome> "<summary>"`
- `team-bootstrap-runtime.sh <team> [preserve|disconnect]`
- `team-recover-runtime.sh <team> [preserve|disconnect]`
- `team-update-command.sh <team> <command-id> <status> [note] [agent-id]`
- `team-append-event.sh <team> <role> <type> "<message>"`

## runtime 경로

generic team runtime은 아래 경로를 쓴다.

- `runtime/teams/<team-id>/subagents`
- `runtime/teams/<team-id>/queue/pending`
- `runtime/teams/<team-id>/queue/archive`
- `runtime/teams/<team-id>/dispatch/ready`
- `runtime/teams/<team-id>/dispatch/active`
- `runtime/teams/<team-id>/dispatch/archive`
- `runtime/teams/<team-id>/events`

## 예시

```bash
./reference/legacy_shell_control_plane/scripts/team-launch-dashboard-cmux.sh example-team
```

role onboarding prompt 렌더:

```bash
./reference/legacy_shell_control_plane/scripts/team-render-role-prompt.sh example-team frontend
```

queue 예시:

```bash
./reference/legacy_shell_control_plane/scripts/team-enqueue-command.sh example-team frontend "Investigate a UI regression" cmux high
```

dispatch 준비 예시:

```bash
./reference/legacy_shell_control_plane/scripts/team-prepare-dispatch.sh example-team
```

dispatch ledger 조회:

```bash
./reference/legacy_shell_control_plane/scripts/team-list-dispatches.sh example-team all
```

이 흐름의 자세한 설명은 `TEAM_CONTROL_PLANE.md`를 본다.
