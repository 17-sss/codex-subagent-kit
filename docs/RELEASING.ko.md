# RELEASING

영문 기본 문서: [RELEASING.md](./RELEASING.md)

`codex-subagent-kit`는 `main` 브랜치 전용 GitHub Actions workflow로 시멘틱 버전 태그와 GitHub Release를 만들고, TypeScript package용 npm publish workflow도 별도로 가진다.

## 트리거

- `main`에 대한 `push`
- 수동 `workflow_dispatch`

권장 흐름은 다음과 같다.

1. `main` 대상 PR 생성
2. PR CI에서 TypeScript repository gate 확인
3. `main`으로 merge
4. release workflow가 workspace version file을 먼저 `main`에 sync
5. sync된 commit 기준으로 tag와 GitHub Release 생성
6. npm publish workflow가 같은 버전의 `codex-subagent-kit` package를 publish

## 태그 형식

- `0.1.0`
- `0.2.0`
- `0.2.1`
- `0.3.0`

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

아직 semver tag가 하나도 없다면, workflow는 [packages/codex-subagent-kit/package.json](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/package.json)의 현재 package version을 초기 기준 버전으로 사용한다.

현재 저장소는 `0.2.1`을 눈에 보이는 package 기준선으로 유지한다.

이제 release workflow가 새 릴리즈를 만들 때 [packages/codex-subagent-kit/package.json](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/package.json)과 [package-lock.json](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/package-lock.json)을 먼저 `main`에 sync한 뒤 tag를 생성한다. 즉 merge 이후에는 저장소에 보이는 버전, git tag, GitHub Release, npm package version이 자동으로 같은 릴리즈 기준으로 맞춰진다.

## 중복 방지

현재 커밋에 이미 semver tag가 붙어 있으면, workflow는 그 버전을 재사용하고 중복 tag 생성을 건너뛴다.

자동 version sync commit에는 `[skip release]` marker를 넣어 release workflow가 자기 자신을 다시 트리거하지 않도록 한다.

나중에 branch protection을 다시 강하게 걸 경우에는 release workflow가 자동 version sync commit을 `main`에 push할 수 있도록 허용해야 한다.

## npm Publish 흐름

- workflow 파일: [publish-npm.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/publish-npm.yml)
- 트리거: published GitHub Release
- 인증 방식: GitHub Actions OIDC 기반 npm trusted publishing
- 필요한 permission: npm provenance와 trusted publishing을 위한 `id-token: write`

첫 publish 전에 npm package 설정에서 이 저장소와 workflow에 대한 trusted publishing을 먼저 연결해야 한다.

npm workflow는 release tag가 plain semver인지 확인하고, publish 시점에 workspace package version을 그 tag와 맞춘 뒤 `./scripts/test.sh`를 실행하고 다음 명령으로 publish를 수행한다.

- `npm publish --workspace codex-subagent-kit --access public --provenance`

## 구현 참고

- workflow 파일: [release-semver.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/release-semver.yml)
- 테스트되는 semver helper: [release-versioning.ts](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/src/release-versioning.ts)
