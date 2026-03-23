# RELEASING

영문 기본 문서: [RELEASING.md](./RELEASING.md)

`codex-orchestrator`는 `main` 브랜치 전용 GitHub Actions workflow로 시멘틱 버전 태그와 GitHub Release를 만든다.

## 트리거

- `main`에 대한 `push`
- 수동 `workflow_dispatch`

## 태그 형식

- `0.1.0`
- `0.1.1`
- `0.2.0`

이 workflow는 `v` prefix 없는 plain semver tag를 사용한다.

## 버전 증가 규칙

- `major`
  - 커밋 메시지에 `BREAKING CHANGE:`가 포함된 경우
  - conventional commit subject에 `!`가 있는 경우. 예: `feat!: ...`
- `minor`
  - major 조건이 없고 `feat: ...` 커밋이 있는 경우
- `patch`
  - 그 외 모든 경우

## 초기 릴리즈

아직 semver tag가 하나도 없다면, workflow는 [pyproject.toml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/pyproject.toml)의 현재 `[project].version`을 초기 기준 버전으로 사용한다.

즉 지금 기준으로는 package version을 바꾸지 않는 한 첫 자동 태그는 `0.1.0`부터 시작한다.

## 중복 방지

현재 커밋에 이미 semver tag가 붙어 있으면, workflow는 그 버전을 재사용하고 중복 tag 생성을 건너뛴다.

## 구현 참고

- workflow 파일: [release-semver.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/release-semver.yml)
- 테스트되는 semver helper: [release_versioning.py](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/src/codex_orchestrator/release_versioning.py)
