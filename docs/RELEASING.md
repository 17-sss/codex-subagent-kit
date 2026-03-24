# RELEASING

Korean version: [RELEASING.ko.md](./RELEASING.ko.md)

`codex-subagent-kit` uses a `main`-only GitHub Actions workflow to create semantic-version tags and GitHub Releases.

## Trigger

- `push` to `main`
- manual `workflow_dispatch`

The intended sequence is:

1. open a PR targeting `main`
2. let the PR CI workflow run both the Python and TypeScript package gates
3. merge to `main`
4. let the release workflow create the tag and GitHub Release

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

If no semver tag exists yet, the workflow uses the current `[project].version` from [pyproject.toml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/pyproject.toml) as the base release version.

That means the first automatic tag from this repository will start from `0.1.0` unless the package version is changed first.

## Duplicate Protection

If the current commit already has a semver tag, the workflow reuses that version and skips creating a duplicate tag.

## Implementation Notes

- workflow file: [release-semver.yml](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/.github/workflows/release-semver.yml)
- tested semver helper: [release_versioning.py](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/src/codex_subagent_kit/release_versioning.py)
