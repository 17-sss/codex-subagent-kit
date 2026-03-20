# `__codex_agents` 이관 메모

## 목적

기존 `__codex_agents` 폴더를 제거하기 전에, 새 `codex-orchestrator` 프로젝트로 재사용 가능한 자산을 이관한 내역을 정리한다.

## 이관한 것

### 1. 설계 / 운영 문서

- `reference/legacy_shell_control_plane/docs/TEAM_MANIFEST.md`
- `reference/legacy_shell_control_plane/docs/TEAM_CONTROL_PLANE.md`
- `reference/legacy_shell_control_plane/docs/SUBAGENT_DASHBOARD.md`

### 2. generic shell control-plane 자산

- `reference/legacy_shell_control_plane/scripts/*.sh`

범위:

- team manifest load
- runtime state 갱신
- queue
- dispatch ledger
- bootstrap / recovery
- `tmux` / `cmux` dashboard launcher

## 이관하지 않은 것

- `__codex_agents/runtime/`
- event log
- queue archive
- dispatch archive
- live agent id와 상태 파일
- 특정 workspace에 종속된 역할/프롬프트/팀 예시

이 값들은 세션성 산출물이므로 제품 asset로 옮기지 않았다.
마지막 항목은 새 프로젝트가 개인용 범용 도구로 전환되면서 의도적으로 제외했다.

## 새 기준 구조

- 실행 코드: `src/codex_orchestrator/`
- 제품 문서: `docs/`
- shell 기반 reference asset: `reference/legacy_shell_control_plane/`

## 해석 기준

- `reference/`는 “과거에 검증된 구현 참고본”
- `src/`는 “현재 제품의 source of truth”

즉, 앞으로 기능 추가는 `src/`와 `docs/`를 기준으로 하고, `reference/`는 구현 참고와 스캐폴드 설계 입력으로 쓴다.
