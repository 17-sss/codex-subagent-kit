# RELEASING

Korean version: [RELEASING.ko.md](./RELEASING.ko.md)

`codex-subagent-kit` uses a `main`-only GitHub Actions workflow to create semantic-version tags and GitHub Releases.

The repository also includes a dedicated npm publish workflow for the TypeScript package.

## Trigger

- `push` to `main`
- manual `workflow_dispatch`

The intended sequence is:

1. open a PR targeting `main`
2. let the PR CI workflow run the TypeScript repository gate
3. merge to `main`
4. let the release workflow sync the workspace version files into `main`
5. let the release workflow create the tag and GitHub Release from that synced commit
6. let the npm publish workflow publish the matching `codex-subagent-kit` package version

## Tag Format

- `0.1.0`
- `0.2.0`
- `0.2.1`
- `0.3.0`

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

The repository currently keeps `0.2.0` as the visible package baseline.

On each new release, the release workflow now syncs [packages/codex-subagent-kit/package.json](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/package.json) and [package-lock.json](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/package-lock.json) back into `main` before tagging. That means the repository-visible version, git tag, GitHub Release, and npm package version stay aligned automatically after merge.

## Duplicate Protection

If the current commit already has a semver tag, the workflow reuses that version and skips creating a duplicate tag.

The automated version sync commit uses a `[skip release]` marker so the release workflow does not loop on itself.

If branch protection is enabled later, make sure the release workflow can still push its automated version-sync commit back to `main`.

## npm Publish Flow

- workflow file: [publish-npm.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/publish-npm.yml)
- trigger: published GitHub Release
- authentication model: npm trusted publishing via GitHub Actions OIDC
- required permissions: `id-token: write` for npm provenance and trusted publishing

Before the first publish, configure npm trusted publishing for this repository and workflow in the npm package settings.

The npm workflow validates that the release tag is plain semver, syncs the workspace package version to that tag at publish time, runs `./scripts/test.sh`, and then publishes with:

- `npm publish --workspace codex-subagent-kit --access public --provenance`

## Implementation Notes

- workflow file: [release-semver.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/release-semver.yml)
- tested semver helper: [release-versioning.ts](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/src/release-versioning.ts)
