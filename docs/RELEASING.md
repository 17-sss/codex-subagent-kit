# RELEASING

Korean version: [RELEASING.ko.md](./RELEASING.ko.md)

`codex-subagent-kit` uses a `main`-only GitHub Actions workflow to compute the next semantic version, sync repository version files, run the repository gate, create a semver tag, and create a GitHub Release.

The repository also includes a dedicated npm publish workflow that runs automatically when that semver tag is pushed, and it can be dispatched manually for recovery.

## Trigger

- `push` to `main`
- manual `workflow_dispatch`

The intended sequence is:

1. open a PR targeting `main`
2. let the PR CI workflow run the TypeScript repository gate
3. merge to `main`
4. let the release workflow sync the workspace version files into `main`
5. let the release workflow create the tag and GitHub Release from that synced commit
6. let the tag-triggered publish workflow publish the matching `codex-subagent-kit` package version

## Tag Format

- `0.1.0`
- `0.2.0`
- `0.2.1`
- `0.3.0`

The workflow uses plain semver tags without a `v` prefix.

## Bump Rules

Release bumping is PR-label-based.

- `release:major`
  - bump to the next major version
- `release:minor`
  - bump to the next minor version
- `release:patch`
  - bump to the next patch version
- `release:none`
  - skip tag / GitHub Release / npm publish for that merge
- no release label
  - skips release automation

Direct pushes to `main` also skip release automation. A release only happens when the `main` push can be traced back to a merged PR that has exactly one supported release label.

If multiple release labels are present on the merged PR, the release workflow fails so maintainers can correct the PR metadata.

The repository-managed source of truth for those labels lives in [.github/labels.yml](../.github/labels.yml), and [create-labels.yml](../.github/workflows/create-labels.yml) can sync them into GitHub.

## Initial Release

If no semver tag exists yet, the workflow uses the current package version from [packages/codex-subagent-kit/package.json](../packages/codex-subagent-kit/package.json) as the first release version.

The repository currently keeps `0.2.0` as the visible package baseline.

On each new release, the release workflow now syncs [packages/codex-subagent-kit/package.json](../packages/codex-subagent-kit/package.json) and [package-lock.json](../package-lock.json) back into `main` before tagging. That means the repository-visible version, git tag, GitHub Release, and npm package version stay aligned automatically after merge.

## Duplicate Protection

If the current commit already has a semver tag, the workflow reuses that version and skips creating a duplicate tag.

The automated version sync commit uses a `[skip release]` marker so the release workflow does not loop on itself.

If branch protection is enabled later, make sure the release workflow can still push its automated version-sync commit back to `main`.

## npm Publish Flow

- release workflow file: [release-semver.yml](../.github/workflows/release-semver.yml)
- release trigger: `push` to `main`
- publish workflow file: [publish-npm.yml](../.github/workflows/publish-npm.yml)
- publish trigger: semver tag `push` or manual `workflow_dispatch`
- authentication model: npm trusted publishing via GitHub Actions OIDC
- required permissions: `id-token: write` on `publish-npm.yml` for npm provenance and trusted publishing

## Label Management

- labels config: [.github/labels.yml](../.github/labels.yml)
- sync workflow: [create-labels.yml](../.github/workflows/create-labels.yml)
- trigger: manual dispatch or pushes that change `.github/labels.yml`

Before the first publish, configure npm trusted publishing for this repository and `publish-npm.yml` in the npm package settings.

Trusted publishing on GitHub Actions should run on Node 22 with npm 11.5.1 or newer. The workflows in this repository explicitly upgrade npm before publishing.

The release workflow syncs the workspace package version to the computed release version, runs `./scripts/test.sh`, then creates the tag and GitHub Release.

The publish workflow checks out the matching tag, keeps the workspace package version aligned with that tag when needed, and publishes with:

- `npm publish --workspace codex-subagent-kit --access public --provenance`

The publish workflow skips safely if npm already has that exact version.

If tag creation and GitHub Release succeed but npm needs to be retried manually, use the recovery workflow:

- workflow file: [publish-npm.yml](../.github/workflows/publish-npm.yml)
- trigger: semver tag `push` or `workflow_dispatch`
- required input: `release_tag`

The recovery workflow tolerates tags whose checked-out package version already matches the requested `release_tag`.

If npm already has a version but the git tag or GitHub Release is missing, sync the workspace version into `main` first if needed and then run `Backfill GitHub Release (Manual)`.

## Implementation Notes

- release workflow file: [release-semver.yml](../.github/workflows/release-semver.yml)
- publish workflow file: [publish-npm.yml](../.github/workflows/publish-npm.yml)
- tested release-label helper: [release-versioning.ts](../packages/codex-subagent-kit/src/release-versioning.ts)
