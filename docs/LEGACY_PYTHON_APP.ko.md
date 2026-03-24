# LEGACY PYTHON APP

영문 기본 문서: [LEGACY_PYTHON_APP.md](./LEGACY_PYTHON_APP.md)

이 저장소는 원래의 Python 구현을 [`src/codex_subagent_kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/src/codex_subagent_kit) 아래에 legacy app으로 계속 보존한다.

## 여기서 Legacy의 의미

- Python 앱은 여전히 이 저장소 안에서 사용할 수 있다
- fallback 개발 경로로 계속 유효하다
- 첫 npm package에 포함되지 않은 experimental 명령을 계속 담고 있다
- 더 이상 npm release의 주된 대상은 아니다

## 진입점

repo 루트에서 직접 모듈 실행:

```bash
PYTHONPATH=src python3 -m codex_subagent_kit.cli --help
```

editable-install legacy 명령:

```bash
./scripts/install.sh
codex-subagent-kit-legacy --help
```

## 현재 Legacy Surface

Python 앱에는 아직 아래가 남아 있다.

- 원래의 curses 기반 TUI
- experimental control-plane 명령
- 원래의 Python 테스트 스위트와 fixture contract

이 영역은 계속 다음 용도로 유효하다.

- 마이그레이션 중 reference implementation
- 이미 Python workflow를 쓰고 있는 기여자의 fallback 도구
- npm package로 아직 옮기지 않은 experimental 명령의 보관소

## TypeScript Package와의 관계

- [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit) 아래의 TypeScript package가 현재 npm release target이다
- Python 앱은 저장소 안에 legacy implementation으로 남겨둔다
- 이제 Python 제거 여부는 즉시 해야 하는 마이그레이션 작업이 아니라 제품 판단의 영역이다
