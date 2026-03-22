# Understanding And Workflow

영문 기본 문서: [UNDERSTANDING_AND_WORKFLOW.md](./UNDERSTANDING_AND_WORKFLOW.md)

## 내가 현재 이해한 제품 방향

- 이 프로젝트의 목적은 단순히 `.codex/agents/*.toml` 파일을 만드는 설치기가 아니다.
- 최종 목적은 프로젝트 로컬 `.codex`를 기준으로 멀티 에이전트 팀을 구성하고 운영하는 control-plane을 만드는 것이다.
- 사용자는 대표 또는 operator로서 루트 orchestrator에게 명령을 내린다.
- orchestrator는 CTO 같은 단일 루트 에이전트로서 하위 subagent들에게 작업을 위임한다.
- control panel은 이 위계가 항상 드러나야 한다.
- 따라서 제품 정체성은 `subagent installer`보다 `orchestrated subagent team builder/control-plane`에 가깝다.

## 현재까지 합의한 핵심 원칙

- 설치 위치는 `Project`와 `Global` 두 가지를 지원한다.
- static agent definition은 `.codex/agents`에 둔다.
- runtime/control-plane 관련 자산은 `.codex/orchestrator`에 둔다.
- agent 정의의 canonical format은 Codex-compatible TOML이어야 한다.
- TOML 구조는 VoltAgent가 사용하는 형태를 강하게 참고하되, 특정 repo 전용 구조로 묶지는 않는다.
- built-in agent뿐 아니라 나중에 사용자가 직접 만든 `.toml` agent도 같은 생태계 안에 추가될 수 있어야 한다.
- 최상단 control panel에는 반드시 root orchestrator가 있어야 한다.

## 현재 구현 상태와 목표 상태

### 현재 구현됨

- `Project` / `Global` scope 선택
- built-in + discovered `.toml` source 기반 agent 선택
- 선택한 agent를 `.codex/agents/*.toml`로 생성
- generated agent는 VoltAgent-style Codex-compatible TOML에 가깝게 출력
- project-scope install 시 `.codex/orchestrator` scaffold 생성
- root orchestrator가 들어간 `team.toml` seed 생성
- runtime / queue / dispatch ledger seed 생성
- `panel` 명령으로 topology + seeded runtime summary 렌더링 가능
- `board` 명령으로 role-specific terminal board 렌더링 가능
- `enqueue` 명령으로 operator command를 queue에 적재 가능
- `dispatch-open` 명령으로 queue command를 dispatch ledger로 승격 가능
- `dispatch-prepare` 명령으로 ready dispatch handoff package 렌더링 가능
- `dispatch-begin` 명령으로 in-flight `dispatched` 상태 전환 가능
- `apply-result` 명령으로 dispatch outcome을 queue / ledger / runtime에 반영 가능
- project-local launcher seed 생성
- `launch` 명령으로 generated `tmux` / `cmux` launcher 실행 또는 dry-run 가능
- CLI와 설치용 TUI 제공

### 아직 미구현

- live runtime-aware terminal control panel
- actual `spawn_agent` / `send_input` / `wait_agent` integration
- live queue drain 및 pane/session status sync

## Workflow Diagram

```mermaid
flowchart TD
    U[User / Operator]
    O[Root Orchestrator<br/>CTO-like coordinator]
    W1[Worker Subagent A]
    W2[Worker Subagent B]
    W3[Worker Subagent C]

    U -->|gives task| O
    O -->|delegates| W1
    O -->|delegates| W2
    O -->|delegates| W3
    W1 -->|reports back| O
    W2 -->|reports back| O
    W3 -->|reports back| O
    O -->|final answer / coordination result| U
```

## Product Workflow

```mermaid
flowchart LR
    A[1. Choose Scope<br/>Project or Global]
    B[2. Discover Agent Definitions<br/>Built-in + external TOML]
    C[3. Select Team Composition<br/>root orchestrator + workers]
    D[4. Generate Assets<br/>.codex/agents + .codex/orchestrator]
    E[5. Render Control Panel<br/>terminal topology + state seed view]
    F[6. Runtime Delegation<br/>operator -> orchestrator -> workers]

    A --> B --> C --> D --> E --> F
```

## Directory Model

```text
.codex/
├── agents/
│   ├── orchestrator.toml
│   ├── reviewer.toml
│   ├── code-mapper.toml
│   └── ...
└── orchestrator/
    ├── team.toml
    ├── runtime/
    ├── queue/
    ├── ledger/
    └── launchers/
```

## 중요한 드리프트

- terminal control panel은 seed file을 읽는 summary 단계까지만 있고, live runtime/queue drain/pane orchestration은 아직 없다.
- built-in source는 여전히 Python 코드에 남아 있고, 아직 packaged TOML library로 옮겨지진 않았다.
- 따라서 다음 단계는 generated team metadata를 panel runtime에 연결하고, 필요하면 built-in source도 파일 기반 구조로 옮기는 것이다.

## 다음 구현 우선순위

1. actual `send_input` / `wait_agent` integration 방향을 thin slice로 연결한다.
2. 필요하면 built-in source도 portable file-based catalog로 정리한다.
