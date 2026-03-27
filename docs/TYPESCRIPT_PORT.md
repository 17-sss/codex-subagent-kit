# TYPESCRIPT PORT

Korean version: [TYPESCRIPT_PORT.ko.md](./TYPESCRIPT_PORT.ko.md)

## Goal

The TypeScript migration is complete for the stable product surface. `codex-subagent-kit` now ships as an npm-oriented CLI built from the workspace under [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit).

## Current TypeScript Status

The TypeScript package is the product source of truth and npm release target.

Current implemented slice:

- shared path helpers
- catalog data model
- vendored VoltAgent catalog snapshot inside the TypeScript workspace
- working `catalog` command
- working `catalog sync` command
- working `catalog import` command
- working `template init` command
- working `install` command
- working `doctor` command
- working `install --validate` flow
- working `usage` command
- working prompt-driven install-first `tui`
- working bare command entrypoint that opens the interactive install flow
- shared fixture-based parity tests for generated TOML, `usage`, and `doctor`

Current validation commands:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run pack:ts
node packages/codex-subagent-kit/dist/cli.js --help
node packages/codex-subagent-kit/dist/cli.js
```

The stable CLI surface now includes:

- bare command entrypoint that opens the install-first TUI
- `catalog`
- `catalog sync`
- `catalog import`
- `install`
- `doctor`
- `usage`
- `template init`
- TUI install flow

## Contract

The TypeScript CLI preserves the stable user-facing behavior that was originally defined during the migration.

Priority parity targets:

- generated `.codex/agents/*.toml` format
- catalog precedence rules
- template scaffold output
- `doctor` success and failure reporting
- `usage` output structure
- exit-code behavior for stable commands

Use the package-local fixtures as the release contract:

- golden fixtures under [packages/codex-subagent-kit/test/fixtures/golden](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/test/fixtures/golden)
- TypeScript CLI behavior locked in [packages/codex-subagent-kit/test](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit/test)

## Recommended Stack

Use a Node CLI stack rather than a browser-oriented build tool.

Recommended baseline:

- TypeScript
- Node.js CLI runtime
- `commander` for command parsing
- `@inquirer/prompts` for the first interactive TUI pass
- `@iarna/toml` or an equivalent TOML library for round-trippable parsing and writing
- `tsup` for packaging and publishing builds

Avoid `Vite` for the core CLI package. It is not the natural fit for a filesystem-heavy terminal tool.

## Release Readiness

Before the npm package is published, confirm:

- generated TOML is accepted by Codex
- package name, README, and examples are aligned with npm usage
- `npm pack --dry-run` produces the expected package contents
- the TypeScript package has its own CI and release path

The repository now includes:

- PR CI for the TypeScript package
- a release semver workflow
- an npm publish workflow triggered from published GitHub releases
