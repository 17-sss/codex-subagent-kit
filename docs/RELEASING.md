# RELEASING

Korean version: [RELEASING.ko.md](./RELEASING.ko.md)

`codex-subagent-kit` uses a `main`-only GitHub Actions workflow to create semantic-version tags and GitHub Releases.

The repository also includes a dedicated npm publish workflow for the TypeScript package.

## Trigger

- `push` to `main`
- manual `workflow_dispatch`

The intended sequence is:

1. open a PR targeting `main`
2. let the PR CI workflow run both the Python and TypeScript package gates
3. merge to `main`
4. let the release workflow create the tag and GitHub Release
5. let the npm publish workflow publish the matching `codex-subagent-kit` package version

## Tag Format

- `0.1.0`
- `0.1.1`
- `0.2.0`

The workflow uses plain semver tags without a `v` prefix.

## Bump Rules

- `major`
  - any commit containing `BREAKING CHANGE:`
  - any conventional-commit subject using `!`, for example `feat!: ...`
- `minor`
  - any `feat: ...` commit when no major bump is present
- `patch`
  - everything else

## Initial Release

If no semver tag exists yet, the workflow uses the current package version from [packages/codex-subagent-kit/package.json](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/package.json) as the base release version.

That means the first automatic tag from this repository will start from `0.1.0` unless the TypeScript package version is changed first.

## Duplicate Protection

If the current commit already has a semver tag, the workflow reuses that version and skips creating a duplicate tag.

## npm Publish Flow

- workflow file: [publish-npm.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/publish-npm.yml)
- trigger: published GitHub Release
- required secret: `NPM_TOKEN`
- required permissions: `id-token: write` for npm provenance

The npm workflow validates that the release tag is plain semver, syncs the workspace package version to that tag at publish time, and then runs:

- `npm run test:ts`
- `npm run typecheck:ts`
- `npm run build:ts`
- `npm run pack:ts`
- `npm publish --workspace codex-subagent-kit --access public --provenance`

## Implementation Notes

- workflow file: [release-semver.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/release-semver.yml)
- tested semver helper: [release-versioning.ts](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/src/release-versioning.ts)
