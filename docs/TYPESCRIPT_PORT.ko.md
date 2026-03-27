# TYPESCRIPT PORT

영문 기본 문서: [TYPESCRIPT_PORT.md](./TYPESCRIPT_PORT.md)

## 목적

TypeScript 마이그레이션은 stable product surface 기준으로 완료됐다. 이제 `codex-subagent-kit`는 [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit) 아래의 npm-oriented CLI로 배포된다.

## 현재 TypeScript 상태

TypeScript package가 제품 source of truth이며 npm release target이다.

현재 구현된 슬라이스:

- shared path helper
- catalog data model
- TypeScript workspace 안의 vendored VoltAgent catalog snapshot
- 실제로 동작하는 `catalog` 명령
- 실제로 동작하는 `catalog sync` 명령
- 실제로 동작하는 `catalog import` 명령
- 실제로 동작하는 `template init` 명령
- 실제로 동작하는 `install` 명령
- 실제로 동작하는 `doctor` 명령
- 실제로 동작하는 `install --validate` 흐름
- 실제로 동작하는 `usage` 명령
- 실제로 동작하는 prompt-driven install-first `tui`
- interactive install flow를 여는 bare command entrypoint
- generated TOML, `usage`, `doctor`에 대한 shared fixture-based parity test

현재 검증 명령:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
node packages/codex-subagent-kit/dist/cli.js --help
node packages/codex-subagent-kit/dist/cli.js
```

현재 stable CLI surface는 다음을 포함한다.

- 기본 명령 실행 시 열리는 install-first TUI
- `catalog`
- `catalog sync`
- `catalog import`
- `install`
- `doctor`
- `usage`
- `template init`
- TUI install flow

## Contract

TypeScript CLI는 마이그레이션 중 확정된 stable user-facing contract를 유지한다.

우선적으로 맞춰야 할 parity 대상:

- generated `.codex/agents/*.toml` 포맷
- catalog precedence 규칙
- template scaffold 출력
- `doctor`의 성공/실패 리포트
- `usage` 출력 구조
- stable command의 exit-code 동작

release contract는 package-local fixture와 테스트로 고정한다.

- [packages/codex-subagent-kit/test/fixtures/golden](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/test/fixtures/golden)의 golden fixture
- [packages/codex-subagent-kit/test](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/test)에 고정된 CLI 동작

## 추천 스택

브라우저 중심 빌드 도구보다 Node CLI 스택을 쓰는 편이 맞다.

추천 baseline:

- TypeScript
- Node.js CLI runtime
- command parsing: `commander`
- 첫 interactive TUI 구현: `@inquirer/prompts`
- TOML 처리: `@iarna/toml` 또는 동급 라이브러리
- 패키징: `tsup`

핵심 CLI 패키지에는 `Vite`를 쓰지 않는 편이 낫다. 파일시스템 중심 터미널 도구에는 자연스러운 선택이 아니다.

## 릴리즈 준비 조건

npm package를 publish하기 전에 아래를 확인해야 한다.

- generated TOML이 Codex에서 실제로 받아들여진다
- package name, README, 예시가 npm 사용 방식에 맞게 정리돼 있다
- `npm pack --dry-run` 결과가 기대한 package contents를 보여준다
- TypeScript package 전용 CI와 release path가 준비돼 있다

현재 저장소에는 이미 아래가 포함되어 있다.

- TypeScript package용 PR CI
- semver release workflow
- published GitHub Release에서 실행되는 npm publish workflow
