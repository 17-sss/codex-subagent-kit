# codex-subagent-kit

영문 기본 문서: [README.md](./README.md)

`codex-subagent-kit`는 프로젝트 또는 글로벌 `.codex` 디렉터리에 Codex subagent 정의를 설치하고 관리하는 local-first 툴킷이다.

현재 제품 구현과 npm 릴리즈 대상은 [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit) 아래의 TypeScript package다.

현재 stable core는 단순하다.

- VoltAgent 기반 기본 catalog와 external/user-authored catalog 탐색
- 호환되는 `.codex/agents/*.toml` 설치
- 새 category / agent template scaffold 생성
- upstream catalog 내용을 project/global source root로 sync
- install-first 흐름을 위한 TUI 제공

`codex-subagent-kit`는 작업공간을 준비하고, 실제 agent thread의 실행과 관리는 `codex`가 맡는다.

## Quick Start

이 저장소에서 현재 TypeScript 구현을 바로 써보려면:

```bash
npm install
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js
```

bare command를 실행하면 install-first TUI가 열린다.

비대화형으로 바로 설치해보려면:

```bash
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
```

## 5-Minute Test Drive

가장 빠르게 end-to-end 확인을 하고 싶다면 아래 흐름을 그대로 실행하면 된다.

```bash
mkdir -p /tmp/codex-subagent-kit-demo
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
node packages/codex-subagent-kit/dist/cli.js usage \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --task "Review the failing auth flow"
cd /tmp/codex-subagent-kit-demo
codex
```

기대 결과:

- `.codex/agents/reviewer.toml`, `.codex/agents/code-mapper.toml`이 생성된다
- `doctor`가 `status: ok`를 출력한다
- `usage`가 Codex에 붙여 넣을 starter prompt를 보여준다

## Stable Workflow

1. `Project` 또는 `Global`을 고른다.
2. vendored VoltAgent snapshot, synced source root, 또는 외부 `categories/` 트리를 본다.
3. 원하는 agent를 선택한다.
4. `.codex/agents/*.toml`을 설치한다.
5. 그 프로젝트에서 `codex`를 실행해 subagent를 사용한다.

이 흐름은 현재 Codex-native 모델과 맞는다. custom agent 정의는 `~/.codex/agents/` 또는 `.codex/agents/`에 두고, 실제 agent thread는 Codex 안에서 spawn되고 관리된다.

## Stable Commands

bare command로 실행하면 기본적으로 TUI가 열린다.

```bash
codex-subagent-kit
```

대부분의 사용자는 아래 stable 명령만 알면 충분하다.

```bash
codex-subagent-kit catalog
codex-subagent-kit catalog sync --scope project --source-root /path/to/awesome-codex-subagents
codex-subagent-kit catalog import --scope project --catalog-root /path/to/categories --agents custom-helper
codex-subagent-kit catalog --catalog-root /path/to/categories
codex-subagent-kit install --scope project --agents reviewer,code-mapper --validate
codex-subagent-kit doctor --scope project --project-root .
codex-subagent-kit usage --scope project --project-root . --task "Review the failing auth flow"
codex-subagent-kit template init --project-root . --category custom-ops --agent custom-coordinator
```

어떤 명령을 써야 할지 헷갈리면 이렇게 보면 된다.

- `catalog`: 현재 보이는 agent 목록을 본다
- `catalog sync`: VoltAgent 기반 source catalog를 갱신한다
- `install`: project/global 범위에 `.codex/agents/*.toml`을 설치한다
- `doctor`: 설치된 TOML과 catalog root를 검증한다
- `usage`: 설치된 agent 기준으로 Codex starter prompt를 만든다
- `template init`: 직접 쓸 category/agent template를 scaffold한다

## Catalog Model

- 기본 built-in catalog는 VoltAgent [`awesome-codex-subagents/categories`](https://github.com/VoltAgent/awesome-codex-subagents/tree/main/categories)의 vendored snapshot이다
- project-local synced source root는 `.codex/subagent-kit/sources/<source>/categories/` 아래에 있다
- global synced source root는 `~/.codex/subagent-kit/sources/<source>/categories/` 아래에 있다
- project-local injection 경로는 `.codex/subagent-kit/catalog/categories/`이다
- global injection 경로는 `~/.codex/subagent-kit/catalog/categories/`이다
- `--catalog-root <path>`로 awesome-style `categories/` 트리를 직접 주입할 수 있다
- `catalog sync`로 VoltAgent upstream 또는 local awesome-style clone에서 synced source root를 갱신할 수 있다
- `catalog import`로 선택한 category 또는 agent를 injection 경로에 영구 반영할 수 있다
- 사용자가 직접 만든 템플릿도 같은 폴더 형식을 따르면 같은 install 흐름에 참여할 수 있다

merge된 catalog precedence는 다음 순서다.

- built-in VoltAgent snapshot
- global synced source root
- global user catalog injection root
- project synced source root
- project user catalog injection root
- 명시적인 `--catalog-root`

설치된 agent 파일의 최종 precedence는 scope 기준으로:

- `project`
- `global`

## Template Scaffolding

project-local injection 경로에 새 category와 agent template를 만든다.

```bash
codex-subagent-kit template init \
  --project-root . \
  --category custom-ops \
  --agent custom-coordinator
```

외부 `categories/` 트리에 직접 생성할 수도 있다.

```bash
codex-subagent-kit template init \
  --catalog-root /path/to/categories \
  --category custom-ops \
  --agent custom-coordinator \
  --orchestrator
```

외부 템플릿을 project-local injection 경로로 영구 가져올 수도 있다.

```bash
codex-subagent-kit catalog import \
  --scope project \
  --project-root . \
  --catalog-root /path/to/categories \
  --agents custom-helper,custom-reviewer
```

local clone에서 project-local VoltAgent source root를 갱신:

```bash
codex-subagent-kit catalog sync \
  --scope project \
  --project-root . \
  --source-root /path/to/awesome-codex-subagents
```

VoltAgent GitHub `main/categories`에서 직접 갱신:

```bash
codex-subagent-kit catalog sync --scope project --project-root .
```

생성되는 agent 파일은 Codex-compatible TOML 형식을 따른다.

- `name`
- `description`
- `model`
- `model_reasoning_effort`
- `sandbox_mode`
- `developer_instructions`

## Validation

install 이후에는 `doctor`로 현재 보이는 agent 파일과 주입된 catalog root가 아직 정상 형식인지 확인할 수 있다. 한 번에 끝내고 싶다면 `install --validate`를 쓰면 된다.

```bash
codex-subagent-kit install --scope project --agents reviewer,code-mapper --validate
codex-subagent-kit doctor --scope project --project-root .
```

TUI install 흐름도 성공적인 설치 뒤에 같은 validation을 자동으로 실행하고, 완료 화면에 validation 상태를 함께 보여준다.

## Usage Helper

`usage`는 현재 scope에서 실제로 보이는 installed agent를 기준으로 Codex에 바로 붙여 넣을 starter prompt를 만들어준다. meta-orchestration agent가 설치돼 있으면 그쪽을 우선 활용하고, 없으면 specialist 직접 호출 예시를 제안한다.

```bash
codex-subagent-kit usage \
  --scope project \
  --project-root . \
  --task "Review the failing auth flow"
```

설치 후 Codex에 바로 이렇게 말하면 된다.

- `Use reviewer to review the current changes for bugs, regressions, and missing tests.`
- `Use code-mapper to map the auth flow before we change it.`

## TypeScript 패키지 상태

TypeScript 패키지는 이제 stable CLI surface의 source of truth다. `catalog`, `catalog sync`, `catalog import`, `template init`, `install`, `doctor`, `usage`, install-first interactive `tui`가 동작하고, bare command entrypoint도 interactive install flow를 연다. shared golden fixture로 generated TOML과 `usage`, `doctor` 출력도 함께 검증한다.

부트스트랩 검증 명령:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
node packages/codex-subagent-kit/dist/cli.js --help
node packages/codex-subagent-kit/dist/cli.js
node packages/codex-subagent-kit/dist/cli.js catalog
node packages/codex-subagent-kit/dist/cli.js catalog sync --scope project --project-root /tmp/example --source-root /tmp/awesome-codex-subagents
node packages/codex-subagent-kit/dist/cli.js catalog import --scope project --project-root /tmp/example --catalog-root /tmp/categories --agents custom-helper
node packages/codex-subagent-kit/dist/cli.js install --scope project --project-root /tmp/example --agents reviewer,code-mapper --validate
node packages/codex-subagent-kit/dist/cli.js usage --scope project --project-root /tmp/example --task "Review the failing auth flow"
```

## 테스트 / 검증

기본 자동 검증 명령:

```bash
./scripts/test.sh
```

개별 명령으로 실행하려면:

```bash
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
npm run smoke:ts:consumer
```

TUI를 수정했다면 자동 테스트 외에 interactive smoke도 한 번 같이 확인하면 된다.

## 참고

- 제품 방향: [docs/PRD.ko.md](./docs/PRD.ko.md)
- 제품 이해 / workflow: [docs/UNDERSTANDING_AND_WORKFLOW.ko.md](./docs/UNDERSTANDING_AND_WORKFLOW.ko.md)
- 테스트 workflow: [docs/TESTING.ko.md](./docs/TESTING.ko.md)
- PR CI workflow: [docs/TESTING.ko.md](./docs/TESTING.ko.md)
- 릴리즈 workflow: [docs/RELEASING.ko.md](./docs/RELEASING.ko.md)
- TypeScript/npm 포팅 계획: [docs/TYPESCRIPT_PORT.ko.md](./docs/TYPESCRIPT_PORT.ko.md)
