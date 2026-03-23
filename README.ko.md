# codex-orchestrator

영문 기본 문서: [README.md](./README.md)

`codex-orchestrator`는 프로젝트 또는 글로벌 `.codex` 디렉터리에 Codex subagent 정의를 설치하고 관리하는 local-first 툴킷이다.

현재 stable core는 단순하다.

- built-in / external agent catalog 탐색
- 호환되는 `.codex/agents/*.toml` 설치
- 새 category / agent template scaffold 생성
- install-first 흐름을 위한 TUI 제공

`codex-orchestrator`는 작업공간을 준비하고, 실제 agent thread의 실행과 관리는 `codex`가 맡는다.

## Stable Workflow

1. `Project` 또는 `Global`을 고른다.
2. built-in 템플릿이나 외부 `categories/` 트리를 본다.
3. 원하는 agent를 선택한다.
4. `.codex/agents/*.toml`을 설치한다.
5. 그 프로젝트에서 `codex`를 실행해 subagent를 사용한다.

이 흐름은 현재 Codex-native 모델과 맞는다. custom agent 정의는 `~/.codex/agents/` 또는 `.codex/agents/`에 두고, 실제 agent thread는 Codex 안에서 spawn되고 관리된다.

## Stable Commands

bare command로 실행하면 기본적으로 TUI가 열린다.

```bash
codex-orchestrator
```

대부분의 사용자는 아래 stable 명령만 알면 충분하다.

```bash
codex-orchestrator catalog
codex-orchestrator catalog import --scope project --catalog-root /path/to/categories --agents custom-helper
codex-orchestrator catalog --catalog-root /path/to/categories
codex-orchestrator install --scope project --agents cto-coordinator,reviewer,code-mapper --validate
codex-orchestrator doctor --scope project --project-root .
codex-orchestrator usage --scope project --project-root . --task "Review the failing auth flow"
codex-orchestrator template init --project-root . --category custom-ops --agent custom-coordinator
```

개발 중에는 repo 루트에서 직접 실행할 수도 있다.

```bash
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog
PYTHONPATH=src python3 -m codex_orchestrator.cli catalog import --scope project --catalog-root /path/to/categories --agents custom-helper
PYTHONPATH=src python3 -m codex_orchestrator.cli install --scope project --agents cto-coordinator,reviewer --validate
PYTHONPATH=src python3 -m codex_orchestrator.cli doctor --scope project --project-root .
PYTHONPATH=src python3 -m codex_orchestrator.cli usage --scope project --project-root . --task "Review the failing auth flow"
PYTHONPATH=src python3 -m codex_orchestrator.cli template init --project-root . --category custom-ops --agent custom-coordinator
```

## Catalog Model

- 앱은 소수의 app-owned built-in catalog를 포함한다
- `awesome-codex-subagents` 전체를 제품 안에 vendoring하지 않는다
- project-local injection 경로는 `.codex/orchestrator/catalog/categories/`이다
- global injection 경로는 `~/.codex/orchestrator/catalog/categories/`이다
- `--catalog-root <path>`로 awesome 스타일 `categories/` 트리를 직접 주입할 수 있다
- `catalog import`로 선택한 category 또는 agent를 이 injection 경로에 영구 반영할 수 있다
- 사용자가 직접 만든 템플릿도 같은 폴더 형식을 따르면 같은 install 흐름에 참여할 수 있다

같은 agent key가 충돌하면 precedence는 다음 순서다.

- `project`
- `global`
- `built-in`

## Template Scaffolding

project-local injection 경로에 새 category와 agent template를 만든다.

```bash
codex-orchestrator template init \
  --project-root . \
  --category custom-ops \
  --agent custom-coordinator
```

외부 `categories/` 트리에 직접 생성할 수도 있다.

```bash
codex-orchestrator template init \
  --catalog-root /path/to/categories \
  --category custom-ops \
  --agent custom-coordinator \
  --orchestrator
```

외부 템플릿을 project-local injection 경로로 영구 가져올 수도 있다.

```bash
codex-orchestrator catalog import \
  --scope project \
  --project-root . \
  --catalog-root /path/to/categories \
  --agents custom-helper,custom-reviewer
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
codex-orchestrator install --scope project --agents cto-coordinator,reviewer --validate
codex-orchestrator doctor --scope project --project-root .
```

## Usage Helper

`usage`는 현재 scope에서 실제로 보이는 installed agent를 기준으로 Codex에 바로 붙여 넣을 starter prompt를 만들어준다.

```bash
codex-orchestrator usage \
  --scope project \
  --project-root . \
  --task "Review the failing auth flow"
```

## Experimental Commands

현재 저장소에는 control-plane 성격의 명령도 들어 있다. 다만 이 기능들은 실험 기능으로 유지하며, 제품의 기본 정체성으로 보지 않는다. 이후 더 공격적으로 바뀔 수 있다.

experimental 명령:

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

이 명령들은 Codex를 대체하는 독립 multi-agent runtime이라기보다, Codex 사용 주변에 붙는 session-companion 또는 prototype layer로 이해하는 편이 맞다.

현재 experimental 경계는 [docs/EXPERIMENTAL.ko.md](./docs/EXPERIMENTAL.ko.md)에 따로 정리돼 있다.

## 개발용 설치 / 제거

개발용으로는 repo-local editable install을 사용하면 된다.

```bash
./scripts/install.sh
codex-orchestrator --help
./scripts/uninstall.sh
```

기본 동작:

- `install.sh`는 repo 루트에 `.venv/`를 만들고 `pip install -e .`를 수행한다
- 기본적으로 `~/.local/bin/codex-orchestrator` symlink 생성을 시도한다
- `~/.local/bin`이 `PATH`에 없으면 `source .venv/bin/activate` 또는 `.venv/bin/codex-orchestrator`로 실행하면 된다
- `install.sh --dry-run`, `install.sh --no-link`, `uninstall.sh --keep-venv` 같은 옵션이 있다

## 테스트 / 검증

기본 자동 검증 명령:

```bash
./scripts/test.sh
```

개별 명령으로 실행하려면:

```bash
python3 -m compileall src
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

`curses` 기반 TUI를 수정했다면 자동 테스트 외에 PTY 수동 smoke도 함께 유지한다.

## 참고

- 제품 방향: [docs/PRD.ko.md](./docs/PRD.ko.md)
- 제품 이해 / workflow: [docs/UNDERSTANDING_AND_WORKFLOW.ko.md](./docs/UNDERSTANDING_AND_WORKFLOW.ko.md)
- 테스트 workflow: [docs/TESTING.ko.md](./docs/TESTING.ko.md)
- experimental 경계: [docs/EXPERIMENTAL.ko.md](./docs/EXPERIMENTAL.ko.md)
