# Team Control Plane

이 문서는 manifest 기반 팀 런타임에서 `bootstrap`, `recovery`, `queue`, `dispatch ledger`, `dispatch brief`가 어떻게 이어지는지 설명한다.

## 왜 필요한가

`tmux`/`cmux` dashboard는 상태를 보여주지만, 실제 `spawn_agent`, `send_input`, `wait_agent`는 main Codex conversation만 할 수 있다.

그래서 실사용 가능한 흐름을 만들려면 다음 두 층을 분리해야 한다.

- shell/runtime 층
  - manifest 로딩
  - queue/event log/state 파일 관리
  - dispatch ledger 관리
  - dashboard 표시
  - 다음 명령 pick/claim
- main Codex 층
  - 실제 sub-agent spawn
  - 실제 sub-agent dispatch
  - 결과 수집과 상태 반영

즉, 이 문서의 스크립트들은 완전 자동 에이전트 오케스트레이터가 아니라, main Codex가 개입하기 직전까지를 표준화하는 control plane이다.

## 핵심 스크립트

- `team-bootstrap-runtime.sh <team> [preserve|disconnect]`
  - runtime 디렉터리와 state 파일을 준비하고, repo snapshot 기준으로 상태를 한 번 정리한다.
- `team-recover-runtime.sh <team> [preserve|disconnect]`
  - 세션이 끊긴 뒤 dashboard/runtime를 다시 세운다.
  - `disconnect` 모드는 live agent id를 비우고 `needs-rebind` 상태로 전환한다.
- `team-enqueue-command.sh <team> <role> "<command>" [source] [priority]`
  - role 앞으로 새 명령을 pending queue에 넣는다.
- `team-pick-command.sh <team> [role|all] [summary|id|env|path]`
  - 아직 claim되지 않은 다음 명령을 priority/created_at 기준으로 고른다.
- `team-claim-command.sh <team> <command-id> [claimer] [note]`
  - command를 `claimed`로 바꾸고 coordinator가 집었다는 흔적을 남긴다.
- `team-open-dispatch.sh <team> [role|all] [claimer]`
  - queue command를 live agent 대상으로 dispatch ticket으로 승격한다.
- `team-list-dispatches.sh <team> [all|ready|active|archive] [role|all]`
  - dispatch ledger를 조회한다.
- `team-update-dispatch.sh <team> <dispatch-id> <state> [note] [agent-id]`
  - dispatch 상태를 직접 조정한다.
- `team-render-dispatch-brief.sh <team> <command-id>`
  - owner scope, handoff, sync rule, runtime state를 한 번에 보여준다.
- `team-render-dispatch-message.sh <team> <dispatch-id>`
  - 실제 `send_input`용 메시지를 렌더한다.
- `team-prepare-dispatch.sh <team> [role|all] [claimer]`
  - `open dispatch -> brief -> send_input message`를 한 번에 출력한다.
- `team-begin-dispatch.sh <team> <dispatch-id> [note]`
  - 실제 `send_input` 직후 dispatch를 `dispatched`로 전환하고 queue/runtime/event를 같이 갱신한다.
- `team-apply-agent-result.sh <team> <dispatch-id> <completed|failed|cancelled> "<summary>"`
  - `wait_agent` 결과를 dispatch ledger, queue, runtime state, event log에 반영한다.

## 권장 운영 순서

### 1. 새 세션 시작

```bash
./reference/legacy_shell_control_plane/scripts/team-bootstrap-runtime.sh example-team preserve
```

새 대화라서 기존 live agent binding이 불확실하면:

```bash
./reference/legacy_shell_control_plane/scripts/team-bootstrap-runtime.sh example-team disconnect
```

### 2. dashboard 열기

```bash
./reference/legacy_shell_control_plane/scripts/team-launch-dashboard-cmux.sh example-team
```

또는

```bash
./reference/legacy_shell_control_plane/scripts/team-launch-dashboard-tmux.sh example-team
```

### 3. pane/shell에서 역할 앞으로 명령 enqueue

```bash
./reference/legacy_shell_control_plane/scripts/team-enqueue-command.sh example-team frontend "Investigate a UI regression" cmux high
```

### 4. coordinator가 dispatch ticket 생성

```bash
./reference/legacy_shell_control_plane/scripts/team-prepare-dispatch.sh example-team
```

role을 지정하고 싶으면:

```bash
./reference/legacy_shell_control_plane/scripts/team-prepare-dispatch.sh example-team frontend
```

이 명령은 dispatch id와 함께:

- command/runtime brief
- ready-to-send `send_input` message

를 같이 출력한다.

### 5. main Codex conversation이 실제 dispatch

위 스크립트는 dispatch ticket과 메시지까지만 만든다. 실제 `send_input`은 main Codex conversation이 수행해야 한다.

실제 `send_input`을 보낸 직후:

```bash
./reference/legacy_shell_control_plane/scripts/team-begin-dispatch.sh example-team <dispatch-id>
```

### 6. `wait_agent` 결과 반영

```bash
./reference/legacy_shell_control_plane/scripts/team-apply-agent-result.sh example-team <dispatch-id> completed "요약"
```

또는 실패/취소:

```bash
./reference/legacy_shell_control_plane/scripts/team-apply-agent-result.sh example-team <dispatch-id> failed "실패 요약"
```

## queue와 dispatch의 차이

- queue command
  - 사람이 넣은 작업 요청
  - 아직 배분 전인 업무 backlog
- dispatch ticket
  - 특정 live agent에게 실제로 배분하려는 시도
  - 재시도/실패/완료 기록의 단위

즉, 하나의 queue command에서 여러 dispatch 시도가 생길 수 있게 확장할 수 있다. 지금 버전은 보통 1 command -> 1 dispatch 흐름으로 운용한다.

## 현재 가능한 자동화 수준

지금 단계에서 표준화된 흐름은 이렇다.

1. shell/pane이 queue에 command를 넣는다.
2. coordinator가 dispatch ticket을 연다.
3. main Codex가 실제 `send_input`을 한다.
4. `wait_agent` 결과를 다시 runtime에 반영한다.

즉, control plane은 파일 기준으로 정리됐지만, **실제 tool 호출인 `send_input`/`wait_agent`는 아직 main Codex가 수행**한다.

## 아직 수동인 부분

아래는 아직 shell만으로 자동화되지 않는다.

- 실제 `spawn_agent`
- 실제 `send_input`
- `wait_agent` polling
- queue 자동 drain background loop

즉, 현재 단계는 `관제판 + control plane + dispatch ledger + main Codex 수동 dispatch`까지다.

## 실사용 판단

이 단계면 “실험용 대시보드”는 넘었고, “운영 보조 도구”로는 쓸 수 있다.

다만 아직 완전한 제품 수준은 아니다. 제품 수준으로 가려면 결국 별도 broker/dispatcher 계층이 필요하다.
