# EXPERIMENTAL

영문 기본 문서: [EXPERIMENTAL.md](./EXPERIMENTAL.md)

이 문서는 현재 저장소 안에 존재하지만 stable product core가 아닌 experimental companion 기능을 정리한다.

## 왜 분리했는가

현재 `codex-orchestrator`의 stable 정체성은 다음이다.

- catalog 관리
- TOML 설치
- template scaffolding
- install-first TUI 흐름
- `doctor`를 통한 validation

제품 방향을 다듬는 과정에서 몇 가지 인접 기능도 함께 실험했다. 나중에 다시 유용할 수는 있지만, 지금 이 도구의 기본 약속은 아니다.

## 현재 Experimental Commands

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

## 어떻게 이해하면 되는가

이 기능들은 `Codex session companion` 또는 prototype layer로 이해하는 편이 맞다.

- Codex 사용 주변의 워크플로를 살펴보거나 흉내 내는 데 도움을 줄 수 있다
- agent thread의 runtime owner로서 Codex를 대체하지 않는다
- stable core보다 더 공격적으로 바뀌어도 되는 영역이다

## 아직 약속하지 않는 것

- Codex 바깥의 standalone orchestration runtime
- live `spawn_agent` / `send_input` / `wait_agent` integration
- production-grade queue draining / dispatch automation
- live pane / session synchronization

## 나중에 다시 이어간다면

가장 자연스러운 순서는 다음과 같다.

1. session companion에 대한 사용자 스토리를 다시 명확히 한다
2. 이 기능을 optional로 둘지 first-class로 올릴지 결정한다
3. 현재 Codex-native runtime 모델과 맞는 범위에서만 다시 연결한다
