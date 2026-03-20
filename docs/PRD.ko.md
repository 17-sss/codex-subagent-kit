# PRD: codex-orchestrator

## 목적

`codex-orchestrator`는 프로젝트 로컬 `.codex` 기반으로 subagent를 쉽게 설치하고, 이후 queue/dispatch/control panel까지 확장할 수 있는 멀티 에이전트 운영 도구를 만든다.

## 현재 단계

현재 구현 목표는 다음의 vertical slice다.

1. 설치 위치 선택
   - `Project`
   - `Global`
2. 카테고리별 subagent 선택
3. canonical `.codex/agents/*.toml` 생성
4. project-scope `.codex/orchestrator` scaffold seed 생성

현재 실제로 들어간 것:

- curses 기반 TUI
- 비대화형 install CLI
- 카테고리형 built-in subagent catalog
- project/global `.toml` source discovery와 precedence
- VoltAgent-style Codex-compatible TOML output
- root orchestrator가 포함된 project-scope `team.toml` seed
- runtime / queue / dispatch ledger seed
- `team.toml` + seeded state 기반 terminal panel renderer
- role-specific terminal board renderer
- operator command를 queue에 넣는 최소 control-plane mutation
- queue command를 `ready` dispatch ticket으로 여는 최소 control-plane mutation
- dispatch 결과를 queue / ledger / runtime state에 적용하는 최소 control-plane mutation
- project-local board/monitor/`tmux`/`cmux` launcher seed
- generated launcher를 실행하는 first-class `launch` CLI
- `__codex_agents`에서 이관한 shell control-plane reference asset

## 최종 방향

- `.codex/agents`
  - Codex-native subagent 정의
- `.codex/orchestrator`
  - team manifest
  - runtime state
  - queue / dispatch ledger
  - bootstrap / recovery
  - `tmux` / `cmux` control panel

## 제품 원칙

- Codex-native first
- Local-over-global
- explicit delegation
- static definition과 runtime state 분리
- dashboard는 optional
- 특정 회사/제품명에 묶인 예시를 기본 제공하지 않음

## MVP 이후

- role별 project-specific owner agent 생성기
- actual `send_input` / `wait_agent` integration
- queue / dispatch / recovery 통합
- seeded panel을 live runtime control panel로 확장
- reference shell asset에서 Python-native control-plane으로 점진 이관
