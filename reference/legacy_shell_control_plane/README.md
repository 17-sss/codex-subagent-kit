# legacy_shell_control_plane

이 폴더는 과거 `__codex_agents`에서 검증했던 shell 기반 control-plane 자산 중, 현재 `codex-orchestrator`에 참고 가치가 있는 파일만 이관해 둔 reference 영역이다.

## 이 폴더의 목적

- 새 Python 프로젝트에서 control panel 기능을 구현할 때 참고할 seed asset 보존
- queue / dispatch / recovery / dashboard 흐름의 shell 선행 구현 보관
- `__codex_agents` 폴더를 제거해도 설계와 동작 예시를 잃지 않도록 백업

## 여기 있는 것

- `scripts/`
  - generic team manifest 기반 shell control-plane 스크립트
  - queue, dispatch ledger, runtime state, dashboard launch 관련 흐름
- `docs/`
  - `TEAM_MANIFEST.md`
  - `TEAM_CONTROL_PLANE.md`
  - `SUBAGENT_DASHBOARD.md`

## 여기 없는 것

- 세션성 runtime state
- event log
- pending/archive queue 파일
- 특정 workspace 현재 상태 스냅샷

그런 값은 새 프로젝트의 source of truth가 되면 안 되므로 이관하지 않았다.

## 사용 원칙

- 이 폴더는 현재 제품의 실행 엔트리포인트가 아니다.
- 현재 실행 엔트리포인트는 `src/codex_orchestrator/` 아래 Python 코드다.
- 이 폴더는 control panel, recovery, queue, dispatch 기능을 구현할 때 참고하는 자료다.

## 다음 단계

- shell 스크립트의 개념을 Python 및 template 기반 scaffold로 재구성
- `.env` manifest를 `.toml` manifest로 전환
- `tmux` / `cmux` launcher를 installer와 연결
