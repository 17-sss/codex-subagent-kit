# TYPESCRIPT PORT

Korean version: [TYPESCRIPT_PORT.ko.md](./TYPESCRIPT_PORT.ko.md)

## Goal

The TypeScript port is intended to produce an npm-publishable CLI that preserves the stable product core of `codex-subagent-kit`.

The port is not a product reset. It is a language and packaging migration built on top of the already-stabilized Python behavior.

## Current Workspace Bootstrap

The repository now includes a dedicated TypeScript workspace under [`packages/codex-subagent-kit/`](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/packages/codex-subagent-kit).

That package is intentionally a bootstrap, not a parity-complete replacement. It provides the npm package shape and CLI entrypoint that the rest of the port can build on.

Current implemented slice:

- shared path helpers
- catalog data model
- built-in catalog assets inside the TypeScript workspace
- working `catalog` command
- working `catalog import` command
- working `template init` command
- working `install` command
- working `doctor` command
- working `install --validate` flow
- working `usage` command

Current bootstrap validation commands:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js --help
```

## Stable Scope To Port First

The first TypeScript release should cover only the stable CLI surface:

- bare command entrypoint that opens the install-first TUI
- `catalog`
- `catalog import`
- `install`
- `doctor`
- `usage`
- `template init`
- TUI install flow

## Out Of Scope For The First Port

Do not port the experimental companion layer in the first TypeScript pass:

- `panel`
- `board`
- `launch`
- `enqueue`
- `dispatch-open`
- `dispatch-prepare`
- `dispatch-begin`
- `apply-result`

These commands can remain Python-only or be revisited after the stable npm package exists.

## Parity Contract

The TypeScript CLI should preserve the user-facing behavior of the Python stable core.

Priority parity targets:

- generated `.codex/agents/*.toml` format
- catalog precedence rules
- template scaffold output
- `doctor` success and failure reporting
- `usage` output structure
- exit-code behavior for stable commands

Use the current Python implementation as the reference contract, especially:

- golden fixtures under [tests/fixtures/golden](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/tests/fixtures/golden)
- CLI behavior locked in [tests/test_cli.py](/Users/hoyoungson/Code/Project/Personal/codex-orchestrator/tests/test_cli.py)

## Recommended Stack

Use a Node CLI stack rather than a browser-oriented build tool.

Recommended baseline:

- TypeScript
- Node.js CLI runtime
- `commander` for command parsing
- `ink` or `blessed` for the TUI layer
- `@iarna/toml` or an equivalent TOML library for round-trippable parsing and writing
- `tsup` for packaging and publishing builds

Avoid `Vite` for the core CLI package. It is not the natural fit for a filesystem-heavy terminal tool.

## Suggested Delivery Order

1. create a dedicated TypeScript package workspace
2. implement shared data model and filesystem path helpers
3. port catalog loading and TOML rendering
4. port `template init`
5. port `install`
6. port `doctor`
7. port `usage`
8. port the install-first TUI
9. add fixture-based parity tests against the Python contract
10. prepare npm metadata and publishing workflow

## Release Readiness For The TypeScript Port

Before the npm package is published, confirm:

- stable commands match Python behavior closely enough for docs and examples
- generated TOML is accepted by Codex
- package name, README, and examples are aligned with npm usage
- the TypeScript package has its own CI and release path

## Current Decision

The repository should continue to treat Python as the source of truth until the first TypeScript CLI reaches stable-core parity.
