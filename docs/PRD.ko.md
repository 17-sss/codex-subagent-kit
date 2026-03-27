# PRD: codex-subagent-kit

영문 기본 문서: [PRD.md](./PRD.md)

## 목적

`codex-subagent-kit`는 프로젝트 로컬 또는 글로벌 `.codex` 디렉터리 아래에 Codex subagent 정의를 설치하고 관리하는 Codex-native 툴킷이다.

이 제품은 의도적으로 “준비”에 집중한다.

- `codex-subagent-kit`는 catalog를 정리하고, template를 scaffold하고, agent TOML을 설치한다
- 실제 agent thread의 spawn, 라우팅, 관리는 `codex`가 맡는다

## Stable Product Core

현재 stable한 제품 정체성은 다음 흐름이다.

1. 설치 대상을 고른다
   - `Project`
   - `Global`
2. built-in 또는 injected catalog를 본다
   - vendored VoltAgent snapshot
   - synced source root
   - user-authored injection root
3. subagent를 고른다
4. 호환되는 `.codex/agents/*.toml`을 생성한다
5. 그 작업공간에서 `codex`를 실행한다

stable capability:

- curses 기반 install-first TUI
- 비대화형 install CLI
- `doctor` validation CLI
- VoltAgent 기반 built-in catalog snapshot
- project/global synced source-root discovery 및 refresh
- project/global discovery와 precedence
- awesome 스타일 외부 catalog injection
- project/global catalog injection 경로로의 persistent import
- project/global template scaffolding
- `developer_instructions`를 사용하는 Codex-compatible TOML output
- 선택한 install 조합에 meta-orchestration agent가 있을 때만 optional experimental scaffold 생성

## Session Companion Layer

저장소 안에는 Codex 사용 주변을 돕는 얇은 session-companion 레이어가 포함될 수 있다. 이 레이어는 설치된 자산을 살펴보거나 레이아웃을 미리 보거나 세션 보조 기능을 실험하는 데 도움을 줄 수 있지만, 제품을 외부 런타임으로 재정의하지는 않는다.

예:

- read-only topology 렌더링
- launcher prototype
- queue / dispatch 실험

## Experimental Boundary

다음 영역은 명시적으로 experimental로 둔다.

- panel 렌더링
- board 렌더링
- launcher 실행
- queue / dispatch / result lifecycle helper

이 기능들은 유용할 수는 있지만 제품의 주된 가치 제안으로 보지 않는다.

## 제품 원칙

- Codex-native first
- local over global
- runtime 추상화보다 static definition 우선
- VoltAgent를 기본값으로 쓰되 VoltAgent lock-in은 피하기
- 명시적이고 검토 가능한 TOML template
- 회사/제품 고유의 기본 자산은 포함하지 않음

## 현재 비목표

- Codex를 대체하는 runtime owner 만들기
- Codex 바깥의 standalone multi-agent broker 구축
- 사용자를 단일 서드파티 catalog repo에만 묶어두기

## 단기 우선순위

- install / catalog / template workflow 강화
- vendored VoltAgent snapshot과 `catalog sync` 흐름 최신성 유지
- 생성된 TOML에 대한 compatibility check와 validation 보강
- 사용자 작성 catalog의 import / extension 경로 개선
- 설치된 agent를 Codex 세션 안에서 어떻게 쓰는지 문서화 강화
- stable core만 대상으로 하는 TypeScript/npm 포팅 계획 정리
- Python 앱을 legacy implementation 및 experimental track으로 남겨두면서 TypeScript 패키지가 stable command scope와 어긋나지 않게 관리
