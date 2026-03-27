# codex-subagent-kit

`codex-subagent-kit` is the TypeScript CLI package for installing and managing Codex subagent definitions, catalogs, and templates.

The current TypeScript package covers the stable command surface:

- `catalog`
- `catalog sync`
- `catalog import`
- `template init`
- `install`
- `doctor`
- `usage`
- `tui`
- bare command entrypoint for the install-first interactive flow

The TypeScript package is the active npm-targeted implementation. The Python app remains in the repository as a legacy implementation, a fallback development path, and the home for experimental commands that are outside the npm-first surface.

## Quick Start

From the repository root:

```bash
npm install
npm run build:ts
node packages/codex-subagent-kit/dist/cli.js
```

That bare command opens the install-first TUI.

If you want one quick non-interactive check:

```bash
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --agents reviewer,code-mapper \
  --validate
node packages/codex-subagent-kit/dist/cli.js usage \
  --scope project \
  --project-root /tmp/codex-subagent-kit-demo \
  --task "Review the failing auth flow"
```

## Local Development

From the repository root:

```bash
npm install
npm run test:ts
npm run typecheck:ts
npm run build:ts
npm run smoke:ts:consumer
node packages/codex-subagent-kit/dist/cli.js --help
node packages/codex-subagent-kit/dist/cli.js
```

## Stable Commands

Browse the VoltAgent-backed built-in snapshot and any injected catalogs:

```bash
node packages/codex-subagent-kit/dist/cli.js catalog
```

Refresh a project-local synced source root from a local clone or from VoltAgent upstream:

```bash
node packages/codex-subagent-kit/dist/cli.js catalog sync --scope project --project-root /tmp/example --source-root /tmp/awesome-codex-subagents
node packages/codex-subagent-kit/dist/cli.js catalog sync --scope project --project-root /tmp/example
```

Import external awesome-style `categories/` content into the project catalog:

```bash
node packages/codex-subagent-kit/dist/cli.js catalog import \
  --scope project \
  --project-root /tmp/example \
  --catalog-root /tmp/categories \
  --agents custom-helper
```

Install project-scoped agents and validate them immediately:

```bash
node packages/codex-subagent-kit/dist/cli.js install \
  --scope project \
  --project-root /tmp/example \
  --agents reviewer,code-mapper \
  --validate
```

Use `doctor` if you want to re-check the generated files later:

```bash
node packages/codex-subagent-kit/dist/cli.js doctor --scope project --project-root /tmp/example
```

Render a Codex starter prompt from the installed agents:

```bash
node packages/codex-subagent-kit/dist/cli.js usage \
  --scope project \
  --project-root /tmp/example \
  --task "Review the failing auth flow"
```

Common Codex-side prompts:

- `Use reviewer to review the current changes for bugs, regressions, and missing tests.`
- `Use code-mapper to map the auth flow before we change it.`
- `Use multi-agent-coordinator to coordinate reviewer and code-mapper for this task.`

If the selected install set includes a `meta-orchestration` agent such as `multi-agent-coordinator`, the project install also seeds the optional experimental scaffold under `.codex/subagent-kit/`.

## Packaging

The repository includes a dry-run packaging command:

```bash
npm run pack:ts
npm run smoke:ts:consumer
```

See the repository-level TypeScript migration notes in `docs/TYPESCRIPT_PORT.md` for current parity status and release readiness.
