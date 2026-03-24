# TYPESCRIPT PORT

영문 기본 문서: [TYPESCRIPT_PORT.md](./TYPESCRIPT_PORT.md)

## 목적

TypeScript 포팅의 목적은 `codex-subagent-kit`의 stable product core를 유지한 채 npm에 배포 가능한 CLI를 만드는 것이다.

이 작업은 제품을 다시 정의하는 것이 아니라, 이미 안정화된 Python 동작을 기준으로 언어와 패키징 방식을 옮기는 작업이다.

## 현재 워크스페이스 부트스트랩

현재 저장소에는 [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit) 경로의 dedicated TypeScript workspace가 있다.

이 패키지는 parity를 끝낸 대체 구현이 아니라, 이후 포팅 작업이 바로 이어질 수 있도록 npm 패키지 형태와 CLI entrypoint를 먼저 잡아둔 bootstrap이다.

현재 구현된 슬라이스:

- shared path helper
- catalog data model
- TypeScript workspace 안의 built-in catalog asset
- 실제로 동작하는 `catalog` 명령
- 실제로 동작하는 `template init` 명령
- 실제로 동작하는 `install` 명령
- 실제로 동작하는 `doctor` 명령
- 실제로 동작하는 `install --validate` 흐름

현재 부트스트랩 검증 명령:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js --help
```

## 먼저 포팅할 Stable 범위

첫 TypeScript 릴리즈는 stable CLI surface만 다룬다.

- 기본 명령 실행 시 열리는 install-first TUI
- `catalog`
- `catalog import`
- `install`
- `doctor`
- `usage`
- `template init`
- TUI install flow

## 첫 포팅에서 제외할 범위

첫 TypeScript 포팅에서는 experimental companion layer를 옮기지 않는다.

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

이 명령들은 당분간 Python에 남겨두거나, stable npm package가 나온 뒤 다시 검토한다.

## Parity Contract

TypeScript CLI는 Python stable core의 사용자 경험을 최대한 유지해야 한다.

우선적으로 맞춰야 할 parity 대상:

- generated `.codex/agents/*.toml` 포맷
- catalog precedence 규칙
- template scaffold 출력
- `doctor`의 성공/실패 리포트
- `usage` 출력 구조
- stable command의 exit-code 동작

기준선으로 삼을 Python 계약:

- [tests/fixtures/golden](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/tests/fixtures/golden)의 golden fixture
- [tests/test_cli.py](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/tests/test_cli.py)에 고정된 CLI 동작

## 추천 스택

브라우저 중심 빌드 도구보다 Node CLI 스택을 쓰는 편이 맞다.

추천 baseline:

- TypeScript
- Node.js CLI runtime
- command parsing: `commander`
- TUI: `ink` 또는 `blessed`
- TOML 처리: `@iarna/toml` 또는 동급 라이브러리
- 패키징: `tsup`

핵심 CLI 패키지에는 `Vite`를 쓰지 않는 편이 낫다. 파일시스템 중심 터미널 도구에는 자연스러운 선택이 아니다.

## 권장 작업 순서

1. 전용 TypeScript package/workspace 생성
2. 공통 data model과 filesystem path helper 구현
3. catalog loading과 TOML rendering 포팅
4. `template init` 포팅
5. `install` 포팅
6. `doctor` 포팅
7. `usage` 포팅
8. install-first TUI 포팅
9. Python 계약과 비교하는 fixture 기반 parity test 추가
10. npm metadata와 publish workflow 준비

## TypeScript 포트의 릴리즈 준비 조건

npm package를 publish하기 전에 아래를 확인해야 한다.

- stable command가 문서/예시 기준으로 Python과 충분히 같은 동작을 한다
- generated TOML이 Codex에서 실제로 받아들여진다
- package name, README, 예시가 npm 사용 방식에 맞게 정리돼 있다
- TypeScript package 전용 CI와 release path가 준비돼 있다

## 현재 결정

첫 TypeScript CLI가 stable-core parity에 도달하기 전까지는 Python 버전을 source of truth로 유지한다.
